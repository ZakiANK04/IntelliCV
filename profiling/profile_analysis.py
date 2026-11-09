"""Time one IntelliCV analysis end to end, step by step, in a fresh process.

Run from the repo root with the project venv:

    .venv/Scripts/python profiling/profile_analysis.py --warm-passes 5 > out.json

Renders the 7 sample CVs in tests/test_data/sample_cvs.py to PDF (the recipe in
docs/running-and-testing.md), then drives the real Flask routes through the test client:
POST /api/submit-user, then POST /api/upload-cv. Every pipeline step is wrapped with a
timer, so the numbers are the production code paths, not a re-implementation.

"cold" is the first upload in a fresh process. "warm" is every later upload.
"""
import argparse
import json
import os
import statistics
import sys
import tempfile
import time

T_SCRIPT = time.perf_counter()

import psutil  # noqa: E402

PROC = psutil.Process()
# Interpreter start to the first line of this script.
INTERP_START_S = time.time() - PROC.create_time()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

TMP = tempfile.mkdtemp(prefix="intellicv-prof-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(TMP, "prof.db").replace("\\", "/")
os.environ["UPLOAD_FOLDER"] = os.path.join(TMP, "uploads")
os.environ["FLASK_CONFIG"] = "production"


def rss_mb():
    return PROC.memory_info().rss / 2**20


timings = {}  # step name -> list of ms for the current request
startup = {}
memory = {"after_interpreter_mb": rss_mb()}


def timed(name, fn):
    def wrapper(*a, **kw):
        t = time.perf_counter()
        try:
            return fn(*a, **kw)
        finally:
            timings.setdefault(name, []).append((time.perf_counter() - t) * 1000)
    return wrapper


# --- startup: spaCy import and model load, measured separately from the app factory ---
t = time.perf_counter()
import spacy  # noqa: E402
startup["import_spacy_ms"] = (time.perf_counter() - t) * 1000
memory["after_import_spacy_mb"] = rss_mb()

_spacy_load = spacy.load


def _timed_spacy_load(*a, **kw):
    t = time.perf_counter()
    m0 = rss_mb()
    nlp = _spacy_load(*a, **kw)
    startup["spacy_load_ms"] = (time.perf_counter() - t) * 1000
    memory["spacy_model_delta_mb"] = rss_mb() - m0
    return nlp


spacy.load = _timed_spacy_load

t = time.perf_counter()
from app import create_app, db  # noqa: E402
startup["import_app_ms"] = (time.perf_counter() - t) * 1000

t = time.perf_counter()
app = create_app()  # registers blueprints -> imports nlp_analyzer singleton -> spacy.load
startup["create_app_total_ms"] = (time.perf_counter() - t) * 1000
startup["create_app_excl_spacy_load_ms"] = startup["create_app_total_ms"] - startup.get("spacy_load_ms", 0)
startup["interpreter_start_ms"] = INTERP_START_S * 1000  # process creation to line 1 of this script
startup["script_to_ready_ms"] = (time.perf_counter() - T_SCRIPT) * 1000
memory["after_app_ready_mb"] = rss_mb()

# --- wrap every pipeline step ---
from app.services import cv_analyzer as cva  # noqa: E402
from app.services.pdf_extractor import pdf_extractor as px  # noqa: E402
from app.services.nlp_analyzer import nlp_analyzer as na  # noqa: E402

px.validate_pdf = timed("validate_pdf", px.validate_pdf)
px._extract_with_pdfplumber = timed("extract_pdfplumber", px._extract_with_pdfplumber)
px._extract_with_pymupdf = timed("extract_pymupdf_fallback", px._extract_with_pymupdf)
px._clean_and_normalize = timed("clean_and_normalize", px._clean_and_normalize)
px.extract_text = timed("extract_text_total", px.extract_text)

NLP_STEPS = [
    "_detect_sections", "_extract_skills", "_extract_entities", "_detect_career_field",
    "_detect_experience_level", "_calculate_scores", "_identify_strengths",
    "_identify_weaknesses", "_generate_recommendations", "_generate_youtube_suggestions",
]
for s in NLP_STEPS:
    setattr(na, s, timed("nlp" + s, getattr(na, s)))
na.analyze = timed("nlp_analyze_total", na.analyze)

# FileStorage.save on the uploaded file
from werkzeug.datastructures import FileStorage  # noqa: E402
FileStorage.save = timed("save_upload", FileStorage.save)

_orig_commit = db.session.commit


def _commit(*a, **kw):
    t = time.perf_counter()
    try:
        return _orig_commit(*a, **kw)
    finally:
        timings.setdefault("db_commit", []).append((time.perf_counter() - t) * 1000)


cva.db.session.commit = _commit
cva.cv_analyzer_service.process_cv = timed("process_cv_total", cva.cv_analyzer_service.process_cv)


# --- render the samples to PDF (not timed) ---
def render_pdfs():
    import pymupdf
    from tests.test_data.sample_cvs import ALL_SAMPLE_CVS
    out = {}
    for name, cv in ALL_SAMPLE_CVS.items():
        lines = cv["text"].strip().split("\n")
        doc = pymupdf.open()
        for i in range(0, len(lines), 60):
            doc.new_page().insert_text((50, 50), "\n".join(lines[i:i + 60]), fontsize=9)
        path = os.path.join(TMP, name + ".pdf")
        doc.save(path)
        out[name] = {"path": path, "pages": doc.page_count, "bytes": os.path.getsize(path),
                     "chars": len(cv["text"])}
    return out


def upload(client, name, path):
    timings.clear()
    r = client.post("/api/submit-user", json={"full_name": "Prof User", "email": "p@example.com",
                                              "phone": "0555000111"})
    uid = r.get_json()["user_id"]
    with open(path, "rb") as f:
        t = time.perf_counter()
        r = client.post("/api/upload-cv", data={"user_id": str(uid), "cv_file": (f, name + ".pdf")},
                        content_type="multipart/form-data")
        http_ms = (time.perf_counter() - t) * 1000
    assert r.status_code == 201, r.get_data(as_text=True)
    row = {k: round(sum(v), 3) for k, v in timings.items()}
    row["http_upload_cv_ms"] = round(http_ms, 3)
    # submit-user commit is outside this request; keep only the upload's commit
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warm-passes", type=int, default=5)
    args = ap.parse_args()

    pdfs = render_pdfs()
    names = list(pdfs)
    client = app.test_client()

    cold = {"cv": names[0], **upload(client, names[0], pdfs[names[0]]["path"])}
    memory["after_first_upload_mb"] = rss_mb()

    warm = {n: [] for n in names}
    for _ in range(args.warm_passes):
        for n in names:
            warm[n].append(upload(client, n, pdfs[n]["path"]))

    # Fallback extractor cost, measured directly: pdfplumber always succeeds on these PDFs.
    fallback = {}
    for n in names:
        runs = []
        for _ in range(args.warm_passes):
            t = time.perf_counter()
            import pymupdf
            d = pymupdf.open(pdfs[n]["path"])
            "\n\n".join(p.get_text("text", sort=True) for p in d)
            d.close()
            runs.append((time.perf_counter() - t) * 1000)
        fallback[n] = round(statistics.median(runs), 3)

    def med(rows, key):
        vals = [r.get(key, 0.0) for r in rows]
        return round(statistics.median(vals), 3)

    keys = sorted({k for rows in warm.values() for r in rows for k in r})
    warm_median = {n: {k: med(rows, k) for k in keys} for n, rows in warm.items()}
    all_rows = [r for rows in warm.values() for r in rows]
    warm_overall = {k: med(all_rows, k) for k in keys}
    warm_p95 = {}
    for k in keys:
        vals = sorted(r.get(k, 0.0) for r in all_rows)
        warm_p95[k] = round(vals[min(len(vals) - 1, int(0.95 * len(vals)))], 3)

    mi = PROC.memory_info()
    memory["final_rss_mb"] = mi.rss / 2**20
    memory["peak_working_set_mb"] = getattr(mi, "peak_wset", 0) / 2**20

    print(json.dumps({
        "startup_ms": {k: round(v, 1) for k, v in startup.items()},
        "memory_mb": {k: round(v, 1) for k, v in memory.items()},
        "pdfs": {n: {k: v for k, v in p.items() if k != "path"} for n, p in pdfs.items()},
        "cold_first_upload_ms": cold,
        "warm_median_ms_overall": warm_overall,
        "warm_p95_ms_overall": warm_p95,
        "warm_median_ms_per_cv": warm_median,
        "pymupdf_fallback_median_ms_per_cv": fallback,
        "warm_passes": args.warm_passes,
    }, indent=1))


if __name__ == "__main__":
    main()

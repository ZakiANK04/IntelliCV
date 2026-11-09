# Where analysis time goes today (2026-11-09)

Answers [Where does analysis time go today?](https://github.com/ZakiANK04/IntelliCV/issues/3).
Throwaway branch, never merged.

## Setup

- Machine: AMD Ryzen AI 9 365, 31 GB RAM, Windows 11 Home, Balanced power plan, **on battery**
  (expect a few percent slower than mains).
- Python 3.13.15 `.venv` per `docs/running-and-testing.md`: spaCy 3.8.18 with `en_core_web_sm`,
  pdfplumber 0.11.10, PyMuPDF, ftfy 6.3.1, Flask 3.1.3, SQLite.
- Harness: [`profiling/profile_analysis.py`](../../profiling/profile_analysis.py). It renders the 7
  samples in `tests/test_data/sample_cvs.py` to PDF with the PyMuPDF recipe from
  `docs/running-and-testing.md` (1 to 2 pages, 1 to 3 KB, 254 to 2,478 chars), builds the app with
  `create_app()` (production config, temp SQLite and upload dir), and drives the real routes through
  the Flask test client: `POST /api/submit-user`, then `POST /api/upload-cv`. Each pipeline function
  is wrapped with a timer in place, so the numbers are the production code paths.
- 4 fresh processes. In each: 1 cold upload (first in the process), then 10 warm passes over all 7
  CVs (70 uploads). Raw output: `profiling/results/run1..4.json`, import trace
  `profiling/results/importtime.txt`.
- Figures below are medians across the 4 processes. Warm figures are the median (and p95) over 70
  uploads per process.

## Process start (once per worker)

| Step | ms |
|---|---|
| Interpreter start | 696 |
| `import spacy` | 5,110 |
| `from app import create_app` (Flask, SQLAlchemy, flask_wtf, ...) | 2,572 |
| `spacy.load('en_core_web_sm')` | 647 |
| rest of `create_app()` (blueprints, `db.create_all`) | 244 |
| **Script start to app ready** | **8,762** |

`-X importtime` shows the `import spacy` cost is mostly spaCy pulling in `spacy.cli`
(download/info), thinc and its config machinery; SQLAlchemy is about 1.3 s of the app import. The
model load itself is under 1 s. The dev server (`run.py`, `debug=True`) pays all of this twice,
because the reloader loads spaCy in both the watcher and the worker.

## One analysis, cold vs warm

`process_cv` is everything inside the request after Flask parses the upload.

| Step | Cold (first upload) ms | Warm median ms | Warm p95 ms |
|---|---|---|---|
| save upload to disk | 1.1 | 1.0 | 2.4 |
| `validate_pdf` | 2.8 | 2.7 | 3.8 |
| extraction: pdfplumber | 434 | 76 | 126 |
| extraction: `_clean_and_normalize` | 214 | 2.8 | 4.5 |
| NLP `_detect_sections` | 59 | 60 | 93 |
| NLP `_extract_skills` | 92 | 88 | 127 |
| NLP `_extract_entities` (regex + spaCy NER) | 217 | 141 | 172 |
| NLP `_detect_career_field` | 4.1 | 3.4 | 4.4 |
| NLP `_detect_experience_level` | 0.6 | 0.5 | 2.5 |
| NLP `_calculate_scores` | 1.1 | 0.6 | 1.2 |
| NLP strengths, weaknesses, recommendations, YouTube | <0.1 | <0.1 | <0.1 |
| NLP `analyze` total | 362 | 269 | 337 |
| DB commit (SQLite) | 84 | 58 | 64 |
| **`process_cv` total** | **1,086** | **406** | **576** |
| **HTTP `/api/upload-cv` (test client)** | **1,224** | **410** | **581** |

Warm per CV (one process): from 166 ms (`poor_quality`, 254 chars) to 453 ms
(`senior_software_engineer`, 2 pages). Time scales with text length.

PyMuPDF fallback never fires on these PDFs (pdfplumber always returns text). Timed directly it
takes 5 to 24 ms per CV, about 4x faster than pdfplumber.

### What the cold cost is

The first upload is about 680 ms slower than a warm one. Nearly all of it is lazy imports inside
the request: `pdfplumber` is imported inside `_extract_with_pdfplumber` (+360 ms) and `ftfy` inside
`_clean_and_normalize` (+210 ms), plus spaCy's first-call warm-up in NER (+75 ms) and the first
SQLite commit (+25 ms).

### Why the rule-based steps are slow

`_extract_skills` runs 640 separate `re.search` calls, one per skill. Python's `re` cache holds 512
patterns, so the skill patterns (plus 44 section-header patterns) evict each other and are
recompiled on every call: precompiling them alone cuts the step from 88 to 47 ms, and a single
alternation or a set lookup over tokens would go well below that. `_detect_sections` compiles each
header regex per call too, and calls `_extract_skills` again when no Skills header is found. These
are code-quality costs, not language costs.

## Memory

| Point | RSS MB |
|---|---|
| Interpreter | 22 |
| After `import spacy` | 89 |
| spaCy model load (delta) | +41 |
| App ready | 160 |
| After first upload | 211 |
| After 71 uploads | 239 |
| **Peak working set** | **299** |

## What the browser shows

The upload wizard (`app/templates/upload.html`, `simulateProgress`) ticks its four processing
steps on a fixed 1.5 s timer (1.5, 3.0, 4.5, 6.0 s), unrelated to server progress. It redirects to
`/results/<id>` as soon as `/api/upload-cv` returns. With a warm worker the request takes about
0.4 s (0.6 s p95) plus network, so the user sees the processing screen with **no ticks at all**
before the redirect; on the cold first request (about 1.2 s) still none. The ticks only appear if
the request exceeds 1.5 s. The results page then animates the score for about 1 s
(50 steps of 20 ms) and the bars after 300 ms. The browser also renders a PDF.js preview of page 1
on file selection, client side, before upload.

## Summary for the decisions waiting on this

- Warm analysis of a 1 to 2 page digital PDF: about **0.4 s** server time, of which spaCy NER is
  about 35%, the two rule-based steps (skills, sections) about 35%, pdfplumber about 19% and the
  SQLite commit about 14%.
- About half the rule-based time is avoidable in Python (regex cache thrash, per-call compiles);
  pdfplumber can be swapped for PyMuPDF (4x faster) without leaving Python.
- Process start is **8.8 s**, dominated by imports (spaCy 5.1 s, Flask/SQLAlchemy stack 2.6 s), not
  by the model (0.65 s). A long-lived worker hides it; a scale-to-zero host pays it on every cold
  start.
- The cold first request adds about 0.7 s of lazy imports.
- Memory: about 300 MB peak per worker with the small English model only.
- Not measured: DOCX and OCR (the app has neither), real-world CVs (multi-column, 3+ pages,
  images), concurrency (the dev server is single-process), network and browser rendering time,
  Linux.

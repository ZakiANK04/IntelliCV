# Known issues

Each entry was verified on 2026-11-08 by reading the code and, where marked, by running it.
Ordered by how much they distort what a user sees. When you fix one, remove it here and update the
doc that describes the behaviour.

## Analysis correctness

### 1. Skills with symbols never match; tiny skills match everywhere (verified by run)

`\bc\+\+\b`, `\bc#\b`, `\b\.net\b`, `\basp\.net\b` cannot match. "C++" is reported as `c`. One-letter
`r`, `c` and two-letter `go` match "R&D", "plan C", "go to market". Fix: use
`(?<![\w+#.])skill(?![\w+#])` style lookarounds.

### 2. Career field uses substring matching

Short keywords (`pr`, `hr`, `bi`, `ev`, `car`, `art`, `design`, `law`...) match inside other words,
so most CVs score in many unrelated fields and `General` is never returned. The "poor quality"
sample is labelled `Teacher`. Use word boundaries as `_extract_skills` does.

### 3. Smaller logic slips

- `_score_section_quality`: the `word_count > 200` (+2) branch is unreachable after `> 100`.
- `_detect_section_by_content` for work experience runs on the whole CV and counts "present" inside
  "presentation".
- `_generate_recommendations` has a branch for field `"Software Development"`, which doesn't exist.
- `_calculate_scores` computes a sentence count for readability and never uses it.
- Skill scoring saturates at 13 skills; soft skills count as much as technical ones.
- Career scoring saturates at 6 skills listed for the field: 4 of the 7 samples score 100.
- `config.SCORING_WEIGHTS`, `CV_SECTIONS`, `SPACY_MODEL` are never read; changing them does nothing.
- YouTube `video_id`s are hard-coded and only drive thumbnails; `'197472099'` is not a YouTube ID.
- Section `explanation` strings and all of `analysis_json` are stored but never shown in the UI.

## Security and privacy

- **Public results and API.** `/results/<id>`, `/api/analysis/<id>` (includes email and phone) and
  `/api/analysis/<id>/summary` need no auth, and IDs are sequential. Anyone can enumerate every
  candidate's name, contact details and analysis.
- **Uploaded CVs served without auth** at `/uploads/<filename>`; only the random filename protects
  them.
- **Default secrets.** `SECRET_KEY` falls back to a constant in `config.py`; admin defaults to
  `admin` / `admin123`, which `run.py` prints. Changing `ADMIN_PASSWORD` later doesn't remove the
  old `admin` row with the old hash.
- `/api/upload-cv` accepts any existing `user_id`; no binding between the wizard's step 1 and step 2.
- `CORS(app)` with defaults allows every origin on every route.
- No rate limiting on login or on the analysis endpoint (each upload costs ~1 s of CPU).
- PDFs and full text kept forever; no consent text, no retention policy.
- Dockerfile `chmod 777 uploads`.

## Ops and repo hygiene

- `create_db.py` is broken (MySQL leftover, `Config.MYSQL_HOST` doesn't exist, `pymysql` not
  installed). `.env.example` only lists unused `MYSQL_*` vars, and nothing loads `.env`.
- `requirements.txt` pulls torch, transformers and sentence-transformers that nothing imports.
- No migrations; schema changes need manual work on an existing `app.db`.
- Docker runs `DevelopmentConfig` (no `FLASK_CONFIG` set).
- Chart.js loaded from jsDelivr with no version and never used; Tailwind via the Play CDN, which is
  not meant for production.
- `test_api.py` writes into the real `app.db`.
- Uses legacy `Query.get()` (SQLAlchemy 2.0 deprecation) and `datetime.utcnow()` (deprecated in 3.12).
- `fitz` import emits a FutureWarning (PyMuPDF wants `import pymupdf`).

## README claims that do not match the code

| README says | Code does |
|---|---|
| NFKC normalisation | NFC (`unicodedata.normalize('NFC')`) |
| `validate_pdf` checks page count and encryption | Checks existence, size and `%PDF` header only |
| "MySQL is the configured backend, `config.py` reads `MYSQL_*`" | SQLite by default, `DATABASE_URL` override, no `MYSQL_*` read |
| `create_db.py` initialises the schema | It crashes; `create_app()` runs `create_all()` |
| "~40 heading variants" | 44 patterns |
| Validation reports are committed in `tests/reports/` | JSON reports are git-ignored; only `README.md` is there |
| Each section's explanation is shown on the result page | Stored, never rendered |

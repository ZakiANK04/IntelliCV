# Overview

## Goal

IntelliCV takes a PDF résumé and returns a 0–100 score that can be explained: five weighted
sub-scores, a per-section verdict, the skills it found, strengths and weaknesses, concrete
recommendations, and YouTube learning links. The pitch is "a score with its reasoning attached",
as opposed to CV checkers that only print a number.

It is a student project by Ahcene Zakaria Aouanouk (Data Science & AI, Algiers), imported into this
workspace from the Hugging Face Space `Zaki47/Intellicv`. The git history is a single import commit
(`3d632be`).

## What it does today

1. A visitor fills in name, email and phone. A `User` row is created.
2. They drop a PDF (max 16 MB). The browser renders page 1 with PDF.js as a preview.
3. The server saves the file under a random name, checks it is a PDF, extracts text
   (pdfplumber, falling back to PyMuPDF), cleans it, and runs the rule-based analyser.
4. The result is stored in one `CVAnalysis` row and the browser is sent to `/results/<id>`.
5. An admin can log in at `/admin` to see stats, search and filter submissions, read the extracted
   text, download the original PDF, delete a submission, list users, and export everything as CSV.

Everything is rules plus spaCy NER. There is no trained model, no embeddings, no LLM, and no job
description matching. `transformers`, `torch` and `sentence-transformers` are in
`requirements.txt` but nothing imports them.

## What it is not

- Not multilingual: patterns, skills and spaCy model (`en_core_web_sm`) are English only.
- Not private by default: results pages and the JSON API have no auth, IDs are sequential.
  See [known-issues.md](known-issues.md#security-and-privacy).
- Not a job matcher: "career field" is a guess at which of 32 fields the CV belongs to.

## Stack (as installed and run on 2026-11-08)

| Layer | What |
|---|---|
| Runtime | Python 3.13 (Docker image `python:3.13-slim`; spaCy has no wheels for 3.14 yet) |
| Web | Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-WTF (CSRF), Flask-CORS, gunicorn |
| DB | SQLite at `app.db` by default, any SQLAlchemy URL via `DATABASE_URL` |
| PDF | pdfplumber, PyMuPDF (`fitz`) |
| Text | `unicodedata` (NFC), ftfy, `re` |
| NLP | spaCy 3.8 + `en_core_web_sm` 3.8 (NER only) |
| Frontend | Jinja2, Tailwind Play CDN, Font Awesome 6.5.1, PDF.js 3.11.174, Chart.js (unpinned), Google Fonts |
| Deploy | Docker, Hugging Face Spaces on port 7860 |

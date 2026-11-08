# IntelliCV

Flask app that scores PDF résumés with rules + spaCy. Code is in `app/`, tests in `tests/`.

## Source of truth: `docs/`

Read `docs/README.md` first; it says which doc covers what. Those docs describe the code as it
behaves today and were checked against a live run. The top-level `README.md` is a portfolio
write-up with several wrong claims (listed in `docs/known-issues.md`); don't trust it over `docs/`.

- Before changing analysis or scoring logic, read `docs/analysis-pipeline.md` and `docs/scoring.md`.
- Before fixing a bug, check `docs/known-issues.md`; it may already be diagnosed with a fix direction.
- **Any change to behaviour updates the matching doc in the same commit.** Fixing a known issue
  removes its entry. New behaviour gets documented where a reader would look for it.
- Docs cite files and function names, not line numbers. Numbers from runs carry their date.

## Running

Python 3.13 venv in `.venv` (spaCy has no 3.14 wheels). Setup, server, tests and the accuracy
validator are in `docs/running-and-testing.md`. On Windows set `PYTHONIOENCODING=utf-8` for the test
runner and validator.

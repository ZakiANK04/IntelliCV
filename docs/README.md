# IntelliCV docs

These files describe what the code does **today**, checked against the source and a live run on
2026-11-08. They are the source of truth for working on the project. Where the top-level
`README.md` disagrees with them, these docs win: the README is a portfolio write-up and is wrong in
several places (listed in [known-issues.md](known-issues.md#readme-claims-that-do-not-match-the-code)).

| File | Read it when |
|---|---|
| [overview.md](overview.md) | You need the goal, the scope, and the stack in five minutes |
| [architecture.md](architecture.md) | You are changing how the app is wired: factory, blueprints, services, config, storage, deployment |
| [features.md](features.md) | You are changing anything a user or admin sees |
| [analysis-pipeline.md](analysis-pipeline.md) | You are touching PDF extraction, text cleaning, section/skill/field/level detection, or advice |
| [scoring.md](scoring.md) | You are touching any number on the results page |
| [api.md](api.md) | You are calling or changing an HTTP route |
| [data-model.md](data-model.md) | You are changing a table or the JSON stored in it |
| [running-and-testing.md](running-and-testing.md) | You want to run it, test it, or deploy it |
| [known-issues.md](known-issues.md) | Before fixing a bug, and before trusting a score |

## Keeping these docs true

- A change to behaviour updates the matching doc in the same commit. A doc that describes old
  behaviour is worse than no doc.
- Every claim about logic names its file and function, so it can be re-checked with one read.
  Line numbers are left out on purpose: they drift. Function names don't.
- When you fix something in [known-issues.md](known-issues.md), delete the entry (or move it to
  "Fixed" with the date) and update the doc that described the old behaviour.
- Numbers quoted from a run (test counts, validator accuracy, timings) carry the date of the run.

## Layout of the repo

```
IntelliCV/                 git repo root (this folder)
  run.py                   dev entry point + gunicorn target (run:app)
  config.py                Config classes, read from env
  create_db.py             broken leftover from a MySQL version (see known-issues)
  Dockerfile               Hugging Face Spaces image, gunicorn on :7860
  app/
    __init__.py            create_app() factory, extensions, error handlers
    models.py              User, CVAnalysis, AdminUser
    routes/main.py         public pages
    routes/api.py          JSON API used by the upload wizard
    routes/admin.py        login, dashboard, submissions, users, CSV export
    services/pdf_extractor.py   PDF -> cleaned text
    services/nlp_analyzer.py    text -> AnalysisResult (all the rules live here)
    services/cv_analyzer.py     orchestration + persistence
    templates/             Jinja pages (Tailwind via CDN)
    static/                logo, favicon, landing images, testimonial photos
  tests/                   unittest suite + accuracy validator + sample CVs
  docs/                    you are here
```

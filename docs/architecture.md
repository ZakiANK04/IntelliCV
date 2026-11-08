# Architecture

A single Flask process. No queue, no background workers, no cache: a CV is analysed inside the
`POST /api/upload-cv` request and the response waits for it (about 1 s for a 2-page CV on the
dev machine).

```
Browser ──► main_bp   (/ , /upload , /results/<id> , /documentation , /uploads/<f>)   HTML
        ──► api_bp    (/api/*)            JSON, CSRF-exempt, no auth
        ──► admin_bp  (/admin/*)          HTML, Flask-Login session, CSRF on POST forms

api_bp.upload_cv ──► CVAnalyzerService.process_cv          (services/cv_analyzer.py)
                       ├─ save file  -> UPLOAD_FOLDER/<uuid4>.pdf
                       ├─ PDFExtractor.validate_pdf         (services/pdf_extractor.py)
                       ├─ PDFExtractor.extract_text         pdfplumber -> PyMuPDF -> _clean_and_normalize
                       ├─ NLPAnalyzer.analyze               (services/nlp_analyzer.py)
                       └─ CVAnalysis row -> db.session.commit()
```

## Application factory (`app/__init__.py`)

`create_app(config_name=None)`:

1. Picks the config from `FLASK_CONFIG` (default `development`). See [Config](#config).
2. Inits module-level extensions: `db = SQLAlchemy()`, `login_manager`, `csrf = CSRFProtect()`,
   and `CORS(app)` with defaults (every origin allowed on every route).
3. Sets `login_manager.login_view = 'admin.login'`.
4. `os.makedirs(UPLOAD_FOLDER)`.
5. Registers `main_bp` at `/`, `api_bp` at `/api`, `admin_bp` at `/admin`.
6. Runs `db.create_all()` inside an app context. There are no migrations: schema changes to an
   existing `app.db` need a manual `ALTER` or deleting the file.
7. Registers error handlers for 404, 500, 413. Paths under `/api/` get JSON
   (`{"error": ...}`), everything else gets `templates/errors/<code>.html`. The 500 handler rolls
   back the session.

`run.py` calls `create_app()` at import time (that `app` object is what gunicorn serves as
`run:app`). Run as a script it also seeds an `AdminUser` `admin`/`admin123` and starts the dev
server on `127.0.0.1:5000` with `debug=True`. Under gunicorn `init_database()` is not called;
the admin row is created on first login instead (see [features.md](features.md#admin-login)).

## Services are module singletons

Each service module ends with an instance created at import time:

| Module | Singleton | Import-time cost |
|---|---|---|
| `pdf_extractor.py` | `pdf_extractor = PDFExtractor()` | none |
| `nlp_analyzer.py` | `nlp_analyzer = NLPAnalyzer()` | loads spaCy `en_core_web_sm`; if missing it shells out to `python -m spacy download` and retries; on any failure `self.nlp = None` and NER is skipped silently |
| `cv_analyzer.py` | `cv_analyzer_service = CVAnalyzerService()` | imports the two above |

`app/routes/api.py` imports `cv_analyzer_service` at module level, so building the app loads spaCy.
Each gunicorn worker (2 in Docker) holds its own copy. The services keep no per-request state.

`CVAnalyzerService` needs an app context (`current_app.config['UPLOAD_FOLDER']`, `db.session`),
so it only runs inside a request or `app.app_context()`. `NLPAnalyzer` and `PDFExtractor` are plain
Python and are what the tests call directly.

## Config (`config.py`)

| Setting | Source / default | Notes |
|---|---|---|
| `SECRET_KEY` | env `SECRET_KEY`, else `'ai-cv-analyzer-secret-key-2024'` | Hard-coded fallback signs admin sessions |
| `SQLALCHEMY_DATABASE_URI` | env `DATABASE_URL`, else `sqlite:///<repo>/app.db` | |
| `UPLOAD_FOLDER` | env `UPLOAD_FOLDER`, else `<repo>/uploads` | |
| `MAX_CONTENT_LENGTH` | 16 MB | Werkzeug rejects bigger bodies with 413 |
| `ALLOWED_EXTENSIONS` | `{'pdf'}` | |
| `PERMANENT_SESSION_LIFETIME` | 24 h | Login does not set `remember`, so it is a browser-session cookie |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | env, else `admin` / `admin123` | |
| `SPACY_MODEL`, `SCORING_WEIGHTS`, `CV_SECTIONS` | constants | **Not read anywhere.** The analyser has its own hard-coded copies |

Config classes: `DevelopmentConfig` (DEBUG), `ProductionConfig`, `TestingConfig` (in-memory
SQLite). `config['default']` is development. The Dockerfile sets `FLASK_ENV=production` but not
`FLASK_CONFIG`, so the container runs `DevelopmentConfig` (gunicorn ignores `DEBUG`, so the
debugger is not exposed, but `app.debug` is True).

`.env.example` lists `MYSQL_*` variables. Nothing reads them, and `python-dotenv` is installed but
never called, so a `.env` file has no effect unless your shell exports it.

## Storage

- **Database**: three tables, see [data-model.md](data-model.md).
- **Uploads**: the original PDF is kept forever as `UPLOAD_FOLDER/<uuid4 hex>.pdf`. It is removed
  only when validation/extraction fails or an admin deletes the submission.
- **Extracted text**: stored in full in `cv_analysis.extracted_text`.

## Frontend

Server-rendered Jinja templates. `templates/base.html` is the public layout; `templates/admin/base.html`
is the admin layout; `admin/login.html` is standalone. Everything else extends one of them.

All styling is Tailwind through the Play CDN (`cdn.tailwindcss.com`, configured inline with
`darkMode: 'class'`) plus a large inline `<style>` block. Dark mode: `toggleTheme()` in `base.html`
flips the `dark` class on `<html>` and stores `localStorage.theme`; the default follows
`prefers-color-scheme`.

External scripts loaded on every public page: Tailwind CDN, Font Awesome 6.5.1, PDF.js 3.11.174
(+ its worker from cdnjs), Chart.js from jsDelivr with **no version pin**. Fonts: Space Grotesk and
Playfair Display from Google Fonts. No build step, no `package.json`, no GSAP.

The only page JavaScript with logic:

- `upload.html`: the 3-step wizard, drag and drop, PDF.js preview, the two `fetch` calls. See
  [features.md](features.md#upload-wizard-upload).
- `results.html`: animates the score ring, counter and bars from server-rendered values.
- `index.html`: IntersectionObserver reveals, count-up stats, a typing effect, a scroll parallax.

## Deployment (`Dockerfile`)

`python:3.13-slim`, apt installs `build-essential libgl1 libglib2.0-0 poppler-utils`, `pip install -r
requirements.txt` (pulls torch, a multi-GB layer that nothing uses), downloads `en_core_web_sm`,
copies the repo, `mkdir uploads && chmod 777`, then
`gunicorn --bind 0.0.0.0:7860 --workers 2 --timeout 120 run:app`.

On Hugging Face Spaces the filesystem is ephemeral, so `app.db` and `uploads/` reset on every
restart unless `DATABASE_URL` / `UPLOAD_FOLDER` point at a persistent volume.

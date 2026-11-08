# Features

Everything a visitor or admin can do, with the route and template behind it.

## Public site (`app/routes/main.py`, layout `templates/base.html`)

Navigation on every page: Home, Analyze CV, Documentation, a theme toggle, and an Admin button.
A mobile menu toggles with the `active` class.

### Landing page (`/`, `index.html`)

Marketing page: hero with a typing animation ("Understood." → "Refined." → "Humanized."), a features
grid (Structural NLP Analysis, Quantifiable Metrics, Skill Detection, Career Pivot), a stats strip, an
image collage (`static/img/collage_*.jpg`), three testimonials with photos (`melinia.png`,
`abdessamed.png`, `amine.png`), an FAQ, and a call to action.

The stats strip numbers (`12,402`, `95.4%`, `<0.8s`, `52`) are hard-coded in the template. They are
not read from the database or from `/api/stats`.

### Upload wizard (`/upload`, `upload.html`)

Three client-side steps in one page, switched by `showStep(n)`:

1. **Your Info**: full name, email, phone (all `required` in HTML). Submit posts JSON to
   `POST /api/submit-user`; on success the returned `user_id` is kept in a JS variable.
2. **Upload CV**: click or drag-and-drop. The client rejects non-`.pdf` names and files over 16 MB,
   then renders page 1 of the PDF onto a canvas with PDF.js (scale 1.5). "Analyze CV" is enabled
   once a file is chosen. "Back" returns to step 1 (a second submit there creates a second `User`).
3. **Analysis**: posts `FormData{user_id, cv_file}` to `POST /api/upload-cv`. The four progress
   ticks ("Extracting text", "Running NLP", "Calculating scores", "Generating recommendations")
   are a fake timer, one every 1.5 s, unrelated to server progress. On success the browser goes to
   `redirect_url`; on error it returns to step 2 and shows the message for 5 s.

`/api/validate-pdf` exists but the wizard never calls it.

### Results (`/results/<id>`, `results.html`)

Rendered on the server from the `CVAnalysis` row. No login required. Shows:

- Overall score ring (green ≥ 70, yellow ≥ 40, red below) and a verdict line
  (≥ 80 "Excellent", ≥ 60 "Good", ≥ 40 "Average", else "Needs significant improvement").
- Experience level, career field, number of skills, processing time.
- Five sub-score bars with their weights (see [scoring.md](scoring.md)).
- The nine sections: tick or cross, and a `quality_score/10` badge (green ≥ 7, yellow ≥ 4, red).
  The per-section `explanation` string is stored but **not shown anywhere**, here or in admin.
  Neither are the extracted entities, extraction method or warnings in `analysis_json`; only the
  JSON API returns them.
- Skills as chips.
- Strengths, "Areas for Improvement" (weaknesses), numbered recommendations.
- Learning Resources: up to 5 cards. The link is a YouTube **search** for `suggestion.query`; the
  thumbnail comes from the hard-coded `video_id`, which is unrelated to the search and sometimes
  invalid (see [known-issues.md](known-issues.md)).
- "Analyze Another CV" and "Print Results" (`window.print()`).

### Documentation page (`/documentation`, `documentation.html`)

A static in-app write-up: overview, architecture, NLP pipeline, scoring, libraries, database,
ethics, limitations. It is hand-written HTML and is not generated from these docs; check it against
them before trusting it.

### Error pages

`errors/404.html`, `413.html`, `500.html`. API paths get JSON instead.

## Admin (`app/routes/admin.py`, layout `templates/admin/base.html`)

Sidebar: Dashboard, Submissions, Users, Export CSV, Logout. Every route except `/admin/login`
needs a Flask-Login session; unauthenticated requests redirect to `/admin/login?next=...`.

### Admin login

`GET/POST /admin/login`, standalone template with a CSRF token. Two ways in, checked in order:

1. Username and password equal `ADMIN_USERNAME` / `ADMIN_PASSWORD` from config (plain string
   compare). If no `AdminUser` row has that username it is created with that password hashed.
2. Otherwise, any `AdminUser` row whose Werkzeug hash matches.

`last_login` is updated, a flash message is set, and the user lands on the dashboard. No rate
limiting, no lockout. There is no UI for creating or managing admin users.

### Dashboard (`/admin/`, `/admin/dashboard`)

Totals (users, analyses, mean score), the 10 newest analyses, a score histogram in five 20-point
buckets (CSS bars sized as a share of all analyses), and the count per stored experience level.
Plain HTML/CSS: Chart.js is loaded by the layout but no page creates a chart.

### Submissions (`/admin/submissions`)

20 per page, newest first. Filters (GET params, combined with AND):

- `search`: case-insensitive substring on user name, user email, or career field.
- `min_score`, `max_score`: inclusive.
- `experience`: exact match on the stored level string. Rows analysed before 2026-11-08 can hold
  `Mid Level`, which the `Mid-Level` option doesn't match (see
  [analysis-pipeline.md](analysis-pipeline.md#experience-level)).

Each row links to the admin detail page and the public results page, and has a Delete button
(POST with CSRF, JS confirm).

### Submission detail (`/admin/submission/<id>`)

User contact details, scores, sections with their quality scores, skills, the first 5,000
characters of extracted text, links to the public results page and to the original PDF
(`/uploads/<stored_filename>`), and Delete.

### Delete (`POST /admin/submission/<id>/delete`)

`CVAnalyzerService.delete_analysis`: removes the PDF from disk, then the row. The `User` row stays.

### Users (`/admin/users`)

20 per page, newest first, `search` on name or email.

### CSV export (`/admin/export/csv`)

All analyses joined with users, newest first, as `cv_submissions_<YYYYmmdd_HHMMSS>.csv`. Columns:
ID, Full Name, Email, Phone, Score, Experience Level, Career Field, the five sub-scores, Skills Found
(comma-joined), Submitted At, Processing Time (`"1.04s"`).

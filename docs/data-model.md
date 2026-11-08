# Data model

`app/models.py`, SQLAlchemy 2 typed mappings. Tables are created by `db.create_all()` in
`create_app()`; there are no migrations. Timestamps use `datetime.utcnow` (naive UTC).

```
users 1 ──< cv_analysis          (cascade delete-orphan from User)
admin_users                      (standalone)
```

## `users` (`User`)

| Column | Type | Notes |
|---|---|---|
| id | int PK | autoincrement, sequential |
| full_name | str(255) | required |
| email | str(255) | required, indexed, lowercased by the API, not unique |
| phone | str(50) | required |
| created_at | datetime | |

`to_dict()` returns all five fields, `created_at` as ISO string.

## `cv_analysis` (`CVAnalysis`)

| Column | Type | Content |
|---|---|---|
| id | int PK | sequential, used in public URLs |
| user_id | FK users.id | |
| original_filename | str(255) | `secure_filename` of the upload |
| stored_filename | str(255) | `<uuid4 hex>.pdf` in `UPLOAD_FOLDER` |
| extracted_text | Text | full cleaned text |
| text_length | int | `len(extracted_text)` |
| score | float | overall, 2 dp |
| experience_level | str(50) | `Fresher`, `Junior`, `Mid-Level`, `Senior`, `Unknown` (rows analysed before 2026-11-08 may hold `Mid Level`) |
| career_field | str(100) | one of the 32 field names, or `General` |
| experience_score, skills_score, structure_score, career_score, readability_score | float | 0–100, 2 dp |
| sections_detected | JSON | see below |
| skills_found | JSON | `["python", "sql", ...]` in database order |
| recommendations | JSON | see below |
| analysis_json | JSON | see below |
| created_at | datetime | |
| processing_time | float | seconds, 2 dp |

### `sections_detected`

Always all nine keys:

```json
{
  "professional_summary": {"detected": true, "quality_score": 6.0, "explanation": "Good professional summary section with adequate information"},
  "internship_experience": {"detected": false, "quality_score": 0.0, "explanation": ""},
  ...
}
```

### `recommendations`

```json
{
  "strengths": ["..."],          // ≤ 5
  "weaknesses": ["..."],         // ≤ 5
  "recommendations": ["..."],    // ≤ 7
  "youtube_suggestions": [       // ≤ 5
    {"title": "...", "query": "...", "video_id": "...", "reason": "..."}
  ]
}
```

### `analysis_json`

```json
{
  "entities": {"names": [], "organizations": [], "locations": [], "dates": [], "emails": [], "phones": []},
  "extraction_method": "pdfplumber",   // or "pymupdf"
  "pages_processed": 2,
  "extraction_warnings": []
}
```

### `CVAnalysis.to_dict()`

Used by `GET /api/analysis/<id>`. Includes `user` (the `User.to_dict()`), all scores, the three
JSON columns, `original_filename`, `created_at`, `processing_time`. Leaves out `stored_filename`,
`extracted_text`, `text_length`.

## `admin_users` (`AdminUser`, Flask-Login `UserMixin`)

| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| username | str(100) | unique |
| password_hash | str(255) | Werkzeug `generate_password_hash` |
| created_at | datetime | |
| last_login | datetime, nullable | set on each login |

`load_user` uses the legacy `AdminUser.query.get(int(id))`.

Rows are created by `run.py:init_database()` (`admin`/`admin123`, only when run as a script) and by
the login route on the first successful config-credential login. Note that if
`ADMIN_PASSWORD` is changed later, the old row keeps the old hash and the old password still works
through the database check.

## Personal data held

Name, email, phone, the original PDF, and the full CV text, kept indefinitely. No consent step, no
retention job, no user-facing delete. Deleting a submission in admin keeps the `User` row.

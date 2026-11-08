# HTTP routes

All verified against a running dev server on 2026-11-08.

## JSON API (`app/routes/api.py`, prefix `/api`)

The whole blueprint is `csrf.exempt`. None of it requires login. CORS allows every origin.
Errors are `{"error": "<message>"}` (validate-pdf uses `{"valid": false, "error": ...}`).
Unexpected exceptions return 500 with `str(exception)` as the message.

### `POST /api/submit-user`

Body (JSON): `{"full_name": str, "email": str, "phone": str}`, all three non-empty.
Values are stripped; email is lowercased. Nothing else is validated (no email format check, no
dedupe: the same person submitting twice gets two `User` rows).

- 201 `{"success": true, "user_id": 3, "message": "User information saved successfully"}`
- 400 `No data provided` | `<field> is required`

### `POST /api/upload-cv`

Body (multipart): `user_id`, `cv_file`.

Checks in order: `user_id` present (400) → user exists (404 `User not found`) → `cv_file` part
present (400) → filename not empty (400) → extension is `.pdf` (400) → then
[`process_cv`](analysis-pipeline.md#1-orchestration-cvanalyzerserviceprocess_cv). Any failure
inside processing is 400 with the service message, e.g. `Invalid PDF: Invalid PDF format`.

- 201 `{"success": true, "analysis_id": 1, "message": "CV analyzed successfully", "redirect_url": "/results/1"}`
- 413 JSON when the body is over 16 MB.

The `user_id` is not tied to the caller in any way: anyone can attach a CV to any existing user.

### `POST /api/validate-pdf`

Multipart `file`. Checks the extension and the `%PDF` header only.
200 `{"valid": true, "filename": "<secure_filename>"}`, or 400 with `valid: false`. Not used by the UI.

### `GET /api/analysis/<id>`

`CVAnalysis.to_dict()`: every column except `stored_filename`, `extracted_text` and `text_length`,
plus the nested `user` (name, **email, phone**). 404 JSON if missing. Shape in
[data-model.md](data-model.md#cvanalysisto_dict).

### `GET /api/analysis/<id>/summary`

```json
{"id": 1, "score": 96.12, "experience_level": "Mid-Level", "career_field": "Machine Learning",
 "skills_count": 32, "sections_detected": 6, "processing_time": 1.04}
```

### `GET /api/stats`

`{"total_users": int, "total_analyses": int, "average_score": float (2 dp)}`. Not used by the UI.

## Pages (`app/routes/main.py`)

| Route | Template | Notes |
|---|---|---|
| `GET /` | `index.html` | |
| `GET /upload` | `upload.html` | |
| `GET /results/<id>` | `results.html` | No auth. 404 if missing |
| `GET /documentation` | `documentation.html` | |
| `GET /uploads/<filename>` | file | Serves any file from `UPLOAD_FOLDER` with no auth; the docstring says "for admin use". Filenames are 128-bit random, which is the only protection |

## Admin (`app/routes/admin.py`, prefix `/admin`)

All require login except `/login`. POST forms carry a CSRF token; a POST without it gets 400.

| Method | Route | Does |
|---|---|---|
| GET, POST | `/admin/login` | See [features.md](features.md#admin-login) |
| GET | `/admin/logout` | Logs out, redirects to login |
| GET | `/admin/`, `/admin/dashboard` | Stats page |
| GET | `/admin/submissions?page&search&min_score&max_score&experience` | Paginated list |
| GET | `/admin/submission/<id>` | Detail |
| POST | `/admin/submission/<id>/delete` | Delete row + PDF |
| GET | `/admin/export/csv` | CSV download |
| GET | `/admin/users?page&search` | Paginated list |

## Error handling

`app/__init__.py:register_error_handlers`: 404, 500 and 413 return JSON under `/api/` and an HTML
page elsewhere.

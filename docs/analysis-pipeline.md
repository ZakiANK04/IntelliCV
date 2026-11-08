# Analysis pipeline

From uploaded file to `CVAnalysis` row. Orchestrated by `CVAnalyzerService.process_cv`
(`app/services/cv_analyzer.py`). All rules live in `app/services/pdf_extractor.py` and
`app/services/nlp_analyzer.py`. Scores are in [scoring.md](scoring.md); verified defects are in
[known-issues.md](known-issues.md).

## 1. Orchestration (`CVAnalyzerService.process_cv`)

1. `stored_filename = uuid4().hex + ext`; `file.save(UPLOAD_FOLDER/stored_filename)`.
2. `pdf_extractor.validate_pdf(path)`. On failure: delete the file, return
   `(False, "Invalid PDF: <reason>")` → API answers 400.
3. `pdf_extractor.extract_text(path)`. If `metadata['success']` is false: delete the file, return
   `"Failed to extract text from PDF"` → 400. Scanned (image-only) PDFs end here: there is no OCR.
4. `nlp_analyzer.analyze(text)` → `AnalysisResult`.
5. Build the `CVAnalysis` row: every score rounded to 2 decimals, sections converted by
   `_sections_to_dict` (drops `content`, `start_pos`, `end_pos`), advice packed into
   `recommendations`, NER and extraction metadata packed into `analysis_json`.
   `processing_time` covers save + extract + analyse, not the commit.
6. `db.session.commit()`.
7. Any exception: rollback, delete the file if it exists, return `"Processing error: <exc>"`.

## 2. PDF validation (`PDFExtractor.validate_pdf`)

Checks, in order: file exists; size is not 0; size ≤ 16 MB; first bytes start with `%PDF`. That is
all. It does not check page count or encryption (the README says it does).

## 3. Text extraction (`PDFExtractor.extract_text`)

- **pdfplumber first**: `page.extract_text(x_tolerance=2, y_tolerance=2, layout=False,
  x_density=7.25, y_density=13)` per page, pages joined with `\n\n`. Accepted if the stripped text
  is longer than 50 characters.
- **PyMuPDF fallback** if pdfplumber raised or returned ≤ 50 chars: `page.get_text("text",
  sort=True)`, same join and same 50-char rule.
- If both fail: `("", {success: False, ...})`.
- Metadata: `{method: 'pdfplumber'|'pymupdf'|None, pages: int, warnings: [str], success: bool}`.
  `warnings` holds the pdfplumber error when the fallback was used.

## 4. Cleaning (`PDFExtractor._clean_and_normalize`)

Applied to the extracted text before anything else sees it. Steps in order:

1. `unicodedata.normalize('NFC')` (NFC, not the NFKC the README claims, so ligatures like `ﬁ`
   survive unless ftfy fixes them).
2. `ftfy.fix_text` if ftfy is importable.
3. Character map: bullets `U+F0B7 U+F0A7 U+2022 U+2023 U+25CF U+25E6` → `•`; `U+2043 U+F02D`
   and en/em dashes → `-`; curly quotes → straight; NBSP → space; zero-width space and BOM removed; tab → space.
4. Drop every Unicode category `C*` character except `\n` and `\r`.
5. Join letter-spaced words: every run of three or more single letters separated by single
   spaces (`\b(?:[A-Za-z] ){2,}[A-Za-z]\b`) loses its spaces, so `J a v a` becomes `Java`. The
   pattern matches a literal space, never a newline, and needs three letters, so ordinary
   one-letter words survive: `"Worked at a big firm"` and `"A B testing"` are unchanged. The seven
   sample CVs score the same before and after cleaning (checked 2026-11-08).
6. Collapse runs of spaces.
7. Re-flow lines: strip each line; keep at most one blank line in a row; join a line onto the
   previous one if the previous doesn't end in `. ! ? : ;` and this one starts lowercase; join
   without a space if the previous ends in `-`.
8. Collapse 3+ newlines to 2; strip.

## 5. NLP analysis (`NLPAnalyzer.analyze`)

If the text is shorter than 50 chars after strip, returns an empty `AnalysisResult` with one
weakness ("CV text is too short or empty"). Otherwise, in order:

| Step | Method | Input |
|---|---|---|
| Sections | `_detect_sections(text)` | original case |
| Skills | `_extract_skills(text_lower)` | lowercased |
| Entities | `_extract_entities(text)` | original case |
| Career field | `_detect_career_field(text_lower, skills)` | |
| Experience level | `_detect_experience_level(text_lower, sections)` | |
| Scores | `_calculate_scores(text, result)` | see scoring.md |
| Advice | `_identify_strengths`, `_identify_weaknesses`, `_generate_recommendations`, `_generate_youtube_suggestions` | the result so far |

### Sections (`_detect_sections`)

Nine sections, keyed `professional_summary, education, work_experience, internship_experience,
skills, projects, certifications, achievements, hobbies`. `SECTION_PATTERNS` holds 44 regex
fragments.

**Header pass.** For each section, its patterns are tried in order as
`^[\s•\-\*]*(<pattern>)[\s:]*$` with `IGNORECASE | MULTILINE`: the heading must be **alone on its
line** (optional leading bullets, optional trailing colon). `Experience` matches;
`Experience (5 years)` or `Skills & Tools` do not. The first match anywhere in the text wins.

Things that follow from the patterns:
- A bare `Experience` heading counts as work experience; `Qualifications` as education;
  `Works` as projects; `Activities` or `Interests` as hobbies.
- `Accomplishments` / `Key Accomplishments` matches both `projects` and `achievements`.
- `Profile` matches the summary.

**Section content** (`_extract_section_content`): from the end of the heading to the start of the
next line that matches any of the 44 patterns, capped at 2,000 characters.

**Content fallback** (`_detect_section_by_content`), only for `education`, `work_experience` and
`skills` when no heading was found. It searches the **whole** lowercased CV, not a block:

| Section | Signals (any match counts once) | Detected when |
|---|---|---|
| education | degree words (`bachelor`, `master`, `phd`, `b.s`, `m.a`...), `university/college/institute/school of X`, `gpa/cgpa <number>`, a `YYYY-YYYY` range | ≥ 2 of 4 |
| work_experience | `worked/working as/at/for`, `responsibilities:`/`duties:`, `<month> YYYY`, `present/current/ongoing` (substring, so "presentation" counts) | ≥ 2 of 4 |
| skills | number of skills found by `_extract_skills` | ≥ 3 |

A fallback-detected section gets `quality_score = confidence × 10` (education/work: 6.67 or 10;
skills: 6, 8 or 10), empty `content`, and the explanation
`"Detected by content analysis (confidence: NN%)"`.

**Quality score** (`_score_section_quality`, 0–10, header-detected sections only). Base 5, then by
word count of the content: `< 10` −2, `< 30` −1, `> 100` +1 (the `> 200` +2 branch is unreachable).
Then:

| Section | Bonus |
|---|---|
| professional_summary | +2 if 50–150 words; +1 if it contains experienced/skilled/passionate/seeking/goal |
| education | +1 degree word; +1 university/college/institute; +0.5 gpa/cgpa/grade |
| work_experience | +1 any 4-digit number; +1 developed/managed/led/created/implemented |
| skills | + min(skills found in the block / 3, 3) |
| projects | +1 developed/built/created/designed; +1 using/with/technologies |
| others | none |

Clamped to 0–10. The explanation (`_explain_section_quality`) is a template by band: ≥ 8
"Excellent ... comprehensive details", ≥ 6 "Good", ≥ 4 "Average", ≥ 2 "Weak", else "Missing or
very weak".

### Skills (`_extract_skills`)

`SKILLS_DATABASE`: 23 categories, 640 entries (625 unique; e.g. `agile`, `scrum`, `negotiation`
appear in more than one). Each entry is searched as `\b<re.escape(skill)>\b` in the lowercased text.
Output is the matched entries, deduplicated, in database order.

Consequences of the `\b...\b` match:
- Entries ending in a symbol never match: `c++`, `c#`, `.net`, `asp.net` (a word boundary needs a
  word character after the `+`/`#`). Writing "C++" yields the skill `c` instead.
- One- and two-letter entries match loosely: `r` matches "R&D", `c` matches "C++" or "plan C",
  `go` matches "go to market".
- Soft skills (`communication`, `teamwork`, `planning`...) count the same as technical ones.

### Entities (`_extract_entities`)

- Regex: emails, and phone numbers shaped like `(+cc) ddd ddd dddd`.
- spaCy `en_core_web_sm` on the first 100,000 chars: `PERSON` → `names`, `ORG` → `organizations`,
  `GPE`/`LOC` → `locations`, `DATE` → `dates`. Deduplicated with `set()` (order is lost).
- If spaCy failed to load, only emails/phones are filled and they are not deduplicated.

Entities are stored in `analysis_json.entities` and returned by the API. Nothing scores or displays
them. The small model tags tech names as people and orgs ("Keras" as a PERSON, "XGBoost" as an ORG
in the 2026-11-08 run).

### Career field (`_detect_career_field`)

`CAREER_FIELDS` has 32 fields, each with `job_titles`, `primary` and `secondary` keyword lists. For
each field, using **substring** matching on the lowercased CV (not word boundaries):

| Signal | Points |
|---|---|
| each job title present | +10, and +5 more if it is in the first 500 chars |
| each primary keyword present | +6 if multi-word, +4 if one word |
| each secondary keyword present | +2 |
| each extracted skill that equals one of the field's keywords | +3 |
| each matched primary keyword occurring more than twice | + min((count − 2) × 2, 8) |
| matches in 2 of the 3 lists | +5; all 3 lists: +10 |

Highest score wins (ties go to the field listed first). Two overrides:
1. A data subfield (ML, AI, NLP Engineer, Computer Vision, Data Analytics, Data Engineering) with
   no job-title match loses to `Data Science` if Data Science scored more than 70% of it and has a
   job-title match.
2. If `Information Technology` wins, the first of the next four fields that has a job-title match
   and more than 60% of IT's score takes over (unless it is Engineering).

`"General"` only when every field scores 0, which practically never happens: short keywords such as
`pr` (in "project"), `hr` (in "through"), `bi`, `ev`, `car`, `art` are substrings of common words,
so almost every CV scores in several unrelated fields. The 2026-11-08 validator run labelled the
"poor quality" sample `Teacher`.

### Experience level (`_detect_experience_level`)

Always returns one of `Fresher`, `Junior`, `Mid-Level`, `Senior`, `Unknown`. The first signal that
gives an answer wins:

1. **Stated years.** Every `N years of experience` / `N+ years of <up to two words> experience`
   in the CV; the largest N is used. "8+ years of experience" → 8.
2. **Dated ranges in the work section.** `YYYY - YYYY`, or `YYYY - present|current|now`, in the
   detected `work_experience` content (separators `-`, en/em dash or `to`). `present` is the real
   current year (`date.today().year`); ends after the current year are clipped. Overlapping ranges
   count once (years are merged, not summed). Used only if the total is above 0. A
   content-detected work section has empty content, so it never gets here.
3. **Keywords**, whole words only (a space in a keyword also matches `-`), searched in the first
   500 characters of the CV (`EXPERIENCE_KEYWORD_SCAN_CHARS`: name, title, summary). Checked
   senior first, first hit wins:
   - Senior: `senior, lead, principal, architect, manager, 6+ years, 7 years, 8 years, 10 years`
   - Mid-Level: `mid level, intermediate, 3 years, 4 years, 5 years`
   - Junior: `junior, associate, 1 year, 2 years, trainee`
   - Fresher: `fresher, fresh graduate, entry level, graduate, recent graduate, no experience`
4. A work or education section was detected but nothing above matched → `Fresher`.
   Otherwise `Unknown`.

Years map to levels in `_level_from_years`: < 1 → Fresher, ≤ 2 → Junior, ≤ 5 → Mid-Level,
otherwise Senior.

Why stated years come before ranges: the number is what the candidate claims as of writing, while
ranges ending in "Present" grow every year, so a CV written in 2023 (like the samples) reads as
older today. The samples depend on this: the marketing CV states 5 years, but `2018 - Present`
covers 8 in 2026. Limits: a skill-specific claim ("10 years of experience with Excel") counts as
total experience, and keywords further down the CV ("graduated", "associate", an early "Junior"
role) are ignored on purpose.

### Strengths (`_identify_strengths`, max 5, in this order)

- ≥ 10 skills: "Strong technical skill set"
- level in `Mid-Level`/`Senior`: "<level> professional experience"
- ≥ 7 sections: "Well-structured CV with comprehensive sections"
- each section with quality ≥ 8: "Excellent <section> section"
- field ≠ `"General"`: "Clear career focus in <field>"
- overall ≥ 80: "Overall excellent CV quality"

### Weaknesses (`_identify_weaknesses`, max 5)

- "Missing <section> section" for each of summary, education, work experience, skills not detected
- < 5 skills: "Limited skills listed"
- Fresher: "Limited or no work experience"
- each detected section with quality < 4: "Weak <section> section needs improvement"
- overall < 50: "Overall CV needs significant improvement"

### Recommendations (`_generate_recommendations`, max 7)

- No summary / no skills / no projects section → one line each.
- Field `"Software Development"`: Git and Docker/Kubernetes tips. **Dead code**: no field has that
  name (the closest is `Information Technology`).
- Field `Data Science`: Python tip if `python` missing; ML tip if neither `machine learning` nor
  `deep learning` found.
- < 10 skills: "Consider adding more relevant technical skills".
- Fresher: highlight projects/internships.
- Always: "Use action verbs..." and "Quantify achievements...". Every CV gets these two.

### Learning suggestions (`_generate_youtube_suggestions`, max 5)

Each item is `{title, query, video_id, reason}`. In order:
1. Up to 2 hard-coded entries for the field, if the field is one of the 18 with a list.
2. < 5 skills: "Top Skills for <field> in 2024".
3. Always: "How to Write a <field> CV/Resume".
4. Fresher: "Entry Level <field> Career Guide".
5. Always: "<field> Interview Preparation".

The results page links to a YouTube **search** for `query`; `video_id` is used only for the
thumbnail. The IDs are hard-coded, the generic ones are reused for every field, and at least one is
not a YouTube ID (`'197472099'` for QuickBooks).

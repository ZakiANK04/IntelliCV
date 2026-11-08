# Scoring

All of it is `NLPAnalyzer._calculate_scores` in `app/services/nlp_analyzer.py`. The weights in
`config.SCORING_WEIGHTS` are **not used**; the method has its own copy. Inputs come from the steps in
[analysis-pipeline.md](analysis-pipeline.md).

```
overall = 0.25·experience + 0.25·skills + 0.20·structure + 0.15·career + 0.15·readability
```

Each sub-score is 0–100. `CVAnalyzerService` rounds every value to 2 decimals before storing.

## Experience (25%)

```
base = {Fresher: 40, Junior: 60, Mid-Level: 80, Senior: 100}.get(level, 30)
if work_experience detected:
    experience = min(100, base + 3 × work_experience.quality_score)
else:
    experience = base
```

`_detect_experience_level` only returns these four labels or `Unknown`, which gets 30. A header-detected work section adds up to 30; a content-detected one
adds 20 or 30 (its quality is 6.67 or 10).

## Skills (25%)

```
skills = min(100, 8 × len(skills_found))
skills = min(100, skills + 5 × number_of_categories_hit)
```

A skill's category is the first category in `SKILLS_DATABASE` that lists it. 13 skills already give
100 before the category bonus; any CV that lists a dozen technologies or soft skills maxes this out.

## Structure (20%)

```
n = sections detected (0–9)
structure = min(100, 12 × n)
structure = min(100, structure + 2 × mean(quality_score of detected sections))
```

## Career alignment (15%)

```
if career_field == "General":
    career = 50
else:
    keywords = job_titles + primary + secondary of CAREER_FIELDS[career_field]
    career = min(100, 70 + 5 × (extracted skills that equal one of those keywords))
```

Matching is exact on the skill text (`python` matches the `python` entry, not `r programming`).
Six matching skills reach the cap; 4 of the 7 samples score 100 here. `General` is rare in
practice because career-field detection uses substring matching (see
[known-issues.md](known-issues.md)), so most CVs start at 70.

## Readability (15%)

```
words = len(text.split())
readability = 80 if 300 ≤ words ≤ 800
            = 60 if 200 ≤ words ≤ 1000
            = 40 if words < 200
            = 50 otherwise (> 1000)
if lines starting with optional spaces then • - or * ≥ 5:
    readability = min(100, readability + 15)
```

The sentence count is computed and never used. Bullets are counted after cleaning, which maps most
Unicode bullets to `•`.

## What the score range looks like in practice

From the 2026-11-08 validator run on the seven sample CVs (raw text, no PDF step), after the
experience-level and career-score fixes:

| Sample | Level | Exp | Career | Overall |
|---|---|---|---|---|
| senior_software_engineer | Senior | 100 | 100 | 98.48 |
| entry_level_data_scientist | Fresher | 40 | 100 | 75.53 |
| mid_level_marketing | Mid-Level | 100 | 75 | 89.17 |
| healthcare_nurse | Senior | 100 | 90 | 92.60 |
| poor_quality | Junior | 69 | 70 | 44.55 |
| ml_engineer | Mid-Level | 100 | 100 | 96.12 |
| accountant | Senior | 100 | 100 | 90.81 |

Running each sample through `PDFExtractor._clean_and_normalize` first gives the same scores.
Before the fixes the same run gave 90.0, 71.0, 76.9, 84.6, 44.5, 80.1 and 82.3: career was a
constant 70 and the marketing and ML CVs got an experience base of 30 (`Mid Level`). Good CVs now
sit between 89 and 99, so the score separates weak from good CVs better than good from excellent.

## Floor and ceiling

- Text under 50 characters: everything 0, overall 0.
- Smallest realistic score for real text: experience 30, skills 0, structure 0, career 50
  (`General`), readability 40 → 0.25·30 + 0.15·50 + 0.15·40 = **21** (24 with any detected field,
  which is the usual case).
- Ceiling: experience 100, skills 100, structure 100, career 100, readability 95 (80 + 15 for
  bullets). That is 25 + 25 + 20 + 15 + 14.25 = **99.25**. No CV can reach 100, because
  readability tops out at 95.

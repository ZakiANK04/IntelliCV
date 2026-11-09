# IntelliCV

IntelliCV analyses CVs with natural language processing, explains what makes them strong or weak,
helps job seekers write better ones, and helps recruiters rank a batch of CVs against a role.

## People

**Job Seeker**:
A person improving their own CV. May use the app anonymously or with an account.
_Avoid_: Candidate (when they are acting for themselves), visitor, user

**Recruiter**:
A person with an account who ranks other people's CVs against a Role.
_Avoid_: HR, employer, admin

**Candidate**:
The person a CV belongs to, as seen from a Recruiter's Batch.
_Avoid_: Applicant, Job Seeker

**Operator**:
Whoever runs the IntelliCV instance and uses the admin tools.
_Avoid_: Admin (as a person), owner

## Analysis

**CV**:
One résumé document, uploaded as a file or written in the Builder.
_Avoid_: Résumé, submission, upload

**Analysis**:
The result of running IntelliCV on one CV: its Quality Score, any Fit Score, detected structure, skills, Career Field, and Advice.
_Avoid_: Report, evaluation, CVAnalysis (that is a table)

**Quality Score**:
How well a CV is written and structured, independent of any job. Every Analysis has one.
_Avoid_: Overall score, CV score

**Fit Score**:
How well a CV matches a Target. Exists only when a Target was given.
_Avoid_: Match score, ATS score, career alignment

**Target**:
What a CV is measured against for a Fit Score: a chosen Career Field or a pasted job description.
_Avoid_: Goal, job

**Evaluative Measure**:
One named, explainable check that contributes to a Quality Score or Fit Score.
_Avoid_: Metric, factor, sub-score (a sub-score may group several measures)

**Career Field**:
A category in IntelliCV's occupation taxonomy, grouping related occupations, that a CV can be classified into or targeted at. An Analysis has one primary Career Field and up to two secondary ones. Being classified into a Career Field never makes it the Target.
_Avoid_: Career category, domain, industry, job title

**General**:
The Career Field an Analysis gets when no real Career Field fits. It is never a secondary field and never a Target.
_Avoid_: Other, unknown, uncategorised

**Advice**:
Strengths, weaknesses and recommendations attached to an Analysis, written in the UI Language.
_Avoid_: Feedback, suggestions, tips

## Languages

**CV Language**:
The language a CV is written in. One of the Supported Languages.
_Avoid_: Locale, document language

**UI Language**:
The language the app's interface and Advice are shown in, chosen by the person using it.
_Avoid_: Locale, display language

**Supported Language**:
A CV Language that has passed its own validation set. Launch set: English, French, Arabic, Spanish, German, Japanese, Chinese.
_Avoid_: Available language

**Language Pack**:
The per-language rules a Supported Language needs beyond the shared multilingual models, such as heading names and date formats.
_Avoid_: Locale file, translation

## Builder

**Builder**:
The guided editor where a Job Seeker writes or fixes a CV, starting blank or from an uploaded CV.
_Avoid_: CV maker, generator, editor

**Draft**:
A CV being worked on in the Builder. Kept in the browser when anonymous, saved to the account otherwise.
_Avoid_: Document, work in progress

**Template**:
A visual layout a Draft is exported with, to PDF or DOCX.
_Avoid_: Theme, design

## Recruiting

**Role**:
A position a Recruiter is hiring for, defined by a job description or a Career Field. A Role is the Target for its Batch.
_Avoid_: Job, vacancy, opening, posting

**Batch**:
The set of CVs a Recruiter uploads to one Role.
_Avoid_: Bulk upload, pool

**Shortlist**:
A Batch's CVs ordered by Fit Score, with the reasoning for each.
_Avoid_: Ranking, leaderboard

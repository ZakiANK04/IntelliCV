# Multilingual CV datasets for validating each Supported Language

Research for issue #10 (map: #2). Done 2026-11-08. Sources are dataset cards, papers and licence pages, read but not downloaded. Anything a source did not state is marked "not stated"; none of it was guessed.

Short answer: public CV corpora are almost all English, plus one Chinese set. No public CV corpus with section, NER or occupation labels was found for fr, ar, es, de or ja. Those languages have public data only for adjacent text (job ads, job titles, ESCO mappings). Most of the English CV data is scraped from sample-resume sites with unclear licences. Each non-English Supported Language will need a validation set that the project builds itself.

## Vocabulary used here

CV Language, Supported Language and Career Field follow `GLOSSARY.md`. "Real personal data" means the card or paper indicates real people's details are present, or fails to rule it out.

## Tables per language

Columns: dataset, size, labels, licence, real personal data, link.

### en (CV Language)

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| Kaggle Resume Dataset (snehaanbhawal) | 2,484 resumes (mirror listing) | 24 job categories | Not verified (Kaggle page not read; mirror does not state) | Scraped from livecareer.com resume examples; likely sample resumes, not stated | [mirror](https://baselight.app/u/kaggle/dataset/snehaanbhawal_resume_dataset) |
| ResumeAtlas / `ahmedheakl/resume-atlas` | 13,389 records (9,640 train, 1,071 val, 2,677 test) | 43 categories | MIT on the HF card; the paper does not state a dataset licence | Scraped from Google Images (3,015), Bing Images (2,722) and LiveCareer (7,652), OCR'd. Paper says resumes "may contain" names, phones and emails and does not say they were removed; GDPR mentioned only as a complication | [card](https://huggingface.co/datasets/ahmedheakl/resume-atlas), [paper](https://arxiv.org/html/2406.18125v1) |
| `datasetmaster/resumes` | 4,817 rows | Nested JSON sections (personal information, experience, education, skills, projects); tagged for token classification; field-level label definitions not stated | MIT | Mixed. Card says real resumes were anonymised and the rest were generated with Faker | [card](https://huggingface.co/datasets/datasetmaster/resumes) |
| `Mehyaar/Annotated_NER_PDF_Resumes` | 5,029 CVs | IT skill spans (single label SKILL) | MIT | Not stated; example text contains a name, employer and university, so assume yes | [card](https://huggingface.co/datasets/Mehyaar/Annotated_NER_PDF_Resumes) |
| CareerCorpus (Mendeley) | 302 resumes in 6 categories | Category plus two expert annotation scores per resume | CC BY 4.0 | Anonymised (names, emails, phones replaced); verification not described. Five categories come from the Kaggle LiveCareer set, one from public LinkedIn profiles | [record](https://data.mendeley.com/datasets/wzzwn37gmd/1) |
| Green, Maynard and Lin 2022 (job descriptions, not CVs) | 18.6k entities | Skill, Qualification, Experience, Occupation, Domain | Paper is CC BY-NC 4.0; dataset licence not confirmed | Job ads; no candidate data | [paper](https://aclanthology.org/2022.lrec-1.128) |

Not verified: the DataTurks "Resume Entities for NER" Kaggle set, often used for spaCy resume NER. The Kaggle page was not read, so no size or licence is claimed ([pointer](https://awesome.ecosyste.ms/projects/github.com%2Ffaisalahmedbijoy%2Fnamed-entity-recognition-spacy)).

### fr

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| No public French CV corpus found | | | | | |
| Résumé parsing corpora (arXiv 2309.07015, 7 languages incl. fr) | Not stated | Hierarchical sequence labelling for résumé parsing | Paper is CC BY-NC-SA 4.0; corpus release not stated | Not stated | [paper](https://arxiv.org/abs/2309.07015) |
| SegCV (TALN 2013) | 100 commercial-domain CVs | Section segmentation | Not stated | Not stated | cited in a [search result](https://research.ou.nl/en/publications/how-adequate-is-your-cv-analyzing-french-cvs-with-readerbench/); original not read, public status unconfirmed |

### ar

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| No public Arabic CV corpus found | | | | | |
| JobArabi (job announcements, not CVs) | 20,528 posts from X, Jan 2024 to Oct 2025 | No annotation scheme described | Not stated; release announced as "will be released" | Public account posts with metadata and geolocation; handling not discussed | [paper](https://arxiv.org/abs/2605.20960) |

An ICALP 2024 paper on Arabic CV classification exists; whether its data is released was not checked.

### es

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| TalentCLEF 2026 Task A | Dev: 10 job descriptions and 472 résumés per language (en, es); full data not yet released | Binary job-résumé relevance by human experts | CC BY 4.0 on the Zenodo sample record | Synthetic. Generated from structured data derived from real job descriptions and CVs; the Spanish side is an LLM translation of the English, checked by reviewers | [corpus page](https://talentclef.github.io/talentclef/docs/talentclef-2026/data/description_corpus), [Zenodo sample](https://zenodo.org/records/17625332) |
| Engineering job ads corpus (Peru, job ads not CVs) | 800 job ads | POS tags and BIO entity labels | CC BY 4.0 | Job ads | [B2FIND](https://b2find.eudat.eu/dataset/0a8bbeda-1a3c-56f0-8d70-f9481a2e96d4) |
| Résumé parsing corpora (arXiv 2309.07015) | Not stated | See fr | See fr | Not stated | [paper](https://arxiv.org/abs/2309.07015) |

### de

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| No public German CV corpus found | | | | | |
| Gnehm et al. 2022 (`jjzha/gnehm`, job ads) | 24,778 sentences (19,889 train, 2,332 dev, 2,557 test) | Token tags B-ICT, I-ICT, O (ICT skills) | CC BY-NC-SA 4.0 | Job ads from the Swiss Job Market Monitor | [card](https://huggingface.co/datasets/jjzha/gnehm) |
| GOJA (job ads) | 500 ads, manually annotated | Roles, tools, experience levels, attitudes | Not checked | Job ads | cited in a [search result](https://aclanthology.org/anthology-files/pdf/emnlp/2025.emnlp-main.1375.pdf); not read directly |
| Résumé parsing corpora (arXiv 2309.07015) | Not stated | See fr | See fr | Not stated | [paper](https://arxiv.org/abs/2309.07015) |

### ja

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| No public Japanese CV (rirekisho or shokumu keirekisho) corpus found | | | | | |

Searches in English and Japanese returned only writing guides and template generators. TalentCLEF does not cover Japanese. Public Japanese job-ad or skill datasets were not found either, though the search was not exhaustive (Japanese NLP corpora hosted on Japanese sites such as the Association for NLP proceedings may have leads).

### zh

| Dataset | Size | Labels | Licence | Real personal data | Link |
|---|---|---|---|---|---|
| Resume NER (Zhang and Yang 2018), mirrored as `PassbyGrocer/resume-ner` | 4,761 rows: 3.82k train, 463 val, 477 test | Integer tags 0 to 16; meaning not documented on the HF card. Repo calls it NER on resumes | HF card: Apache-2.0. Original repo (jiesutd/LatticeLSTM): no licence shown | Yes in practice. Crawled from Sina Finance, covering senior executives of listed companies; preview shows names, birth dates, education, employment. No anonymisation or consent described | [HF card](https://huggingface.co/datasets/PassbyGrocer/resume-ner), [repo](https://github.com/jiesutd/LatticeLSTM) |
| Chinese-SkillSpan (job ads) | 20,000+ instances from four recruitment platforms, 2014 to 2025 | ESCO-aligned spans: knowledge, skill, transversal competence, language competence | Dataset licence not stated | Job ads | [paper](https://arxiv.org/abs/2604.23009), data via the authors' [site](https://sites.google.com/view/cn-skillspan-resources) |
| TalentCLEF 2025 Task A (job titles) | Per-split counts not stated on the page read | Job-title matching linked to ESCO ids and ISCO families; validation relevance binary | Dataset licence not stated (site is CC BY 4.0) | No. Data "inherently excludes any personal information" | [corpus page](https://talentclef.github.io/talentclef/docs/talentclef-2025/data/description_corpus) |

Chinese is available only at the validation split in TalentCLEF 2025 (no Chinese training data).

## Occupation taxonomy and job-title resources (for Career Field)

These do not label CVs. They matter for checking Career Field classification.

| Resource | Coverage | Licence | Link |
|---|---|---|---|
| ESCO v1.2.1 | 28 languages including en, fr, de, es, ar. Japanese and Chinese are not listed | Licence not stated on the download page; download needs an email address and acceptance of a privacy statement. Check terms before shipping the taxonomy | [download](https://esco.ec.europa.eu/en/use-esco/download) |
| O*NET 31.0 | English; Spanish resources on a separate page | CC BY 4.0 with attribution rules | [licence](https://www.onetcenter.org/license_db.html) |
| MELO benchmark | 48 datasets, 21 languages, occupation mentions linked to ESCO via existing human crosswalks (e.g. national terminologies) | Code MIT; data licence not stated; data on Zenodo (10.5281/zenodo.13830967) | [repo](https://github.com/Avature/melo-benchmark), [paper](https://arxiv.org/abs/2410.08319) |
| TalentCLEF 2025 Task A | en, es, de training and test; en, es, de, zh validation | See zh | see above |

ESCO does not cover ja or zh, so the Career Field taxonomy for those two languages needs another source (O*NET Japan or Chinese occupation classifications were not researched).

## Coverage gaps by language

| Language | CV corpus with labels | Job-ad or title data | Taxonomy |
|---|---|---|---|
| en | Yes, several, but mostly scraped sample resumes with weak licences | Yes | ESCO, O*NET |
| fr | None found | None found | ESCO |
| ar | None found | Job-ad posts, unlabelled, unreleased | ESCO |
| es | Synthetic only (TalentCLEF 2026, relevance labels, not NER) | Peru engineering ads | ESCO |
| de | None found | Gnehm (ICT skills, non-commercial licence), GOJA | ESCO |
| ja | None found | None found | Not in ESCO |
| zh | Resume NER (executive biographies, one narrow genre) | Chinese-SkillSpan | Not in ESCO |

Further gaps that apply to every language:

- No source offers labelled CV sections, labelled NER and labelled Career Field on the same documents. Even English sets offer one label type each.
- No public set covers scanned or photographed CVs, which the map lists as an input.
- RTL layout (ar) and the Japanese rirekisho form have no public test material.
- The seven-language résumé parsing corpora (en, fr, zh, es, de, pt, sv) would cover four of the seven languages, but the paper does not say they are released. Worth contacting the authors.

## Synthetic CV generation as a fallback

Existing practice:

- TalentCLEF 2026 builds résumés synthetically from structured data derived from real job descriptions and CVs, generates English first, reviews by hand, and produces Spanish by LLM translation checked by humans ([corpus page](https://talentclef.github.io/talentclef/docs/talentclef-2026/data/description_corpus)).
- `datasetmaster/resumes` mixes anonymised real CVs with Faker-generated ones ([card](https://huggingface.co/datasets/datasetmaster/resumes)).

What it is good for:

- Privacy. No real person's data, which matters under the map's GDPR-grade standing decision.
- Controlled coverage. Gold labels come free if the generator writes the label with the text: section boundaries, skills, titles, and a Career Field assigned from the ESCO occupation used as the seed.
- Layout and format stress tests per language: date formats, name order, RTL, rirekisho structure, DOCX and PDF rendering.
- Regression suites that catch breakage after changes, in all seven languages.

Validity limits:

- Maheshwari et al. found LLM-generated benchmarks track real-data performance for simple tasks such as intent classification but "fall short" for named entity recognition, and that smaller generator models favour their own output ([paper](https://arxiv.org/abs/2409.11968)). Section detection and skills extraction are NER-like, so this applies.
- If the analyser's models and the generator share a model family or training data, scores will read high. The paper recommends generating with several larger models.
- Generated CVs are more regular than real ones: tidy headings, complete sentences, standard section names. Real CVs have broken PDF text order, tables, columns, mixed languages and missing sections. The point of validation is those cases.
- Translated CVs (as in the Spanish TalentCLEF side) carry translationese and the source country's conventions, not native CV style (for example a German Lebenslauf with a photo and personal details block, or a Japanese rirekisho).
- Labels derived from the seed occupation are only as valid as the seed; ESCO titles are cleaner than what people write.
- A language that passes only on synthetic data has not shown it handles real CVs. This should not count as "validated" in the sense the map uses, or the Supported Language gate should say which set it passed.
- Not found: a study measuring the synthetic-to-real gap on CV tasks specifically. The evidence above is from NER and intent benchmarks generally.

Assessment: synthetic CVs are a sound fallback for regression and format coverage in all seven languages, and a weak substitute for a real held-out set. The sound design is a small real set per language (a few dozen CVs, consented or donated, or hand-written by native speakers as realistic personas) used as the pass or fail gate, with synthetic volume used for regression and edge-case coverage.

## Sources

Primary, read directly:

- [ResumeAtlas dataset card](https://huggingface.co/datasets/ahmedheakl/resume-atlas) and [paper](https://arxiv.org/html/2406.18125v1)
- [datasetmaster/resumes](https://huggingface.co/datasets/datasetmaster/resumes)
- [Mehyaar/Annotated_NER_PDF_Resumes](https://huggingface.co/datasets/Mehyaar/Annotated_NER_PDF_Resumes)
- [PassbyGrocer/resume-ner](https://huggingface.co/datasets/PassbyGrocer/resume-ner) and [LatticeLSTM repo](https://github.com/jiesutd/LatticeLSTM)
- [CareerCorpus on Mendeley Data](https://data.mendeley.com/datasets/wzzwn37gmd/1)
- [jjzha/gnehm](https://huggingface.co/datasets/jjzha/gnehm)
- [TalentCLEF 2025 data](https://talentclef.github.io/talentclef/docs/talentclef-2025/data/description_corpus), [2026 data](https://talentclef.github.io/talentclef/docs/talentclef-2026/data/description_corpus), [2026 Zenodo sample](https://zenodo.org/records/17625332), [2025 overview paper](https://arxiv.org/abs/2507.13275)
- [MELO repo](https://github.com/Avature/melo-benchmark)
- [Chinese-SkillSpan](https://arxiv.org/abs/2604.23009), [JobArabi](https://arxiv.org/abs/2605.20960), [Résumé parsing as hierarchical sequence labelling](https://arxiv.org/abs/2309.07015)
- [ESCO download page](https://esco.ec.europa.eu/en/use-esco/download), [O*NET licence](https://www.onetcenter.org/license_db.html)
- [Efficacy of Synthetic Data as a Benchmark](https://arxiv.org/abs/2409.11968)

Read through search summaries only (not opened directly): Kaggle Resume Dataset mirror, Green et al. LREC 2022, Engineering job ads corpus on B2FIND, GOJA, SegCV, the ICALP 2024 Arabic CV paper.

## Open questions

1. Are the seven-language résumé parsing corpora (arXiv 2309.07015) released, and under what terms? One email to the authors answers it. If yes, fr, es, de and zh get a real labelled set.
2. What are the tag meanings and original licence of the Chinese Resume NER set? The Hugging Face card documents neither, and the data is real executive biography text, so check the data-protection position before shipping it in a repo.
3. What are the terms of the ESCO download, and does the ESCO licence permit redistribution inside a Language Pack? Not stated on the page read.
4. Which occupation taxonomy covers ja and zh for Career Field? ESCO does not list either language.
5. Is there any Japanese job-ad or CV dataset on Japanese-language sites? The search found none; a native-language search of NLP society proceedings was not done.
6. The Kaggle and DataTurks English sets were not read at source; confirm licences before any use beyond local testing.
7. How many real CVs per language are enough for a pass or fail gate? This belongs to #17.

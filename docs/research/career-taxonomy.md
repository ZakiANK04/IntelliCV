# Which occupation and skills taxonomy should Career Fields come from?

Research for issue #6 (map #2). Researched 2026-11-08. Figures come from the cited pages; where a page did not state a figure, this document says so.

## Short answer

No single taxonomy covers all 7 CV Languages. ESCO covers five of them (en, fr, ar, es, de) with occupations, skills and occupation-skill links, free to reuse with attribution. It has no ja or zh labels. O*NET is English only (plus a Spanish resources page), CC BY 4.0, and has the richest per-occupation skill data. ISCO-08 is the language-neutral backbone that the others map to. Japan and China each publish their own national classification, which can be mapped to ISCO-08 to reach ja and zh.

Recommendation: use ISCO-08 codes as the stable key for Career Fields, ESCO as the multilingual label and skill source for five languages, and the Japanese and Chinese national classifications for ja and zh occupation labels. Treat O*NET as optional English enrichment. Details below.

## Comparison

| | ESCO v1.2.1 | O*NET 31.0 | ISCO-08 | Japan JSOC (2009) | China CNOC (2022) | Lightcast Open Skills |
|---|---|---|---|---|---|---|
| Occupations | 3,039 (v1.2 launch deck) | 1,016 O*NET-SOC rows | 436 unit groups | 329 unit groups | 1,639 occupations | Job titles: 75,000+ per Lightcast docs; not a classification of occupations |
| Hierarchy | ISCO-08 supplies the top four levels; ESCO occupations sit at level 5 and below | O*NET-SOC taxonomy (2019 version), SOC-based | 4 levels: 10 major, 43 sub-major, 130 minor, 436 unit groups | 3 levels: 12 major, 74 minor, 329 unit | 8 major categories; the 2015 edition had 75 classes and 434 subclasses (2022 sub-level counts not found) | Flat skills list |
| Skills linked to occupations | Yes. 13,939 skill/competence/knowledge concepts, with occupation-skill relations. Counts of essential vs optional relations not found | Yes, rich descriptors (Content Model Reference has 3,006 elements; per-occupation skills, knowledge, tasks, technology) | No | No | No | Skills only, no occupation hierarchy |
| Languages | 28, including en, fr, ar, es, de. No ja, zh | English. Spanish resources page exists; the database language for other locales is not stated | Official publication languages not verified here | Japanese and English pages on the MIC site | Chinese; English coverage not verified | English; language support not found in sources |
| Licence | Free reuse for any purpose under Commission Decision 2011/833/EU, with acknowledgement and "adapted" labelling for changes | CC BY 4.0 with attribution; "O*NET" is a trademark | Copyright terms not confirmed in sources | "All Rights Reserved" footer on the MIC page; no reuse terms found | Not found | Taxonomy described as open, but API free access limited to approved nonprofits; commercial use needs a licence |
| Format | CSV, RDF, TTL, ODS, XML, JSON-LD; web API and downloadable Local API (Docker) | Excel, CSV, JSON, SQL dumps, RDF, web services API | Published tables; ILO and UN Statistics Division pages | PDF and web tables | Published dictionary; machine-readable form not found | API (contract-based) |
| Update cadence | Minor releases (v1.2.1 on 2025-12-10); major versions every few years (v1.2 in 2024) | Quarterly, main update in Q3 each year | ISCO-08 is from 2008; revision in progress, revised version to be presented at the 22nd ICLS in 2028 (UN meeting slides) | Last revision December 2009 | 2015 then 2022 | Continuous |

## Findings by candidate

### ESCO

- v1.2.1 is current (last updated 2025-12-10, part of portal release v6.2.0). ESCO v1.2 has 3,039 occupations and 13,939 skills-competences/knowledge concepts and is published in 28 languages (launch deck). The 28 include Arabic and all official EU languages. Japanese and Chinese are not among them.
- Downloads are available in all 28 languages, in RDF, TTL, ODS, CSV, XML and JSON-LD, after accepting a privacy statement and giving an email address. A Local API can run on our own server, which suits a local-only NLP design.
- Each occupation carries preferred and alternative labels per language, which supply synonyms. I did not measure label counts per language.
- Reuse: ESCO help text states the classification may be used and reused for any purpose and by any party free of charge, with a required acknowledgement statement and a clear mark on adapted versions. I did not find the exact wording of the acknowledgement; copy it from the ESCO portal when implementing.
- The skills pillar has its own hierarchy (added to the API in v1.0.5; third level revised in v1.1).

### O*NET

- O*NET 31.0, CC BY 4.0. 1,016 occupation rows (208 updated in 31.0), quarterly updates.
- The best source of per-occupation skills, knowledge, tasks and technology, but English only and US-centred. Useful as an English enrichment layer, not as the multilingual spine.
- Attribution must name the release version and include the trademark line.

### ISCO-08

- 10 major, 43 sub-major, 130 minor, 436 unit groups. Occupations only, no skills.
- Its value is the common code: ESCO is built on it, and O*NET-SOC, JSOC and CNOC can be mapped to it.
- A revision is under way. The 21st ICLS (2023) received a progress report; UN slides say the revised ISCO is to be presented at the 22nd ICLS in 2028, aimed at the 2030 census round. Proposed changes include code changes, title changes and new unit, minor and sub-major groups. We should key on a code table version and expect a later remap.

### Japan

- The Japan Standard Occupational Classification (MIC, 5th revision, December 2009): 12 major, 74 minor, 329 unit groups. English and Japanese pages exist.
- The Ministry of Health, Labour and Welfare runs "job tag", which describes more than 500 occupations by job, task and skill. A bulk-download option and its reuse terms were not found; check the site's terms before any use.
- No machine-readable skills list with free reuse was located for Japan.

### China

- The 2022 edition of the national occupation classification dictionary (MOHRSS, published 2022-09-28): 1,639 occupations, 8 major categories, 97 flagged digital occupations and 134 green occupations.
- Licence and a downloadable machine-readable file were not found. Skill links were not found.

### Lightcast Open Skills

- 33,000+ skills (developer docs) or 35,000+ (marketing pages). Free API access is limited to approved nonprofit use; production use needs a commercial licence. Language support was not found. Not suitable as a dependency.

## Crosswalks

- SOC to ISCO-08: US BLS publishes a SOC-to-ISCO-08 concordance (cited by the IBS study; I did not open the BLS page). IBS (Poland) published O*NET-SOC to ISCO-08 files at 4-digit level. These are many-to-many and approximate.
- ESCO to O*NET: a secondary source describes an ESCO-to-O*NET-SOC mapping of 3,349 ESCO occupations to 958 O*NET occupations, not 1:1. The official source was not located.
- JSOC to ISCO-08 and CNOC to ISCO-08: official crosswalks were not found in this pass.

## Recommendation

1. Key Career Fields to ISCO-08 codes (sub-major or minor group level), not to a hand-written list. The 32 current fields are finer than the 10 major groups and coarser than 436 unit groups, so a curated grouping of minor groups (130 total) is the likely fit. That grouping is a product decision for #15.
2. Pull occupation labels, synonyms and skills for en, fr, ar, es, de from ESCO, using its ISCO links to land in the Career Fields.
3. For ja and zh, use JSOC and CNOC occupation titles, mapped to ISCO-08, and check job tag terms for skills. Expect ja and zh skill vocabularies to be thinner than the other five; a validation set per language will show how thin.
4. Use O*NET as optional English enrichment (skill importance, tasks), with attribution.
5. Build the Language Pack data as a local derived file from these sources. Do not call remote APIs at analysis time.

## Impact on other tickets

- #15 (Career Field taxonomy decision): the choice is no longer which taxonomy, but how to group ISCO minor groups into Career Fields, plus how to fill ja and zh gaps.
- Language Pack tickets: ESCO provides 5 of 7 languages out of the box; ja and zh need their own sourcing, which may need machine translation of ESCO labels, checked by a native reviewer.
- The existing `SKILLS_DATABASE` (640 English skills) can be re-seeded from ESCO skills; mapping effort not estimated here.

## Open questions

- Exact ESCO acknowledgement wording and licence name.
- ISCO-08 official languages and ILO copyright terms.
- JSOC and CNOC machine-readable files, reuse terms, and official ISCO crosswalks.
- Whether job tag data can be downloaded and redistributed.
- ESCO label counts and occupation-skill relation counts per language.
- Whether the ISCO revision (2028) lands before launch and how the remap is handled.

## Sources

- ESCO occupations page: https://esco.ec.europa.eu/en/classification/occupation_main
- ESCO download page: https://esco.ec.europa.eu/en/use-esco/download
- ESCO v1.2 launch deck: https://esco.ec.europa.eu/system/files/2024-05/V1.2%20Launch%20-%20ESCO%20SEC%20combined%20-%20final%20clean.pdf
- ESCO API documentation: https://ec.europa.eu/esco/api/doc/esco-api-doc.pdf
- ESCO local API quick start: https://esco.ec.europa.eu/en/publication/local-api-quick-start-guide
- ESCO FAQ (reuse): https://esco.ec.europa.eu/et/about-esco/faq
- O*NET database: https://www.onetcenter.org/database.html
- O*NET licence: https://www.onetcenter.org/license_db.html
- ILOSTAT ISCO page: https://ilostat.ilo.org/methods/concepts-and-definitions/classification-occupation/
- UN Statistics ISCO-08 revision progress 2025: https://unstats.un.org/unsd/classifications/Meetings/UNCEISC2025/Day2_Session_9b_ISCO-08_revision_progress_2025.pdf
- UN Statistics ISCO-08 classification detail: https://unstats.un.org/unsd/classifications/Family/Detail/1067/
- Japan MIC occupational classification: https://www.soumu.go.jp/english/dgpp_ss/seido/shokgyou/1top.htm and https://www.soumu.go.jp/english/dgpp_ss/seido/shokgyou/co09-1.htm
- MHLW job tag: https://shigoto.mhlw.go.jp/
- China 2022 dictionary (State Council English): https://english.www.gov.cn/statecouncil/ministries/202209/30/content_WS633647bbc6d0a757729e0bb6.html
- Lightcast Open Skills: https://lightcast.io/open-skills and https://docs.lightcast.io/lightcast-api/docs/free-api-features
- IBS O*NET-SOC to ISCO crosswalk: https://ibs.org.pl/app/uploads/2016/04/onetsoc_to_isco_cws_ibs_en1.pdf
- BLS SOC crosswalks (cited by IBS, not opened): https://www.bls.gov/soc/soccrosswalks.htm
- Commission reuse notice: https://data.europa.eu/en/copyright-notice

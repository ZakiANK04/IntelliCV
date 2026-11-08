# GDPR, EU AI Act and Algerian Law 18-07 for IntelliCV

Research for wayfinder ticket #9. Written 2026-11-08. This is research, not legal advice. Check the points marked "open" with a lawyer before launch.

Vocabulary follows `GLOSSARY.md` (Job Seeker, Recruiter, Candidate, Analysis, Quality Score, Fit Score, Builder, Draft, Role, Batch, Shortlist).

## Short answer

1. **Job Seeker Analysis and Builder.** IntelliCV is the controller under the GDPR. The AI Act almost certainly does not make these flows high-risk: their intended purpose is self-improvement, not recruitment or selection of people. Obligations are ordinary GDPR hygiene plus AI literacy (AI Act Art. 4).
2. **Recruiter Batch and Shortlist.** The Recruiter is the controller of Candidate data and IntelliCV is the processor (GDPR Art. 4(7), 4(8), 28), as long as IntelliCV does not use Candidate data for its own purposes. Under the AI Act, IntelliCV is the **provider** and the Recruiter the **deployer** of a **high-risk system** (Annex III point 4(a): "analyse and filter job applications, and to evaluate candidates").
3. **The Art. 6(3) escape is closed for a Fit Score.** An Annex III system "shall always be considered to be high-risk where the AI system performs profiling of natural persons" (Art. 6(3), last subparagraph). Scoring and ranking Candidates is profiling (GDPR Art. 4(4)).
4. **Dates.** The high-risk obligations apply from **2 December 2027**, not 2 August 2026. Regulation (EU) 2026/1744 (the Digital Omnibus on AI) moved the date and is in force since 27 July 2026. AI literacy and the prohibitions already apply. GDPR and Algerian law already apply in full.
5. **Free or student status changes almost nothing.** The AI Act's definition of provider covers systems supplied "free of charge" (Art. 3(3)), and GDPR Art. 3(2)(a) applies "irrespective of whether a payment ... is required". Student status only helps with fine caps for SMEs (AI Act Art. 99(6)) and proportionality language.
6. **Algeria.** Law 18-07 (as amended by Law 25-11 of 24 July 2025) applies to an Algeria-established controller regardless of where users are. It requires prior declaration to the ANPDP (Art. 12-14) and **authorisation for any transfer of data abroad** (Art. 44). That bears directly on hosting.

## Role analysis per flow

| Flow | GDPR role | AI Act role | High-risk? |
|---|---|---|---|
| Job Seeker Analysis (anonymous or account) | IntelliCV is controller. The Job Seeker is the data subject, uploading their own CV. | IntelliCV is provider. The Job Seeker is not a deployer in a professional capacity (Art. 2(10) excludes purely personal non-professional use). | No, if the stated intended purpose is self-improvement. Annex III 4(a) covers systems "intended to be used for the recruitment or selection of natural persons". Open: see question 2. |
| Builder (Drafts, export) | IntelliCV is controller of the Draft. Drafts kept only in the browser are not processed by IntelliCV, but any server call for live scoring is processing. | Provider, same reasoning. | No. |
| Recruiter Batch, Fit Score, Shortlist | Recruiter is controller of Candidate data. IntelliCV is processor under a written contract (Art. 28(3)). The Recruiter account itself (login, billing-free usage logs) is controlled by IntelliCV. | IntelliCV is provider (develops the system and puts it into service under its own name, Art. 3(3), 3(11)). Recruiter is deployer (Art. 3(4)). | Yes. Annex III 4(a), Art. 6(2). Derogation unavailable because of profiling (Art. 6(3)). |

Role risks to manage:

- **Processor drift.** IntelliCV becomes a controller for any Candidate data it keeps for its own ends, for example training or tuning models on Batches, or showing Recruiters data from other Recruiters' Batches. Rule: Candidate CVs are used only for the Batch they were uploaded to.
- **Joint control.** IntelliCV chooses the scoring model and default retention, which are essential means. Whether that makes it a joint controller (Art. 26) rather than a processor is a judgement call that the EDPB controller/processor guidelines (07/2020) cover. Mitigation: let the Recruiter configure the Role criteria and retention, document that the Recruiter sets purposes, and ship a Data Processing Agreement.
- **Candidates are not users.** They never see IntelliCV's terms. The Recruiter owes them the Art. 13/14 notice. IntelliCV should supply a notice template.
- **Intended purpose.** Under Art. 3(12) the provider defines the intended purpose. Keeping Analysis (self-improvement) and Shortlist (recruitment) as separate documented purposes is what keeps the first outside Annex III. If the same Fit Score is sold to Recruiters, treat that engine as high-risk.

## Obligations mapped to product requirements

### GDPR (Regulation (EU) 2016/679), in force

| Obligation | Applies to | Product requirement |
|---|---|---|
| Territorial scope, Art. 3(2)(a): applies to non-EU controllers offering services to people in the EU, even free. Seven UI Languages incl. fr, de, es point to EU targeting. | All flows | Assume GDPR applies. Appoint an EU representative (Art. 27) unless the processing is occasional and low risk (Art. 27(2)(a)); a running CV service is not occasional. Alternatively, restrict launch to Algeria. |
| Principles, Art. 5(1): purpose limitation, minimisation, accuracy, storage limitation, integrity, accountability (5(2)). | All | Keep only what each flow needs. Known issue: PDFs and full text kept forever. Define a retention period per data class. |
| Lawful basis, Art. 6(1)(a)/(b)/(f) | Job Seeker, Recruiter account | Job Seeker: Art. 6(1)(b) (service the user asked for) or consent. Recruiter side: the Recruiter chooses a basis for Candidates (usually 6(1)(b) steps before a contract at the Candidate's request, or 6(1)(f)). IntelliCV records that as the Recruiter's decision. |
| Special categories, Art. 9(1): CVs can reveal health (disability), union membership, religion, ethnicity. Photos are not biometric data unless processed for unique identification (Recital 51). | All | Do not extract, infer, score or store special categories. Exclude photo, age, gender, nationality and marital status from the Fit Score. If incidental content is stored, rely on explicit consent (Art. 9(2)(a)) for Job Seekers. Never run face matching. |
| Transparency, Arts. 12-14. Art. 14(3): inform within a reasonable time and at the latest one month when data was not obtained from the data subject. | Job Seeker, Candidate | Job Seeker: plain privacy notice shown before upload, in all 7 UI Languages. Candidate: notice template for Recruiters (the Recruiter's duty, Art. 14). |
| Data subject rights, Arts. 15-21: access, rectification, erasure, restriction, portability (Art. 20, for consent or contract basis), objection. Response within one month (Art. 12(3)). | Job Seeker (direct), Candidate (via Recruiter) | Per-account self-serve: download all data (JSON plus original files), delete account and all Analyses, delete single Analysis or Draft. Anonymous users: delete link or token, no enumerable IDs. Processor must help the Recruiter answer requests (Art. 28(3)(e)): per-Candidate export and delete in a Batch. |
| Automated decisions and profiling, Art. 22. "solely automated processing ... which produces legal effects ... or similarly significantly affects". Recital 71 names "e-recruiting practices without any human intervention" as an example. | Shortlist | No automatic rejection, no hidden cut-off, no auto-sent decisions. Every Candidate in a Batch stays visible and a Recruiter action is required for any outcome. Human review must be meaningful, "not just a token gesture" and by someone with authority to change the result (WP29 guidelines WP251rev.01). See the SCHUFA note below. |
| Meaningful information about the logic, Arts. 13(2)(f), 14(2)(g), 15(1)(h) | Shortlist | Each Fit Score shows reasons (matched and missing items per Role criterion), which the map already requires. Reasons must be Candidate-readable, not just internal. |
| Data protection by design and default, Art. 25 | All | Private by default, non-guessable IDs, no public results, minimal API fields (known issues: public `/results/<id>`, public `/uploads/`). |
| Security, Art. 32 | All | Fix the known-issues list: no default secrets, no public uploads, restrictive CORS, rate limits, encryption at rest and in transit, access control per Recruiter and Batch. |
| Processor contract, Art. 28(3): instructions only, confidentiality, security, sub-processors (28(2), (4)), assistance, deletion or return at end, audit. | Recruiter Batch | Ship a DPA accepted at Recruiter sign-up. List sub-processors (hosting). Delete or return Batch data on request and at end of retention. |
| Records of processing, Art. 30. The under-250 exemption (30(5)) does not apply to non-occasional processing. | All | Keep a records register, and a processor register for the Batch flow. |
| Breach notification, Arts. 33-34: authority within 72 hours, data subjects if high risk. | All | Incident runbook, breach log. Processor tells the Recruiter "without undue delay" (Art. 33(2)). |
| DPIA, Art. 35(1), 35(3)(a): required for "a systematic and extensive evaluation of personal aspects ... based on automated processing, including profiling, and on which decisions are based that produce legal effects ... or similarly significantly affect". | Shortlist | Run a DPIA before launching the Recruiter feature. The Recruiter, as controller, owes the DPIA, so IntelliCV supplies a DPIA-ready document (also feeds AI Act Art. 26(9)). Do one for the whole service as good practice. |
| DPO, Art. 37(1)(b): required if core activities involve large-scale regular and systematic monitoring or special categories at scale. | Whole service | Probably not required at student scale. Open. Algerian Law 25-11 has its own DPO rule, see below. |
| Children, Art. 8 | Job Seeker | Age-gate or state the service is for adults. |

**SCHUFA and "preparatory" scores.** In C-634/21 (7 December 2023) the Court of Justice held, per secondary summaries I could read, that a probability score produced by a scoring firm can itself be an Art. 22(1) decision when a third party "draws strongly" on it, even though the third party formally decides. A Fit Score that Recruiters follow in practice is exposed to the same reading. I did not read the judgment text; read it before relying on this. Design consequence: assume the Fit Score may count as part of an automated decision, and ship the Art. 22(3) safeguards (human intervention, a way to state a view, a way to contest) for Candidates, passed through the Recruiter.

**Pending GDPR changes.** The Commission's Digital Omnibus proposal of 19 November 2025 would amend the GDPR. Per secondary sources it was still at first reading in Parliament and Council as of autumn 2026 and is not law. Nothing in it should be relied on.

### EU AI Act (Regulation (EU) 2024/1689, as amended by Regulation (EU) 2026/1744)

| Obligation | Article | Applies to | Product requirement | In force? |
|---|---|---|---|---|
| AI literacy: measures to support literacy of staff and others operating the system; no guarantee of a specific level required | Art. 4 (replaced by the Omnibus) | Provider and deployer, any AI system | A short written note on who builds and operates IntelliCV and what they know. For Recruiters, in-product guidance on what the Fit Score does not show. | Yes, since 2 Feb 2025 (Art. 113(a)); amended text in force 27 Jul 2026 |
| Prohibited practices | Art. 5 | All | Do not infer emotions from biometric data; do not score for social or sensitive-trait inference. The Omnibus adds new bans on non-consensual intimate deepfakes (Art. 5(1)(ba), (bb)) from 2 Dec 2026, not relevant here. | Yes (2 Feb 2025) |
| Transparency for AI that interacts with people or generates content | Art. 50 | Builder, if it adds a chatbot or generative text | Local NLP with templated Advice is not generative. If a model writes CV text, mark it machine-readable (Art. 50(2)); if a chat assistant is added, disclose it (Art. 50(1)). | Yes since 2 Aug 2026; pre-existing generators get until 2 Dec 2026 (Art. 111(4) as added by the Omnibus) |
| Classification | Art. 6(2), Annex III 4(a) | Shortlist | Document the intended purpose and the classification as high-risk. Art. 6(4) assessment is only needed to claim an exemption, which is unavailable here. | From 2 Dec 2027 |
| Risk management system | Art. 9 | Provider | Written, continuous process: identify risks to Candidates (bias, language disadvantage, OCR errors, score misread as a verdict), test, mitigate, record. | 2 Dec 2027 |
| Data governance and bias testing | Art. 10 | Provider | Document training, validation and test data for every model, per Language Pack. Examine and mitigate bias (Art. 10(2)(f), (g)). The Omnibus adds Art. 4a so providers may process special categories "to the extent strictly necessary" for bias detection, with safeguards (delete once the bias is corrected). | 2 Dec 2027 (Art. 4a: 27 Jul 2026) |
| Technical documentation | Art. 11, Annex IV | Provider | Maintain a living design document (the `docs/` set is a start). Keep for 10 years (Art. 18). | 2 Dec 2027 |
| Record-keeping and logs | Art. 12, Art. 19, Art. 26(6) | Provider and deployer | Automatic event logs: model version, Role version, Batch id, who reviewed and what they decided. Keep at least six months "unless provided otherwise in ... Union law on the protection of personal data". Logs must not copy CV text, to stay consistent with GDPR minimisation. | 2 Dec 2027 |
| Instructions for use, transparency to deployers | Art. 13 | Provider | Ship a document for Recruiters: purpose, accuracy and its limits per language, known failure cases, human oversight steps. Also the input to the Recruiter's DPIA (Art. 26(9)). | 2 Dec 2027 |
| Human oversight | Art. 14, Art. 26(2) | Provider designs, deployer assigns | UI lets the reviewer see the reasons, override any rank, and stop. The text names the risk of "automation bias" (Art. 14(4)(b)), so avoid a single hero number without context. Deployer must assign competent people. | 2 Dec 2027 |
| Accuracy, robustness, cybersecurity | Art. 15 | Provider | Declare accuracy per Supported Language from its validation set. Test against prompt-like or keyword-stuffing CVs. | 2 Dec 2027 |
| Provider duties: QMS, conformity assessment (self-assessment under Annex VI for Annex III point 4), EU declaration, CE marking, EU database registration, post-market monitoring, serious incident reporting | Arts. 16, 17, 43(2), 47-49, 72, 73 | Provider | Quality management scaled to size (Art. 17(2), amended); registration in the EU database before placing on the market (Art. 49(1)). Provider outside the EU needs an **EU authorised representative** (Art. 22(1)). | 2 Dec 2027 |
| Deployer duties: use per instructions, relevant input data, monitor, keep logs, inform affected people | Art. 26(1), (4), (5), (6), (11) | Recruiter | Terms of use bind the Recruiter to these. Art. 26(11): the deployer must inform natural persons "that they are subject to the use of the high-risk AI system", so supply a Candidate notice template. | 2 Dec 2027 |
| Right to explanation | Art. 86 | Recruiter | A Candidate affected by a decision based on the output can ask the deployer for "clear and meaningful explanations of the role of the AI system". The per-criterion reasons make this answerable. | 2 Dec 2027 |
| Fundamental rights impact assessment | Art. 27 | Public-law deployers and private entities providing public services | Not required for a private-sector Recruiter. Required for a public body Recruiter (for example a public employer). The Omnibus lets it cross-reference the DPIA (Art. 27(4)). | 2 Dec 2027 |
| Penalties | Art. 99 | All | Up to EUR 15 million or 3% of turnover for provider and deployer breaches (99(4)); up to EUR 35 million or 7% for Art. 5. For SMEs the lower of the two amounts (99(6)); the Omnibus extends this to small mid-caps (99(6a)). | Applies with the underlying duty |

**What "AI system" covers.** Art. 3(1) defines an AI system by inference capability; rule-based logic written entirely by people is not within it (Recital 12). Regex heading detection and keyword rules alone may fall outside. NER models, embeddings and trained classifiers do infer, so a Fit Score built on them is in scope. Treat the Shortlist as an AI system.

**Guidelines.** Art. 6(5) required Commission guidelines on classification by 2 February 2026. Secondary sources report a draft published on 19 May 2026 and not yet final. I did not read it. Check the Commission's AI Act pages before the design freeze.

### Algerian Law 18-07 of 10 June 2018, amended by Law 25-11 of 24 July 2025

Sources: JORA No. 34 of 10 June 2018 (Law 18-07) and JORA No. 48 of 24 July 2025 (Law 25-11). I read the French text.

| Topic | Provision | Product requirement |
|---|---|---|
| Scope | Art. 4: applies to a controller established in Algeria, or one using automated or other means located in Algeria. Art. 6(1): personal or domestic use is excluded. | An Algiers-based operator is covered even for EU users. EU-resident processing also triggers the GDPR. Both apply in parallel. |
| Consent | Art. 7: processing needs the data subject's express consent, with exceptions including contract performance and pre-contractual steps, legitimate interest, legal obligation (same article). Consent can be withdrawn at any time. | Consent gate plus withdrawal in the UI. Contract and legitimate-interest exceptions help the Recruiter flow. |
| Quality and retention | Art. 9: lawful and fair, specific purposes, adequate and not excessive, accurate, kept no longer than necessary. | Same retention policy as GDPR. |
| Sensitive data | Art. 3 defines sensitive data (race, politics, religion, union, health). Art. 18 bans processing except express consent or listed cases. | Same rule as GDPR Art. 9: do not extract or store these. |
| Declaration | Arts. 12-14: prior declaration to the national authority (ANPDP), with a receipt within 48 hours; the controller may start on receipt. Art. 17: the authority can require prior authorisation instead if the processing is manifestly risky, decided within 10 days. | File a declaration before launch. A ranking tool for people's CVs could be pushed to authorisation. Open: ANPDP's current procedure. |
| Information | Art. 32: tell people the controller's identity, purposes and recipients, whether answers are mandatory, their rights and any transfer abroad. | Privacy notice covers these. |
| Rights | Art. 34 access; Art. 35 rectification and erasure, free of charge; Art. 36 objection for legitimate grounds. | Same self-serve tools as for GDPR. |
| Automated decisions | Former Art. 11 (no decision with legal effects based solely on automated processing that defines a profile or evaluates personality) was **repealed** by Law 25-11 Art. 7. The same text now appears only as Art. 45 bis 1 inside the new Title V bis on criminal-justice processing. | My reading: no general Algerian rule against solely automated decisions remains for commercial processing. Open: confirm with a local lawyer; the safe course is to apply GDPR Art. 22 safeguards anyway. |
| Profiling | Law 25-11 Art. 2 adds a definition of profiling that explicitly includes evaluating or predicting "rendement au travail" (work performance). | A Fit Score is profiling under Algerian law too. |
| DPO | Art. 41 bis (new): "le responsable du traitement ... désignent ... un délégué à la protection des données". No size threshold in the text. | A DPO appears to be required for every controller. For a student project this can be a named person. Open: whether regulations set thresholds. |
| Records and logbook | Art. 41 bis 2 (records of processing, controller and processor), Art. 41 bis 3 (automated logbook of processing operations, available to the authority). | Matches the AI Act logging requirement. Keep both in one design. |
| DPIA and breach | Arts. 45 bis 6 (impact study for high-risk processing using new technologies), 45 bis 8 (breach notice to the ANPDP within five days), 45 bis 10 (notify people if high risk). These sit in Title V bis, but their wording is general. | Open: whether they bind commercial controllers. Plan to follow them; they match the GDPR duties. |
| Transfers abroad | Art. 44: transfer only with ANPDP authorisation and if the destination offers adequate protection. Art. 45 derogations include the person's express consent, and contract performance or pre-contractual measures at the person's request. | If data is hosted outside Algeria (including the EU), treat each hosting choice as a transfer. For Job Seekers, express consent is available. For Candidates in a Recruiter's Batch it is weaker. Feeds the hosting ticket. |
| Security and processors | Art. 38 security measures; Art. 39 written contract with the processor, acting only on instruction. | Same DPA. |
| Penalties | Arts. 54-69: prison terms of months to five years and fines of DZD 20,000 to 1,000,000, for example Art. 55 (processing without consent, 1 to 3 years, DZD 100,000 to 300,000) and Art. 67 (unlawful transfer abroad, 1 to 5 years, DZD 500,000 to 1,000,000). | Criminal exposure is personal to the operator. Take it seriously even if fines are small. |

## Timeline (as of 2026-11-08)

| Date | What | Source |
|---|---|---|
| 25 May 2018 | GDPR applies | GDPR Art. 99 |
| 10 Jun 2018 | Law 18-07 published (JORA 34) | JORA |
| 2 Feb 2025 | AI Act Chapters I and II apply: AI literacy (Art. 4) and prohibitions (Art. 5) | AI Act Art. 113 |
| 24 Jul 2025 | Law 25-11 published: DPO, records, logbook, profiling definition, repeal of Art. 10-11 of Law 18-07 | JORA 48 |
| 27 Jul 2026 | Digital Omnibus on AI, Regulation (EU) 2026/1744, in force (published 24 Jul 2026, in force third day after) | OJ L, 24.7.2026 |
| 2 Aug 2026 | AI Act general date of application, including Art. 50 transparency | AI Act Art. 113; Omnibus recital |
| 2 Dec 2026 | Art. 50(2) marking for generators already on the market; new Art. 5 bans | Omnibus Art. 111(4), Art. 113 |
| **2 Dec 2027** | **High-risk obligations for Annex III systems (Arts. 6-27 provider and deployer duties, including recruitment)** | Omnibus amending Art. 113(c)(i) |
| 2 Aug 2028 | High-risk obligations for Annex I product-embedded systems | Omnibus amending Art. 113(c)(ii) |
| 2 Aug 2030 | Deadline for high-risk systems already on the market and used by public authorities | AI Act Art. 111(2) |

Already binding for IntelliCV on a launch today: GDPR, Law 18-07 and 25-11, AI Act Arts. 4, 5 and 50. Not yet binding: the high-risk chapter. A system first placed on the market after 2 Dec 2027 gets no grandfathering (Art. 111(2) protects only earlier systems, and only absent significant design changes). A system launched earlier and then substantially redesigned is also caught.

## Does a free or student deployment change anything?

- **AI Act.** No exemption. Provider and deployer definitions include "free of charge" supply (Art. 3(3)). The scientific research exclusion (Art. 2(6)) covers systems developed "for the sole purpose of scientific research and development", which a public service does not meet. The pre-market testing exclusion (Art. 2(8)) ends at launch. What does apply is proportionality: Art. 99(6) caps SME fines at the lower amount, and the Omnibus makes the quality management system proportionate to size (Art. 17(2) as amended) and widens SME treatment to small mid-caps. A student project with no legal entity is still an "operator".
- **GDPR.** No exemption for free services (Art. 3(2)(a)). The Art. 30(5) records exemption does not help because the processing is not occasional. The household exemption (Art. 2(2)(c)) covers individuals, not a published service.
- **Law 18-07.** No size or price exemption. Penalties apply to natural persons.
- **Practical effect.** The legal duties do not shrink. The cost does: self-assessment conformity (no notified body, Art. 43(2)), SME fine caps, proportional QMS.

## Product requirements, consolidated

For ticket #18 (recruiter safeguards) and the data-model and hosting tickets.

1. No auto-reject, no hidden threshold. Every Candidate in a Batch is visible; outcomes need an explicit Recruiter action, recorded.
2. Reasons per Candidate per Role criterion, readable by the Candidate if the Recruiter shares them.
3. The Fit Score never uses age, gender, nationality, photo, marital status, name, or any special category. Run bias tests per Language Pack and keep the results (AI Act Art. 10(2)(f), (g)).
4. Show the Fit Score with its limits (no unexplained single number), to counter automation bias (Art. 14(4)(b)).
5. Candidate data is used only for its Batch, never to train or tune. Written DPA, sub-processor list, per-Batch retention set by the Recruiter with a default (for example 6 months, to align with the AI Act log minimum, with deletion after).
6. Event log without CV content: who, when, what Role version, which model version, what decision.
7. Candidate notice template and rights-request tooling (export or delete one Candidate's data in a Batch).
8. Job Seekers: per-account export and delete, delete token for anonymous Analyses, no public or enumerable IDs, privacy notice and consent text in 7 UI Languages, adults only.
9. Documents to produce before launching Shortlist: instructions for use (Art. 13), technical documentation (Art. 11), risk management record (Art. 9), DPIA support pack, records of processing (GDPR Art. 30, Law 25-11 Art. 41 bis 2), ANPDP declaration, EU representative (GDPR Art. 27) and EU authorised representative (AI Act Art. 22) if offered in the EU from outside it.
10. Hosting and transfers: Algerian transfer authorisation (Law 18-07 Art. 44) if hosting outside Algeria, and GDPR transfer rules (Chapter V) if Candidate data of EU residents goes to a non-EU host. Decide hosting with both in view.

## Open questions

1. Is the Recruiter feature worth its compliance cost? The provider duties from 2 Dec 2027 (QMS, technical documentation, risk management, registration, post-market monitoring, authorised representative) are heavy for one person, though self-assessed and SME-scaled. Options: ship in Algeria only first (the AI Act applies to non-EU providers only where output is used in the Union, Art. 2(1)(c)); ship with the controls above and finish documentation before 2 Dec 2027; or cut the numeric Fit Score and show evidence side by side. The last option is uncertain: Art. 6(3)(d) ("preparatory task") is blocked by the profiling rule if the system evaluates individuals, and I could not establish where the Commission draws the line.
2. Does Job Seeker Analysis against a Target (Fit Score on the Job Seeker side) stay outside Annex III 4(a)? I reasoned yes from intended purpose; it needs confirming against the final Commission guidelines.
3. Has the Commission's high-risk classification guidance been finalised, and does it contain a recruiting example for ranking tools?
4. Does Law 25-11's DPO, DPIA and breach text (placed in a title on criminal-justice processing in places) bind commercial controllers? Needs an Algerian lawyer.
5. Does Algeria still have any general rule on solely automated decisions after the repeal of Art. 11?
6. Is the Recruiter-IntelliCV relationship cleanly controller-processor given IntelliCV chooses the model? A lawyer should review the DPA structure.
7. What is the ANPDP's current declaration procedure and does a Candidate-ranking tool trigger authorisation under Art. 17?
8. Retention default: no primary source fixes one. GDPR and Law 18-07 both say "no longer than necessary". The 6-month figure is the AI Act log minimum, not a Candidate-data rule.

## Sources

Primary, read in full or in the relevant articles:

- [Regulation (EU) 2016/679 (GDPR), EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679): Arts. 2-3, 4, 5, 6, 9, 12-22, 27, 28, 30, 33-35, 37; Recital 71.
- [Regulation (EU) 2024/1689 (AI Act), EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689): Arts. 2, 3, 6, 9-15, 16-19, 22, 25-27, 43, 47-50, 72, 86, 99, 111, 113; Annex III point 4.
- [Regulation (EU) 2026/1744 (Digital Omnibus on AI), EUR-Lex](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng): signed 8 July 2026, published 24 July 2026, in force on the third day after publication; amends AI Act Arts. 4, 4a, 5, 6, 10, 17, 27, 99, 111, 113.
- [WP29 Guidelines on Automated individual decision-making and Profiling, WP251rev.01](https://ec.europa.eu/newsroom/article29/items/612053/en): revised 6 February 2018; "meaningful" human involvement, e-recruiting example.
- [Law 18-07 of 10 June 2018, JORA No. 34](https://www.joradp.dz/FTP/JO-FRANCAIS/2018/F2018034.pdf).
- [Law 25-11 of 24 July 2025, JORA No. 48](https://www.joradp.dz/FTP/JO-FRANCAIS/2025/F2025048.pdf).

Secondary, not verified against the primary text (marked in the body):

- CJEU C-634/21 SCHUFA Holding, judgment of 7 December 2023: summaries only ([curia case page](https://curia.europa.eu/jcms/jcms/p1_4213242/en)).
- Commission draft guidelines on AI Act Art. 6 high-risk classification, reported published 19 May 2026: law-firm summaries only.
- Status of the GDPR part of the Digital Omnibus (proposal of 19 November 2025): trade-press summaries only. Check the EP Legislative Observatory, procedure 2025/0360(COD).
- Not consulted: EDPB guidelines 07/2020 on controller and processor (cited from memory as the place to check, not quoted).

This is research, not legal advice.

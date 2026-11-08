# Rust web, i18n and document-generation stack for IntelliCV

Research for issue #8 (map #2). Date: 2026-11-08. Version, release-date and download figures come from the crates.io API on that date. Feature claims come from the projects' own READMEs and docs, linked in [Sources](#sources). Anything not checked against a source is marked "not verified". Nothing here was benchmarked or prototyped.

## Short answer

- Use **Axum** for the web layer, **server-rendered HTML with HTMX and vanilla GSAP** for the UI, **Fluent** for UI strings, **Typst** for PDF export, **docx-rs** for DOCX export, **Postgres via SQLx**, and a **Postgres-backed job queue** for recruiter Batches.
- **Typst cannot write DOCX.** Its export targets are PDF, PNG, SVG, HTML and a multi-file bundle. PDF and DOCX therefore need two renderers fed from one Template data model. This is the largest design cost in the document layer and affects the Builder prototype (#19).
- A Rust WASM frontend (Leptos, Dioxus) is not needed for live scoring. If scoring rules are pure Rust, that crate can be compiled to a small WASM module and called from plain JS, or the server can answer debounced fragment requests. Which one is a latency question for #13 and #19.
- Loco is a credible shortcut (Axum, SeaORM, workers, auth, mailers in one convention-driven package) but adds an opinionated layer and is a much smaller community than Axum or Actix. It is the main alternative to hand-assembling Axum.

## Requirements that drive the choice

From map #2 and GLOSSARY.md: 7 UI Languages (en, fr, ar with right-to-left, es, de, ja, zh); Builder with live scoring and PDF and DOCX export from Templates; accounts optional for Job Seekers and required for Recruiters; Batches processed in the background; GDPR-grade privacy; one developer working with coding agents; GSAP for animation (Lenis for scroll-driven pages). The current app is a single Flask process with no queue and no background workers (`docs/architecture.md`).

## Options per layer

### 1. Web framework

| Option | Version (2026-11-08) | Maturity signals | Fit for IntelliCV |
|---|---|---|---|
| Axum | 0.8.9, updated 2026-04-14 | about 576M total and 157M recent downloads; Tokio project; still pre-1.0 | Default choice. Tower middleware ecosystem (`tower-http` 0.7.1) covers compression, tracing, CORS, rate limit layers. Extractor style is well represented in agent training data. |
| Actix Web | 4.18.2, updated 2026-11-06 | about 90M total and 13M recent downloads; stable 4.x line | Equally capable and fast. Smaller current usage than Axum; its own middleware model rather than Tower, so Tower-based crates (sessions, rate limits) do not drop in (not verified in detail). |
| Loco | 1.3.1, updated 2026-11-06 | about 743k total and 152k recent downloads | Rails-style: controllers on Axum, SeaORM entities, workers, scheduler, mailers, storage, cache. Worker modes are `BackgroundQueue` (durable, needs a queue backend), `BackgroundAsync` (in-process `tokio::spawn`, lost on crash), `ForegroundBlocking` (tests). Queue backends: Redis, Postgres, SQLite. Views via templating integration. Strong scaffolding, but you inherit its ORM and conventions. |

Other frameworks were not surveyed.

Trade-off for a solo developer with agents: Axum has the most examples and the thinnest framework surface, so agents write it reliably, but you assemble sessions, auth, jobs and migrations yourself. Loco supplies those parts, at the cost of a smaller community (an order of magnitude fewer downloads than Actix, two orders fewer than Axum) and SeaORM lock-in.

### 2. Frontend model

| Option | Notes |
|---|---|
| Server templates plus HTMX (or similar) | Rust renders HTML; the browser needs almost no framework JS. Template engines: Askama 0.16.1 (compile-time checked, about 60M downloads; `rinja` is marked deprecated on crates.io), MiniJinja 3.1.0 (runtime Jinja syntax, about 44M downloads), Tera 2.4.0, Maud 0.27.0 (macro HTML, last release 2025-02-02). `axum-htmx` 0.8.1 gives typed HTMX headers. Datastar has a Rust SDK (`datastar` 0.4.1) as an alternative to HTMX; not evaluated further. |
| Rust WASM framework: Leptos 0.8.23, Dioxus 0.7.10 | Leptos: SSR plus hydration, server functions, an islands mode where only `#[island]` code ships as WASM, so bundle size grows with interactivity, not page size. The Leptos book warns Rust-to-WASM binaries grow with generics and heavy crates and gives `opt-level = 'z'` and LTO settings. Dioxus: cross-platform (web, desktop, mobile) with a `fullstack` feature for SSR, hydration and server functions. Both put the UI in Rust, so GSAP needs wasm-bindgen or JS interop for every animated element (the workspace GSAP rule assumes DOM scripting). Both change APIs between minor versions (observation from version history, not verified). |
| TypeScript SPA on a Rust JSON API | Natural home for GSAP and Lenis, richest component and i18n tooling (ICU MessageFormat libraries), and the best agent support. Cost: two languages and toolchains, an API contract to keep in sync, a second i18n system, SEO and first paint need extra work. |

Trade-offs:
- HTMX keeps the stack in Rust templates plus a little JS. GSAP and Lenis then run as ordinary scripts on server-rendered pages, which matches the house rules directly. HTMX swaps replace DOM nodes, so animations must be re-initialised after swaps (an integration detail to test, not verified here).
- The Builder is the one screen with real client state (editing, live scoring, template preview). HTMX handles it with debounced `hx-post` fragments only if round-trip latency is acceptable; otherwise it needs a small TS or WASM island. The Builder prototype should measure this.
- Leptos and Dioxus remove the TS toolchain but add compile time and WASM size, and make GSAP awkward. Neither was benchmarked here.

### 3. i18n for 7 UI Languages including Arabic

| Option | Notes |
|---|---|
| Fluent via `fluent-bundle` 0.16.0 (last release 2025-05-22, about 24M downloads) | Message format designed for plurals, gender and per-locale grammar. The first bundle locale drives plural rules; select expressions match CLDR plural categories (`zero`, `one`, `two`, `few`, `many`, `other`), which Arabic needs. Placeables are wrapped in Unicode bidi isolation marks by default (`use_isolating`), which protects Latin names and numbers inside Arabic text. Translators work in plain `.ftl` files. |
| `fluent-templates` 0.15.1 (2026-08-05) | Loads FTL from a directory and exposes lookup to template engines. Leptos has `leptos-fluent` built on it. |
| `rust-i18n` 4.2.4 (2026-09-29, about 4.7M downloads) | Key-value style with a `t!` macro and YAML/JSON/TOML files. Simpler, but plural and grammar handling was not examined in depth. |
| ICU4X `icu` 2.4.0 (2026-10-22) | Not a message catalogue. It supplies locale data and formatters (dates, numbers, plurals, calendars, and per its README modular, pluggable locale data). Use it beside Fluent for date and number formatting. Whether its segmenter is suitable for ja and zh word segmentation was not verified. |
| Client-side i18n libraries (ICU MessageFormat) | Only relevant if the frontend is a TS SPA. |

Layout is separate from message translation. Right-to-left needs `dir="rtl"` and `lang` on the document, CSS logical properties instead of left/right, and mirrored components; GSAP animations that translate on the X axis must flip sign for RTL. Fonts for ja, zh and ar must be chosen and bundled or self-hosted. None of this is a Rust library question.

Advice text generation in 7 Languages (map "Not yet specified") is a content workflow problem; Fluent suits templated Advice strings with plural and gender variants.

### 4. PDF and DOCX export from Templates

| Option | Notes |
|---|---|
| Typst as a library: `typst` 0.15.1 (2026-07-17), `typst-pdf` 0.15.1, wrapper `typst-as-lib` 0.17.0 (2026-10-07) | Typst markup acts as the Template language. The compiler can be embedded; `typst-as-lib` gives a builder with fonts, static files and data injected into the template (`sys.inputs`). Its README says the API is not stable. PDF output is tagged by default and can target PDF/A and PDF/UA variants. `#set text(dir: rtl)` and `lang` control bidi; font fallback arrays can name a CJK or Arabic font per code-point class (`covers`), including `latin-in-cjk`. Typst's own docs say RTL output that looks wrong should be reported to them, so RTL is supported but not guaranteed flawless. Fonts must be shipped with the app; font file sizes and licences were not checked. Compile time per CV was not measured. |
| `printpdf` 0.12.8 (2026-09-05) | Low-level PDF writer. You place text and shapes yourself. Its handling of complex-script shaping (Arabic joining, bidi reordering) was not verified; likely a poor fit for multi-language Templates. |
| `genpdf` 0.2.0 | Last release 2021-06-17. Treat as unmaintained. |
| `lopdf` 0.47.0 (2026-11-04) | PDF object manipulation and parsing, not layout. Possibly relevant to document ingestion, not export. |
| `docx-rs` 0.4.22 (2026-07-21, about 3.9M downloads) | Read and write DOCX. Supports paragraphs, runs, tables, numbering, styles, images, headers and footers, hyperlinks, footnotes, comments. Its README states OOXML support "is not exhaustive". Source confirms a paragraph-level `bidi` property and an east-Asian font setting on runs. Whether run-level RTL and complex-script font settings are complete was not confirmed and needs a prototype. The crate also has a WASM and JS build. |
| `docx-rust` 0.1.11 | Smaller, less active (about 130k recent downloads versus about 791k for `docx-rs`). |

Key constraint: **Typst has no DOCX export** (formats are PDF, PNG, SVG, HTML, bundle). Options for the PDF and DOCX pair:
1. One Template data model (sections, fields, styling tokens) rendered twice: Typst for PDF, `docx-rs` for DOCX. Predictable, but every Template is implemented in two renderers and layouts will not match exactly.
2. Generate PDF through Typst and DOCX through `docx-rs` with a deliberately simpler DOCX layout (single column, standard styles).
3. Convert DOCX to PDF with an external office suite (LibreOffice headless). One layout source, but a heavy non-Rust runtime dependency; not evaluated further.

Market-specific formats (rirekisho, Europass) are Templates in the same sense; each needs both renderers.

### 5. Auth and sessions

| Piece | Option | Notes |
|---|---|---|
| Sessions | `tower-sessions` 0.15.0 (2026-02-01) with `tower-sessions-sqlx-store` 0.15.1 | Tower-layer sessions with pluggable stores; a SQLx store exists. |
| Login layer | `axum-login` 0.18.0 (2025-07-20) | Builds on `tower-sessions`; user and permission abstractions. Last release over a year before this date, so check it tracks the current Axum minor. |
| Password hashing | `argon2` 0.6.0 (RustCrypto, about 73M downloads) | Standard choice. |
| Social login | `oauth2` 5.0.0 (2025-01-21), `openidconnect` 4.1.0 (2026-10-31) | Generic OAuth2 and OIDC clients; you wire providers yourself. |
| Passkeys | `webauthn-rs` 0.6.2 (2026-10-31) | Optional passwordless path for Recruiters. |

Loco advertises auth and mailers (not verified in depth). In plain Axum, expect to build account creation, email verification, password reset and account deletion yourself. Email sending was not surveyed. Auth design belongs to the later accounts ticket; this research only shows that maintained Rust pieces exist.

Anonymous Drafts "kept in the browser" (map #2) means no server session for Job Seekers until they choose to sign up.

### 6. Database access: SQLx, SeaORM, Postgres vs SQLite

| Option | Notes |
|---|---|
| SQLx 0.9.0 (2026-05-21, about 185M downloads) | Async, raw SQL with optional compile-time query checking, Postgres, MySQL and SQLite, migrations. The SQLite driver wraps the C library. No ORM, which keeps schema and GDPR export and deletion queries explicit. |
| SeaORM 2.0.4 (2026-09-27, about 29M downloads) | ORM on SQLx, with an entity-first workflow in 2.0. Loco is built on it. More abstraction, more generated code. |
| Postgres | Multi-process and multi-host safe, row locking suited to job queues, `LISTEN/NOTIFY` (SQLx supports it per its README). Needs a server. |
| SQLite | No server, simplest single-box deploy. Single writer; web requests and background workers share one file only on one host. Fine for a prototype, riskier once recruiters upload Batches concurrently. |

Hosting is open (map #2). If hosting lands on one small VM, SQLite is viable. On a managed platform, Postgres is the easier default.

### 7. Background jobs for recruiter Batches

| Option | Version | Notes |
|---|---|---|
| `apalis` | 1.0.0 (2026-10-12, about 1.5M downloads) | Tower-based task library. Backends: Redis, PostgreSQL, SQLite, in-memory, AMQP. Retries, rate limiting, timeouts, scheduling, optional web UI. Reached 1.0 recently. |
| `graphile_worker` | 0.14.1 (2026-10-11) | Rust port of Graphile Worker; Postgres only (not verified in its README); about 96k downloads. |
| `sqlxmq` | 0.6.0 (2025-05-25) | Postgres message queue on SQLx; slower release cadence. |
| `fang` | 0.11.0 (2026-07-02) | Background jobs; about 114k downloads. |
| Loco workers | part of Loco 1.3.1 | See web framework table. |
| In-process `tokio::spawn` plus a jobs table | n/a | Simplest. Durable if job state lives in the table and a startup scan resumes unfinished rows. Retries and timeouts are hand-built. |

Recruiter Batches have per-file progress that the UI shows, which fits a jobs table the app owns (one row per Batch and per CV) with a queue library only dispatching work. CPU-heavy analysis (and any OCR or model inference, see other tickets) should run on a dedicated worker pool, separate from the request runtime.

## Coherent stack combinations

### Stack A: Axum, server templates and HTMX (recommended)

- Axum with `tower-http`; Askama or MiniJinja templates; HTMX for fragments; vanilla GSAP and Lenis as plain scripts.
- Fluent via `fluent-templates` for strings, ICU4X for date and number formatting.
- Typst (`typst-as-lib`) for PDF; `docx-rs` for DOCX from the same Template data model.
- Postgres with SQLx; `tower-sessions` plus `axum-login`, `argon2`.
- Postgres-backed queue (`apalis` with Postgres, or `graphile_worker`) for Batches, run in a separate worker process from the same workspace.
- Builder live scoring: debounced fragment requests first; a WASM build of the scoring crate if latency demands.

Why: one language on the server, minimal JS, direct fit with the GSAP and Lenis house rules, the most agent-friendly crates, and each layer is replaceable. Weakness: you assemble auth, mail, migrations and job plumbing yourself.

### Stack B: Loco

- Loco (Axum, SeaORM, workers, mailers, auth) with its templating; Fluent added on top; Typst and `docx-rs` as in A; Postgres or SQLite queue per its `loco new` wizard.

Why: fastest scaffold for accounts, jobs and mail. Weaknesses: smaller community, SeaORM and Loco conventions shape the app, and i18n was not covered in the Loco docs read. Reasonable if the developer values batteries-included over control.

### Stack C: Axum JSON API and TypeScript SPA

- Axum API with OpenAPI; React, Svelte or similar SPA; GSAP and Lenis native; ICU MessageFormat in TS for UI strings; Typst and `docx-rs` on the server; Postgres, SQLx, queue as in A.

Why: best Builder interactivity, easiest GSAP, widest frontend ecosystem. Weaknesses: two toolchains, a second i18n system beside any Rust-side strings (error messages, exports), contract drift, heavier first load.

A Leptos or Dioxus full-stack variant (Stack D) was considered and not recommended: GSAP fights Rust-owned DOM, both frameworks are young, WASM size and compile times grow with the app, and nothing in the requirements needs an all-Rust UI.

## Recommendation

Stack A, with Postgres. Revisit in two cases:
- The Builder prototype (#19) shows debounced HTMX round trips are too slow or the editor needs too much client state. Then add a small TS island (or WASM scoring module) for the Builder only, not a full SPA.
- The developer wants auth, mail and jobs scaffolded for speed. Then evaluate Loco (Stack B) in the same spike.

## Risks for a solo developer working with coding agents

- **Compile times and feedback loops.** Rust build times slow agent iteration; runtime-loaded templates (MiniJinja) shorten the loop for UI work, compile-time templates (Askama) catch errors earlier. Not benchmarked.
- **Pre-1.0 and unstable APIs.** Axum is 0.8, `typst-as-lib` says its API is unstable, Typst tracks its own versions (0.15), Leptos and Dioxus are 0.x. Pin versions; agents trained on older versions produce stale code. Feed current docs (Context7) into agent prompts.
- **Two document renderers.** PDF (Typst) and DOCX (`docx-rs`) must stay aligned across 7 languages. Each new Template doubles the work and the tests.
- **RTL and CJK in documents.** Typst needs `lang` or `dir` and bundled fonts with fallback; DOCX bidi coverage in `docx-rs` is not fully verified. Test Arabic, Japanese and Chinese output early.
- **Font licensing and size** for bundled CJK and Arabic fonts (not checked).
- **Maintenance risk of niche crates.** `axum-login` last released 2025-07-20, `fluent-bundle` 2025-05-22, `oauth2` 2025-01-21, `genpdf` 2021, `sqlxmq` 2025-05. Check each against the chosen Axum version.
- **Auth and GDPR plumbing** is hand-built in plain Axum (verification, reset, deletion, export, retention).
- **Heavy jobs on the request runtime.** CPU-bound analysis must not block Tokio worker threads; use a separate worker pool or process.
- **Agent-friendliness.** Axum, SQLx, Askama and HTMX patterns are common in public code; Loco, Leptos and Dioxus are less common, so agents may err more there (observation, not measured).

## Implications for other tickets

- **#13 Rust boundary:** the document layer is Rust (Typst, `docx-rs`) regardless of the NLP decision. The scoring core can ship as a Rust library used by the server and, if needed, compiled to WASM for the Builder. A hybrid with Python models as a sidecar is compatible with this web stack, since the web layer talks to workers through the jobs table or HTTP.
- **#19 Builder prototype:** measure live-scoring latency for debounced HTMX fragments versus a client-side WASM scoring module. Prototype one Template rendered through both Typst (PDF) and `docx-rs` (DOCX) in Arabic and Japanese before locking Templates.

## Open questions

1. Typst compile latency per CV in each language, and whether export runs inline or as a job.
2. Does `docx-rs` fully support right-to-left runs and complex-script fonts, or only paragraph bidi?
3. Which fonts to bundle for ar, ja and zh, and their licences and sizes.
4. Hosting decision (map #2): one VM (SQLite viable) or managed platform (Postgres).
5. Does the Builder need client-side state beyond debounced fragments?
6. Does Loco fit multi-language server rendering and Fluent without fighting its conventions?
7. Which mail provider and crate for verification and reset emails (not surveyed).
8. `axum-login` and `tower-sessions` compatibility with the Axum minor chosen at build time.
9. Is ICU4X segmentation adequate for ja and zh text, or is a dedicated tokenizer needed (relates to the NLP tickets)?

## Sources

- Axum: https://github.com/tokio-rs/axum
- Actix Web: https://github.com/actix/actix-web
- Loco README: https://github.com/loco-rs/loco/blob/master/README.md ; worker modes and queue backends: https://github.com/loco-rs/loco/blob/master/website/src/content/docs/docs/how-to/choose-queue-backend.md and https://github.com/loco-rs/loco/blob/master/website/src/content/docs/docs/explanation/background-processing-model.md
- Leptos book (islands, binary size): https://book.leptos.dev/islands.html , https://book.leptos.dev/deployment/binary_size.html ; https://github.com/leptos-rs/leptos
- Dioxus fullstack API: https://docs.rs/dioxus/latest/dioxus/ ; https://github.com/DioxusLabs/dioxus
- Askama: https://github.com/askama-rs/askama ; MiniJinja: https://github.com/mitsuhiko/minijinja ; Tera: https://github.com/Keats/tera ; Maud: https://github.com/lambda-fairy/maud ; axum-htmx: https://github.com/robertwayne/axum-htmx ; datastar-rust: https://github.com/starfederation/datastar-rust
- Fluent (fluent-rs) API docs: https://github.com/projectfluent/fluent-rs ; fluent-templates: https://github.com/XAMPPRocky/fluent-templates ; rust-i18n: https://github.com/longbridge/rust-i18n ; ICU4X: https://github.com/unicode-org/icu4x
- Typst text reference (dir, lang, font fallback): https://typst.app/docs/reference/text/text ; PDF export and standards: https://typst.app/docs/reference/pdf ; export targets: https://typst.app/docs/reference/html and https://typst.app/docs/web-app/export-and-preview ; https://github.com/typst/typst
- typst-as-lib README: https://github.com/Relacibo/typst-as-lib
- docx-rs README and source: https://github.com/bokuweb/docx-rs ; docx-rust: https://github.com/cstkingkey/docx-rs ; printpdf: https://github.com/fschutt/printpdf ; lopdf: https://github.com/J-F-Liu/lopdf ; genpdf: https://git.sr.ht/~ireas/genpdf-rs
- SQLx: https://github.com/launchbadge/sqlx ; SeaORM: https://github.com/SeaQL/sea-orm
- apalis: https://github.com/apalis-dev/apalis ; graphile_worker: https://github.com/leo91000/graphile_worker_rs ; sqlxmq: https://github.com/Diggsey/sqlxmq ; fang: https://github.com/ayrat555/fang
- tower-sessions: https://github.com/maxcountryman/tower-sessions ; axum-login: https://github.com/maxcountryman/axum-login ; argon2: https://github.com/RustCrypto/password-hashes ; oauth2: https://github.com/ramosbugs/oauth2-rs ; openidconnect: https://github.com/ramosbugs/openidconnect-rs ; webauthn-rs: https://github.com/kanidm/webauthn-rs
- crates.io API (versions, dates, downloads), queried 2026-11-08: https://crates.io/api/v1/crates/NAME

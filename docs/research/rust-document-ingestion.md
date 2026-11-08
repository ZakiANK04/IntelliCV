# Rust document ingestion: PDF, DOCX, OCR, scan detection

Resolves issue #5 (map: #2). Researched 2026-11-08 from crate metadata, READMEs, source files and vendor docs. Nothing here was benchmarked on our own CVs, and no sample PDFs or DOCX files exist in the repo, so every latency number below comes from a third-party source on the hardware stated next to it. Where a number was not found, the text says "not found".

## Recommendation

| Need | Pick | Why | Main risk |
|---|---|---|---|
| PDF text and page rendering | `pdfium-render` (MIT OR Apache-2.0) over a prebuilt PDFium (BSD-3/Apache) | Permissive, one library for text, geometry and rendering pages to bitmaps for OCR, prebuilt binaries for Windows and Linux | Reading order on multi-column CVs is not documented; PDFium is not thread-safe |
| PDF text, speed candidate | `pdf_oxide` (MIT OR Apache-2.0), benchmark before adopting | Pure Rust, vendor reports 0.8 ms mean per document | Vendor-only numbers, young project, one maintainer |
| Avoid | `mupdf` crate (AGPL-3.0), `lopdf` for text (no layout extraction), `pdf-extract` (basic) | Licence, missing feature, lower pass rate | n/a |
| DOCX | Read `word/document.xml` directly (zip + `quick-xml`), or the `docx-rs` reader as a shortcut | DOCX has no page layout, so order is document order | Text boxes and table-based columns need handling; no latency data found |
| OCR, CPU, per-script control | PP-OCR models through ONNX Runtime (`ort`), via `oar-ocr` or `paddle-ocr-rs` | Apache-2.0, per-script recognisers for Latin, Arabic, Chinese and Japanese, small models | Seconds per page on CPU in the RapidOCR pipeline; accuracy not measured on CVs |
| OCR, fastest | Indra OCR (runs inside `oar-ocr`) only if its model licence fits | About 0.2 s per page on 4 vCPUs, all 7 scripts covered | Weights are modified OpenRAIL-M, not Apache; Arabic and Japanese evidence is thin |
| OCR, baseline | Tesseract via `leptess` or `rusty-tesseract` | Apache-2.0, per-language trained data of 1.1 to 4.1 MB | Slowest tested; `leptess` last released 2023; needs a system Tesseract |
| Scan detection | Per page: extracted character count plus image coverage, with a hybrid path | Cheap with `pdfium-render`, no model needed | Thresholds must be tuned on real CVs |

Overall: OCR dominates cost. Reading a scanned page costs hundreds of milliseconds to several seconds of CPU and is the same from Python or Rust, so only digital PDFs and DOCX get the Rust speed-up. OCR should run as a separate, queue-fed worker.

## PDF text

### Candidates

| Option | Licence | Text and order | Build on Windows and Linux | Latency |
|---|---|---|---|---|
| `pdfium-render` 0.9.5 | MIT OR Apache-2.0 (crate), PDFium BSD-3/Apache-2.0 | `text().all()`, `segments()` and `chars()` with page coordinates, so we can sort columns ourselves. Also renders pages to bitmaps | PDFium is bound at run time, not built. Prebuilt dynamic libraries for all major platforms come from `bblanchon/pdfium-binaries` (MIT). Static linking is supported through `PDFIUM_STATIC_LIB_PATH` but we must supply the archive | Not found for this crate. A vendor table (below) reports 4.1 ms mean per document for `pypdfium2`, which wraps the same engine |
| `pdf_oxide` 0.3.78 | MIT OR Apache-2.0 (the name is a trademark of its author) | Word-gap parameters are exposed; column handling on CVs is not described | Pure Rust | Vendor: 0.8 ms mean, 9 ms p99 per document, single thread, 3,830 public test PDFs (veraPDF, pdf.js, DARPA SafeDocs). Hardware not stated |
| `mupdf` 0.8.0 | AGPL-3.0 | Strong text extraction | Needs a C build | Vendor table: PyMuPDF 4.6 ms mean, same corpus |
| `lopdf` 0.47.0 | MIT | Document manipulation library; the `pdf_oxide` table lists it as "no built-in extraction" | Pure Rust | 0.3 ms, 80.2% pass rate, no extraction |
| `pdf-extract` 0.12.1 | MIT | Basic, built on `lopdf` | Pure Rust | 4.08 ms mean, 91.5% pass rate (same vendor table) |
| `unpdf` 0.54.0 | not checked | Basic | Pure Rust | 2.8 ms, 95.1% pass rate (same vendor table) |

Python baseline for context, same vendor table: `pdfplumber` 23.2 ms and PyMuPDF 4.6 ms mean per document. The app uses both today (`docs/analysis-pipeline.md`).

### Findings

- Licence: `mupdf` is AGPL-3.0, so it is out unless the whole service accepts AGPL. PyMuPDF has the same licence, which already applies to the Flask app.
- Reading order on multi-column CVs is the open question. No primary source describes how PDFium or `pdf_oxide` orders two-column pages. `pdfium-render` exposes segments with positions, so a column-aware sort is possible in our own code, but it has to be tested on a CV corpus before choosing. This is the most valuable benchmark to run next.
- Threading: PDFium is not thread-safe. `pdfium-render` serialises all calls behind a mutex (default `thread_safe` feature), so extra threads add no throughput. Batch processing (recruiter Batch) should use several processes or workers, as the PDFium authors recommend.
- Reuse for OCR: the same `pdfium-render` handle renders pages to bitmaps, which feeds OCR without a second PDF library.
- Benchmark caveat: the 0.8 ms figure is the project's own README, covers PDFs of all kinds (not CVs) and has no stated hardware.

## DOCX

- `docx-rs` 0.4.22 (MIT) describes itself as a ".docx file writer"; its README documents `read_docx`, which parses a package into the same `Docx` model, with an option to skip image previews. No latency or accuracy data found.
- `docx-rust` 0.1.11 and `docx-lite` 0.2.0 exist; `dotext` was last released in 2017. None was evaluated further.
- A DOCX is a zip of XML (ECMA-376). Text lives in `word/document.xml`, so extraction can be a zip read plus a streaming XML parse with no layout engine. This is my reasoning, not a benchmarked claim. It keeps us in control of tables, text boxes (`w:txbxContent`) and headers, which many two-column CV templates use for their sidebar.
- Per-file latency: not found. Measure on real CVs.

## OCR

### Candidates

| Option | Licence | Scripts for our 7 languages | Build and footprint | Latency evidence |
|---|---|---|---|---|
| PP-OCR (PaddleOCR) models via `ort` (crates `oar-ocr` 0.10.2 and `paddle-ocr-rs` 0.6.1, both Apache-2.0) | Code Apache-2.0; model licences are listed per model | PP-OCRv5 default recogniser: Simplified and Traditional Chinese, English, Japanese. Separate v5 recognisers for Latin (French, German, Spanish and others) and Arabic. `oar-ocr` lists checkpoints for Chinese, English, Arabic, Japanese and Latin among others | ONNX Runtime binaries download by default in `oar-ocr`. Mobile detector 4.7 MB, mobile recogniser 16 MB; server detector 84.3 MB, server recogniser 81 MB | See below |
| Indra OCR (Datalab; runs in `oar-ocr` as `oar_ocr::indra`) | Code Apache-2.0; weights modified OpenRAIL-M: free for research, personal use and startups under $20M funding or revenue, not for use competing with Datalab's API | Four recognisers: Latin, Cyrillic and Greek; CJK (Chinese, Japanese, Korean); RTL (Arabic and others); other scripts. Vertical Chinese and Japanese handled | About 76 MB of models, CPU | Vendor: median 212 ms per page (auto mode) and 344 ms (OCR only), 4 vCPUs, x86, one page at a time |
| Tesseract 5 via `leptess` 0.14.0 (MIT, last release 2023) or `rusty-tesseract` 1.1.10 (MIT, last release 2024, wraps the CLI) | Apache-2.0 | `tessdata_fast` trained data: `eng` 4.1 MB, `fra` 1.1 MB, `deu` 1.5 MB, `spa` 2.3 MB, `ara` 1.4 MB, `jpn` 2.5 MB, `chi_sim` 2.5 MB | `leptess` needs Tesseract and Leptonica installed; on Windows it uses vcpkg with user-wide integration. `rusty-tesseract` needs the Tesseract binary on PATH | Vendor: 5,496 ms median per page (Tesseract 5, Latin model) in the Indra benchmark; 3.4 s per page, one thread, `eng` model, same README |
| `ocrs` 0.14.0 | MIT OR Apache-2.0 | Latin alphabet only, "early preview" per its README | Pure Rust (RTen) | Not found |

### Latency and footprint evidence

Indra OCR benchmark (OmniParseBench pages, x86, 4 vCPUs per engine, one page at a time, run by the vendor):

| Engine | Median ms per page | Pages per second, 4 cores | Pages per second, 32 cores |
|---|---|---|---|
| Indra OCR (text layer plus OCR) | 212 | 6.2 | 43.9 |
| Indra OCR (OCR only) | 344 | not given | not given |
| PP-OCRv6 small text models via RapidOCR | 2,685 | 0.65 | 4.28 |
| Tesseract 5, Latin model | 5,496 | 0.78 | 2.92 |

Throughput columns use one single-threaded worker per core on an AMD EPYC 9004 (Genoa) machine. The vendor competes with the engines it compares, so treat this as directional. The same README scores text accuracy at 35.8 for PP-OCRv6 small, 19.3 for Tesseract and 40.7 for Indra OCR in OCR-only mode; these are benchmark pass rates on mixed documents, not CV accuracy.

PaddleOCR's own per-model figures (PaddlePaddle runtime, Intel Xeon Gold 6271C at 2.60 GHz, "normal mode / high-performance mode"):

| Model | CPU ms | Size MB |
|---|---|---|
| PP-OCRv5 mobile detector | 57.77 / 28.15 | 4.7 |
| PP-OCRv5 server detector | 383.15 / 383.15 | 84.3 |
| PP-OCRv5 mobile recogniser | 21.20 / 5.32 | 16 |
| PP-OCRv5 server recogniser | 31.21 / 31.21 | 81 |

The docs do not say whether recogniser time is per text line or per image, so no per-page figure can be derived. These runs use PaddlePaddle, not ONNX Runtime, so `ort` numbers may differ.

### Accuracy evidence by script

- PP-OCRv5 multilingual recognisers, on PaddleOCR's own datasets: Latin 84.7% (3,111 images), Arabic 81.27% (2,676 images, Arabic and related scripts), English 85.25%. The default Chinese, English and Japanese recogniser reports 81.29% (mobile) and 86.38% (server) average accuracy on PaddleOCR's evaluation set. These are recognition accuracies on the project's datasets, not CVs.
- PP-OCRv6 has small (20.4 MB) and medium (73.3 MB) recognisers covering 50 languages. Its metrics use an internal set and the docs say they are not comparable with v5. I did not find a per-language list, so v6 coverage of Arabic and Japanese is unconfirmed.
- Indra OCR per script on OmniParseBench: Latin 61.6 (9,406 tests), Chinese 64.0 (136), Arabic 69.2 (13), Japanese kana 57.9 (19). The README warns that one test moves a small-script score by 2 to 8 points, so Arabic and Japanese are weak evidence. It lists degraded scans (29.5) and handwriting (25.2) as poor, and says English, French, German and Spanish are unaffected by its diacritic weakness.
- Tesseract: no primary accuracy figures for Arabic, Japanese or Chinese found in this pass.
- Right-to-left: Indra states Arabic lines come out in logical order and a right-to-left page reads its right column first. For PP-OCR and Tesseract, RTL ordering was not checked and needs a test with Arabic CVs.

### Findings

- Engine choice changes page time by 10x to 25x (about 0.2 s against 2.7 to 5.5 s per page on 4 vCPUs in the one comparison found). Rust does not change that.
- The permissive path is PP-OCR through `ort` (Apache-2.0) with one recogniser per script, chosen from the CV Language. The fastest path (Indra) has a weights licence that restricts competing use and applies a $20M threshold; that licence decision belongs to the owner.
- Tesseract is the lowest-risk fallback on licence and Windows packaging is workable through vcpkg, but it was the slowest tested and the Rust wrappers are less maintained.

## Detecting a scanned PDF

No library offers a documented "is scanned" call, so the check is ours. Proposed rule, per page, using `pdfium-render`:

1. Extracted characters: `page.text()` length after removing whitespace. The Flask app today uses 50 characters for the whole document (`docs/analysis-pipeline.md`); per page is more accurate.
2. Image coverage: iterate page objects and sum the bounds of image objects (`as_image_object()` exists in `pdfium-render`). A page mostly covered by one image with few characters is a scan.
3. Bad text layers: some scans carry a poor OCR text layer. The `pdfium-render` README lists `PdfPageTextChar::has_unicode_map_error()` (0.9.6 release notes) for spotting unmapped characters; the share of such characters on a page is a usable signal. crates.io showed 0.9.5 as latest, so confirm it is published.
4. Route per page, not per file. Mixed documents (a scanned page inside a digital file) exist. Indra's pipeline labels pages `text`, `ocr` or `hybrid` and OCRs only image text in hybrid mode, which is a design worth copying.

Thresholds (characters per page, image coverage fraction) are not sourced and must be tuned on a labelled set of digital and scanned CVs.

## Implications for other tickets

- Hosting (#11) and latency budget (#12): digital PDF and DOCX extraction is milliseconds per file in every vendor figure found, so it does not drive the budget. Scanned pages cost 0.2 s to 5.5 s each on 4 vCPUs depending on engine, so the OCR engine and a worker queue drive CPU sizing. A 2-page scan at 2.7 s per page is about 5 s on 4 cores. Throughput to plan around: 0.65 to 6.2 pages per second on 4 cores.
- Model files are small (tens of MB per script set), so memory is set by ONNX Runtime and parallel workers. No source gave ONNX Runtime resident memory, so this is unmeasured.
- Batch (recruiter) uploads need process-level parallelism because of PDFium's threading model.
- Licence check for the stack: avoid `mupdf`; confirm the Indra weights licence before relying on it.

## Open questions

1. Reading order of `pdfium-render` and `pdf_oxide` on two-column and sidebar CV layouts: test on 20 to 50 real CVs in the 7 languages.
2. OCR accuracy on CVs (not general documents), per script, especially Arabic, Japanese vertical text and low-resolution phone photos.
3. Whether PP-OCR through `ort` on our hardware is closer to the Paddle per-model figures (tens of ms per call) or the RapidOCR figure (2.7 s per page).
4. PP-OCRv6 support for Arabic and Japanese, and its ONNX conversions.
5. Whether the Indra weights licence is acceptable.
6. DOCX handling of text boxes and table layouts, and per-file latency.
7. Windows build of the full stack in practice (PDFium DLL placement, ONNX Runtime download, `leptess` through vcpkg).
8. Whether photos (JPEG, PNG) need preprocessing such as deskew before OCR. Indra reports orientation and skew handling; PP-OCR was not checked.

## Sources

- `pdfium-render` README and source: https://github.com/ajrcarey/pdfium-render ; crate: https://crates.io/crates/pdfium-render
- PDFium prebuilt binaries: https://github.com/bblanchon/pdfium-binaries
- `pdf_oxide` README and benchmark tables: https://github.com/yfedoseev/pdf_oxide
- `mupdf-rs` (AGPL-3.0): https://github.com/messense/mupdf-rs
- `lopdf`: https://github.com/J-F-Liu/lopdf ; `pdf-extract`: https://github.com/jrmuizel/pdf-extract ; `unpdf`: https://github.com/iyulab/unpdf
- `docx-rs`: https://github.com/bokuweb/docx-rs ; https://crates.io/crates/docx-rust ; https://crates.io/crates/docx-lite
- OOXML standard: ECMA-376, https://ecma-international.org/publications-and-standards/standards/ecma-376/
- `oar-ocr`: https://github.com/GreatV/oar-ocr ; `paddle-ocr-rs`: https://github.com/mg-chao/paddle-ocr-rs ; `ort`: https://github.com/pykeio/ort ; `ocrs`: https://github.com/robertknight/ocrs
- PaddleOCR PP-OCRv5 and text recognition docs (model tables, test environment): https://github.com/PaddlePaddle/PaddleOCR/tree/main/docs/version3.x ; RapidOCR: https://github.com/RapidAI/RapidOCR
- Indra OCR model card (benchmarks, licence, languages): https://huggingface.co/datalab-to/indra-ocr
- Tesseract: https://github.com/tesseract-ocr/tesseract ; trained data: https://github.com/tesseract-ocr/tessdata_fast ; `leptess`: https://github.com/houqp/leptess ; `rusty-tesseract`: https://github.com/thomasgruebl/rusty-tesseract
- Crate versions and licences: crates.io API, queried 2026-11-08.

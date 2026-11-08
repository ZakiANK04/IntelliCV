# Multilingual NLP models that run on CPU from Rust

Ticket: #4. Date of research: 2026-11-08. Scope: the 7 Supported Languages (en, fr, ar, es, de, ja, zh), local CPU inference only, no hosted LLM APIs.

## How to read the numbers

- Sizes on disk come from the Hugging Face file listings (byte counts from the Hub API), so they are exact for the files named.
- **No source found gives per-CV latency for any candidate.** Model cards and crate READMEs publish throughput on their own hardware, or nothing. Where a measured number exists it is quoted with the hardware the source states. Everything else is marked "not found".
- For the encoders I add a computed cost in GFLOP per CV. This is arithmetic from the architecture in `config.json`, not a measurement. It lets you rank candidates and scale a benchmark from one to another, but it does not give milliseconds. A CV is taken as about 1,024 tokens (an assumption, not measured).
- No model was downloaded or run for this note. The one thing that would settle the latency budget (ticket #12) is a benchmark on the target host, using the ONNX files below. That is listed under open questions.
- Machine context for a later benchmark: the research machine is an AMD Ryzen AI 9 365, 20 logical cores, 31 GB RAM. No benchmark was run on it.

## Inference engine: same cost from Python or Rust

All the Rust runtimes below either call ONNX Runtime (`ort`) or reimplement the maths. The model forward pass dominates, so a model costs about the same from Python (`onnxruntime`, PyTorch) and Rust (`ort`). Rust saves time only around the model: tokenisation, batching, pre- and post-processing. No source compared the same model across Python and Rust except gline-rs (see NER).

| Runtime | What the primary source says | Fit |
|---|---|---|
| `ort` | Rust interface to ONNX Runtime; README badge shows ONNX Runtime v1.31.0; API reference links to 2.0.0-rc.15, so the crate is a release candidate | Best fit. Runs the ONNX files that Hugging Face already ships, including int8 variants. |
| `candle` | README lists BERT, JinaBERT and T5 as embedding-capable examples, an optimised CPU backend (optional MKL on x86, Accelerate on Mac), WASM support. XLM-RoBERTa and E5 are not mentioned in the README | The multilingual encoders here are XLM-RoBERTa-based. Whether candle supports them was not verified. |
| `tract` | Loads ONNX and NNEF; used in production at Sonos for audio; no operator-coverage figure or quantisation mention; Apache-2.0 or MIT | Unproven for 12-layer XLM-R encoders. Needs a test. |
| `rust-bert` | Uses libtorch 2.4 through `tch-rs`; optional `onnx` feature through `ort`. NER models listed: English, German, Spanish, Dutch only. Sentence-embedding list names DistilBERT, BERT, RoBERTa, ALBERT, T5 | Does not cover ar, fr (NER), ja, zh out of the box. Heavy (libtorch). Not recommended. |
| `tokenizers` | Rust is the reference implementation; the README calls the current line a release candidate for 1.0.0 | Needed whichever runtime is used; all candidate models ship a `tokenizer.json` or SentencePiece model. |

Quantisation: the ONNX Runtime docs recommend dynamic quantisation for transformer models, say it "is not a loss-less transformation", and warn about U8S8 saturation on x86 CPUs without VNNI (use S8S8 or reduce-range there). The e5-small and MiniLM repos already ship int8 variants, so quantised files exist without doing the conversion.

## Sentence embeddings (Career Field, Fit Score, cross-language matching)

| Model | Licence | Params | ONNX on disk | Max tokens | Computed cost per 1,024-token CV | Notes |
|---|---|---|---|---|---|---|
| `intfloat/multilingual-e5-small` | MIT | about 118M (12 layers, hidden 384, vocab 250,037) | fp32 470,268,510 B; O4 235,052,531 B; int8 (avx512_vnni) 118,346,824 B | 512 | about 44 GFLOP | Needs "query: " / "passage: " prefixes. Quality numbers not retrieved. |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Apache-2.0 | 117,654,272 | fp32 470,301,610 B; O4 235,166,264 B; int8 variants about 118.4 MB (arm64, avx512, avx512_vnni, avx2) | 128 (model card) | about 44 GFLOP if chunked; it truncates at 128 tokens, so a CV needs about 8 chunks | 50 languages. Same architecture as e5-small. |
| `intfloat/multilingual-e5-base` | MIT (from the e5 family; not separately fetched) | about 278M (12 layers, hidden 768) | not measured | 512 | about 174 GFLOP | About 4x the e5-small cost. |
| `BAAI/bge-m3` | MIT | not stated on card; ONNX external data is 2,266,820,608 B | 2.27 GB fp32, no int8 shipped | 8,192 | about 618 GFLOP, assuming XLM-R-large layout (24 layers, hidden 1024; not fetched) | 100+ languages. Reads a whole CV in one pass. Heavy for CPU. |
| `google/embeddinggemma-300m` | Gemma terms (not an OSI licence) | 302,863,104 | no ONNX in the repo | not retrieved | not computed | Licence is a restriction to review. |
| `Qwen/Qwen3-Embedding-0.6B` | Apache-2.0 | 595,776,512 | no ONNX in the repo | not retrieved | not computed | Larger than bge-m3's budget class for CPU. |

GFLOP figures: 2 x non-embedding parameters x tokens. e5-small: 12 layers x (4x384^2 + 2x384x1536) = 21.2M parameters, so 42.5 MFLOP per token. Attention-over-length cost is ignored, so long inputs cost somewhat more.

Shortlist:
1. **multilingual-e5-small (int8 ONNX, 118 MB)**. MIT, 512-token window, ships ONNX and int8, smallest cost that still reads whole sections. Default pick.
2. **multilingual-e5-base** if e5-small quality fails a per-language validation set. About 4x the compute.
3. **paraphrase-multilingual-MiniLM-L12-v2** as the fallback with the cleanest licence (Apache-2.0). Its 128-token limit means chunking, and it is a paraphrase model, not a retrieval model.
4. bge-m3 only if long-context matching proves necessary and the latency budget allows it.

Quality per language: the e5 paper (arXiv 2402.05672) reports MIRACL and bitext results, but the PDF could not be read through the tools used, so no per-language score is quoted here. The abstract says the models were contrastively pre-trained on 1 billion multilingual text pairs. Quality on CVs specifically (as opposed to web passages) was not found for any model.

## NER (people, organisations, dates, locations; ideally job titles and skills)

| Model | Languages covered | Licence | Size | Notes |
|---|---|---|---|---|
| `Davlan/xlm-roberta-base-ner-hrl` | ar, de, en, es, fr, zh (plus it, lv, nl, pt). **No ja.** | AFL-3.0 | model.safetensors 1,109,868,164 B (XLM-R base, fp32) | PER, LOC, ORG only; trained on news (ANERcorp, CoNLL-2003/2002, Europeana, MSRA); card warns it is limited to news from a time span; no F1 reported on the card. No DATE, no job title, no skill. |
| `urchade/gliner_multi-v2.1` (GLiNER) | "multilingual" per card; the languages are not listed on the card | Apache-2.0 | model.safetensors 1,155,830,112 B | Zero-shot: you pass labels such as "job title", "skill", "date" at call time, which is the only candidate that can cover job titles and skills without new training. ONNX conversion is documented by the GLiNER project; the card itself does not mention ONNX. |
| Japanese NER, `tsmatz/xlm-roberta-ner-japanese` | ja | MIT | not retrieved | Also on the Hub: `llm-book/bert-base-japanese-v3-ner-wikipedia-dataset` (Apache-2.0). Both are Wikipedia-style entity sets, not CV-oriented. |
| spaCy `ja_core_news_*`, `zh_core_web_*` | ja, zh | not retrieved | not retrieved | The spaCy page failed to load model details (size, licence, F-score). Re-check on the spacy-models releases. These run in Python; no Rust path. |

Rust path for GLiNER: the `gline-rs` crate (uses `ort`; needs `model.onnx` and `tokenizer.json`; 1.0.0 is described as production-ready). Its README benchmark, version 0.9.0, on an Intel Core i9 at 2.3 GHz with 8 cores (12 threads): 6.67 sequences per second against 1.61 for the Python GLiNER, so about 4x, using gliner-multitask-large-v0.5 in token mode, 3 entity classes, first 100 entries of a NuNER subset. The model is English-oriented, not the multilingual one, the sequences are short, and a CV is many sequences. This is the only Rust-versus-Python comparison found, and its 4x is not a statement about model cost: it may reflect Python pre- and post-processing. I found no recent independent reproduction. A GPU run of 248.75 sequences per second on an RTX 4080 is also reported; irrelevant for CPU hosting.

Shortlist:
1. **GLiNER multi (via `gline-rs` + `ort`)** for job titles, skills, dates, organisations in all seven languages, subject to per-language validation (the language list was not found).
2. **Davlan xlm-roberta-base-ner-hrl** as the cheaper, proven-style PER/ORG/LOC tagger for six of the seven languages.
3. A separate Japanese NER (tsmatz or llm-book) to fill the ja gap, or rely on GLiNER for ja after testing.
4. Rules and gazetteers for dates, emails, phones: do not spend a model on these. (Design suggestion, not a sourced finding.)

Per-CV latency for NER: not found for any candidate. The XLM-R base cost is about 174 GFLOP per 1,024 tokens by the same arithmetic as above; GLiNER multi's backbone size is not stated on the card (the card lists 209M in a table and 0.3B in the header).

## Language identification

| Candidate | Languages | Licence | Evidence |
|---|---|---|---|
| `whichlang` (Rust) | 16, including ar, de, en, es, fr, ja and Mandarin. Covers all 7. | Not stated in README | Author: 99.5% on its own validation set. A third-party benchmark: 97.03% average across length buckets vs 91.69% for whatlang. Throughput about 105.69 MiB/s short strings, 112.31 MiB/s long strings. |
| `lingua` (Rust) | 75, including all 7 | Apache-2.0 (badge) | Only a few dozen MB RAM with all models loaded (stated). Single thread, 2,000 sentences: whichlang 4.47 ms, CLD2 23.92 ms, whatlang 36.24 ms, lingua low-accuracy 492.50 ms, lingua high-accuracy 640.30 ms. Hardware not stated in the text read. Author says it is the most accurate in its comparison; accuracy below 120 characters drops in low-accuracy mode. |
| `whatlang` (Rust) | 70; the full list was not read, so the 7 are unverified | MIT | Trigram method; README gives no accuracy or speed figures. |
| fastText `lid.176` | 176, includes all 7 | CC BY-SA 3.0 | `lid.176.bin` about 126 MB, `lid.176.ftz` about 917 kB. No timing or accuracy figures on the page. Share-alike licence needs a legal check. |

Shortlist: `whichlang` for speed, `lingua` when accuracy on short or mixed text matters more than a few hundred microseconds per sentence. CVs are long, so per-CV latency for either is small against the encoders (computed: 105 MiB/s means a 10 KB CV in under 0.1 ms for whichlang; lingua's measured 0.32 ms per sentence in high-accuracy mode gives low single-digit milliseconds for a CV of a few dozen sentences, hardware unstated). Mixed-language CVs, such as an English CV with a French section, are a separate open question.

## Japanese and Chinese segmentation

| Crate | Languages | Licence | Evidence |
|---|---|---|---|
| `lindera` | ja (IPADIC named); Chinese support not mentioned in the README read | MIT | About 10-20 MB/s single-threaded for IPADIC, hardware not stated. Dictionaries downloaded separately from GitHub releases. |
| `vibrato` | ja (MeCab-compatible; dictionaries from IPADIC, UniDic) | Apache-2.0 or MIT | README says it is faster than MeCab and reimplementations, with the figure and settings on its wiki; no numbers in the README. UniDic matrix file is 459 MiB. |
| `jieba-rs` | zh | MIT | Embedded dictionary by default; optional TF-IDF and TextRank. Benchmarks are against cppjieba only (linked articles on 2.4x and 33% speedups); no absolute figures. |

The subword tokenizers inside the encoders (SentencePiece for XLM-R models) handle ja and zh without a separate segmenter. A separate segmenter is only needed for rule-based Evaluative Measures that count words or match keywords and skills. Whether those measures need word-level segmentation for ja and zh is a design question for the scoring tickets, not answered here.

## Comparison summary

| Need | First choice | Runtime | Disk | Cost evidence |
|---|---|---|---|---|
| Embeddings | multilingual-e5-small int8 | `ort` | 118 MB | about 44 GFLOP per CV (computed); no measured latency |
| NER | GLiNER multi (+ Davlan for PER/ORG/LOC) | `gline-rs` / `ort` | about 1.1 GB each (fp32) | gline-rs: 6.67 seq/s on an i9 (different model, short sequences) |
| Language ID | whichlang (lingua if accuracy needs it) | native Rust | small | 105 MiB/s; lingua 0.32 ms per sentence |
| ja segmentation | vibrato or lindera | native Rust | dictionary-sized | lindera 10-20 MB/s |
| zh segmentation | jieba-rs | native Rust | embedded | no absolute figure |

Memory (RAM): not found for any model. Planning rule of thumb (not sourced): fp32 weights in RAM are about the file size, so the two NER models alone are about 2.2 GB before any quantisation. Quantising to int8 would cut that roughly to a quarter, but no int8 ONNX for them was confirmed.

## Implications for other tickets

- **#11 hosting:** two roughly 1.1 GB NER models plus an embedder mean the host needs at least a few GB of RAM and a CPU with AVX2 or better (VNNI preferred for int8). A tiny host is out unless the NER models are quantised. This is an inference from file sizes, not a measurement.
- **#12 latency budget:** the only measured things are language ID and segmentation throughput. The encoders and NER have no per-CV number in any primary source. A benchmark on the target CPU is needed before a budget is set. The computed ratios give the scaling: e5-base is about 4x e5-small, XLM-R-large-class models about 14x, and a 128-token model needs about 8x as many calls per CV.
- **#15 (blocked by this ticket):** the Career Field taxonomy and classifier can assume e5-small embeddings plus a small trained classifier head as the baseline.

## Open questions

1. Measured per-CV latency and RAM for e5-small (fp32, O4, int8), e5-base, MiniLM, Davlan and GLiNER multi through `ort` on the target host. Same files from Python `onnxruntime` for the Rust-vs-Python comparison the ticket asks for.
2. Which languages GLiNER multi was trained or tested on; quality for ar, ja, zh job titles and skills.
3. A multilingual CV validation set per language (datasets ticket) so embedding and NER quality can be scored per language, since no model card reports CV-domain results.
4. Does `candle` implement XLM-RoBERTa and run the e5 models? Not verified. Does `tract` run them?
5. e5 per-language MIRACL numbers: read the paper tables (the PDF was not machine-readable here).
6. Licences to review: AFL-3.0 (Davlan), CC BY-SA 3.0 (fastText lid.176), Gemma terms (EmbeddingGemma), unstated (whichlang, gline-rs).
7. spaCy ja and zh model sizes, licences and NER scores, and whether a Rust path exists for them.
8. Does an int8 GLiNER multi lose accuracy that matters? The ONNX Runtime docs warn quantisation is not loss-less.

## Sources

- multilingual-e5-small: https://huggingface.co/intfloat/multilingual-e5-small , config https://huggingface.co/intfloat/multilingual-e5-small/raw/main/config.json , files https://huggingface.co/api/models/intfloat/multilingual-e5-small/tree/main/onnx
- multilingual-e5-base config: https://huggingface.co/intfloat/multilingual-e5-base/raw/main/config.json
- Multilingual E5 report: https://arxiv.org/abs/2402.05672
- paraphrase-multilingual-MiniLM-L12-v2: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 , files https://huggingface.co/api/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2?blobs=true
- BGE-M3: https://huggingface.co/BAAI/bge-m3 , files https://huggingface.co/api/models/BAAI/bge-m3?blobs=true
- EmbeddingGemma: https://huggingface.co/api/models/google/embeddinggemma-300m
- Qwen3-Embedding-0.6B: https://huggingface.co/api/models/Qwen/Qwen3-Embedding-0.6B
- Davlan NER: https://huggingface.co/Davlan/xlm-roberta-base-ner-hrl , files https://huggingface.co/api/models/Davlan/xlm-roberta-base-ner-hrl/tree/main
- GLiNER multi v2.1: https://huggingface.co/urchade/gliner_multi-v2.1 , files https://huggingface.co/api/models/urchade/gliner_multi-v2.1/tree/main
- gline-rs: https://docs.rs/crate/gline-rs/latest
- Japanese NER listing: https://huggingface.co/api/models?search=ner%20japanese&sort=downloads&limit=8
- spaCy: https://spacy.io/models/ja , https://spacy.io/models/zh
- lingua-rs: https://github.com/pemistahl/lingua-rs
- whatlang-rs: https://github.com/greyblake/whatlang-rs
- whichlang: https://github.com/quickwit-oss/whichlang
- fastText language identification: https://fasttext.cc/docs/en/language-identification.html
- vibrato: https://github.com/daac-tools/vibrato
- lindera: https://github.com/lindera/lindera
- jieba-rs: https://github.com/messense/jieba-rs
- ort: https://github.com/pykeio/ort
- candle: https://github.com/huggingface/candle
- tract: https://github.com/sonos/tract
- rust-bert: https://github.com/guillaume-be/rust-bert
- tokenizers: https://github.com/huggingface/tokenizers
- ONNX Runtime quantisation: https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html

Method note: pages were read through a fetch tool that summarises content, so figures are as that tool reported them. Anything it could not extract is marked "not found" or "not retrieved" rather than filled in.

# Technical Documentation — Enterprise AI Research Agent

**Author**: Jay Beedkar  
**Contact**: [jayudict@gmail.com](mailto:jayudict@gmail.com)  
**Repository**: [github.com/jay2244-byte/Enterprise-ResearchAI-Agent](https://github.com/jay2244-byte/Enterprise-ResearchAI-Agent)

---

## 1. System Overview

The **Enterprise AI Research Agent** is a production-style, multi-stage research platform designed for dynamic, empirical investigation. Given any enterprise research question, the agent autonomously plans research sub-questions, executes public web & academic searches, evaluates source reliability via non-LLM rule formulas, extracts verbatim evidence quotes, compares multi-source perspectives, detects contradictions, synthesizes executive conclusions, and maintains 100% verifiable traceability (**Conclusion → Supporting Findings → Verbatim Quotes → Source URLs & Reliability Scores**).

---

## 2. Core Subsystem Architecture & Modules

### A. AI Provider Abstraction (`backend/app/ai/`)

The application enforces an abstract `AIProvider` base class interface (`generate()`, `generate_json()`, `get_embeddings()`) backed by a factory that auto-detects environment credentials:

1. **`GeminiAIProvider`**: Uses official Google Gemini API (`google-genai`).
2. **`OpenAICompatibleProvider`**: Connects to OpenAI, Groq, Ollama, or OpenRouter APIs.
3. **`HeuristicAIProvider`**: Built-in deterministic NLP fallback engine executing key-sentence ranking, term-frequency clustering, and rule-based extraction for zero-config offline execution without external API keys.

### B. Modular Pipeline Execution (`backend/app/modules/`)

| Module | Responsible Class | Description |
| :--- | :--- | :--- |
| `research_planner.py` | `ResearchPlanner` | Deconstructs main question into 4–6 analytical sub-questions covering Technology, Business ROI, Implementation Barriers, Risks, and Future Trends. |
| `source_search.py` | `SourceSearcher` | Queries live public DuckDuckGo, Wikipedia REST API, and ArXiv API. Scrapes clean page content with HTTPX and BeautifulSoup. |
| `source_evaluator.py` | `SourceEvaluator` | Computes objective 0–100 reliability scores based on domain authority, content depth, recency, and query relevance. |
| `information_extractor.py` | `InformationExtractor` | Extracts structured findings paired with exact verbatim evidence quotes from scraped text. |
| `finding_classifier.py` | `FindingClassifier` | Maps findings to configurable enterprise taxonomies (Technology, Business Benefit, Cost, Risk, Workforce, etc.). |
| `evidence_comparator.py` | `EvidenceComparator` | Groups findings into topic clusters and synthesizes multi-source perspective alignment and divergence. |
| `contradiction_detector.py` | `ContradictionDetector` | Analyzes conflicting findings and categorizes conflict type (`true_contradiction`, `different_context`, `different_time_period`, `different_industry`, `incomplete_information`). |
| `conclusion_generator.py` | `ConclusionGenerator` | Synthesizes executive conclusions strictly linked to supporting findings via the `conclusion_findings` association table. |
| `research_qa.py` | `ResearchQA` | Grounded Q&A engine querying stored project evidence via hybrid BM25 + vector search with clickable citations. |

---

## 3. Non-LLM Source Reliability Scoring Formula

The source reliability scoring system calculates an objective score ($0 \le S \le 100$) based on transparent structural factors rather than prompting an LLM:

$$S = S_{\text{domain}} + S_{\text{depth}} + S_{\text{recency}} + S_{\text{relevance}}$$

1. **Domain Authority ($S_{\text{domain}}$, max 35 pts)**:
   - Governmental / Academic TLDs (`.edu`, `.gov`, `.ac.uk`, `nature.com`, `arxiv.org`): **35 pts**
   - Established Analyst / Consultancy (`Gartner`, `McKinsey`, `PwC`, `Bain`): **30 pts**
   - Verified Enterprise Tech Vendor (`IBM`, `Microsoft`, `Google`, `NVIDIA`): **24 pts**
   - Commercial News (`Reuters`, `Bloomberg`, `WSJ`, `FT`): **22 pts**
   - General Web Content: **15 pts**

2. **Content Depth ($S_{\text{depth}}$, max 25 pts)**:
   - Word count > 1,500 words: **25 pts**
   - Word count 700–1,500 words: **20 pts**
   - Word count 250–700 words: **14 pts**
   - Snippet only (< 250 words): **8 pts**

3. **Recency ($S_{\text{recency}}$, max 20 pts)**:
   - Current data (2023–2026): **20 pts**
   - Recent data (2020–2022): **14 pts**
   - Older / Undated publication: **8–12 pts**

4. **Topical Relevance ($S_{\text{relevance}}$, max 20 pts)**:
   - High query keyword density match ($\ge 70\%$ match): **20 pts**
   - Moderate alignment ($40–70\%$ match): **15 pts**
   - General topical match: **10 pts**

**Classification Boundaries**:
- $S \ge 70$: **High Reliability**
- $45 \le S < 70$: **Medium Reliability**
- $S < 45$: **Low Reliability**

---

## 4. REST API Endpoint Specification

### Research Endpoints (`/api/research`)
- `POST /api/research`: Commission new research project.
- `GET /api/research`: List projects (with pagination & status filters).
- `GET /api/research/{id}`: Detailed project information.
- `POST /api/research/{id}/run`: Launch pipeline execution task.
- `GET /api/research/{id}/progress`: Real-time stage progress & logs.
- `GET /api/research/{id}/sources`: Persisted sources with reliability audit breakdowns.
- `GET /api/research/{id}/findings`: Extracted findings with evidence quotes.
- `GET /api/research/{id}/evidence-comparison`: Topic clusters & perspectives.
- `GET /api/research/{id}/contradictions`: Contradiction & contextual tension analysis.
- `GET /api/research/{id}/conclusions`: Major conclusions.
- `GET /api/research/{id}/trace/{conclusion_id}`: Full lineage (**Conclusion → Findings → Evidence Quotes → Source URLs & Scores**).
- `POST /api/research/{id}/ask`: Grounded research Q&A interrogation.

### Knowledge Base & System Endpoints (`/api/knowledge`, `/api/system`)
- `GET /api/knowledge/search?q=...`: Cross-project knowledge search across projects, sources, findings, and conclusions.
- `GET /api/system/stats`: Dashboard KPI metrics.
- `GET /api/system/health`: System health check.

---

## 5. Local Setup & Testing

### Running Backend
```bash
cd backend
python -m pip install -r requirements.txt
python run_backend.py
```
Backend live on: `http://127.0.0.1:8000`

### Running Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend live on: `http://localhost:5173`

### Running Test Suite
```bash
python -m pytest backend/tests
```
Executes unit tests for API endpoints, reliability scoring, contradiction classification, and traceability lineage.

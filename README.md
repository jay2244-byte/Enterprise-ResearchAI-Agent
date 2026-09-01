# Enterprise AI Research Agent

> **Built by**: Jay Beedkar  
> **Contact**: [jayudict@gmail.com](mailto:jayudict@gmail.com)

Production-style web application for autonomous enterprise research. Given any high-level research question, the agent independently plans research subtopics, searches public web/academic repositories (DuckDuckGo, Wikipedia, ArXiv), evaluates source reliability via deterministic scoring rules, extracts structured findings with verbatim evidence quotes, compares multi-source perspectives, detects contradictions, synthesizes executive conclusions, and provides complete **Traceable Evidence Lineage (Conclusion → Findings → Evidence → Sources)** alongside grounded **Research Interrogation Q&A** and a persistent **Knowledge Base**.

---

## Dedicated Technical Documentation

- 📐 **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)**: System Architecture, Component Interfaces & 11-Stage Sequence Flow.
- 📘 **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)**: Module Specs, Non-LLM Reliability Formula, Q&A Algorithm & REST API Endpoints.
- 🗄️ **[DATABASE_ER_DIAGRAM.md](DATABASE_ER_DIAGRAM.md)**: Database ER Diagram (Mermaid), Table Schemas & Traceability Foreign Key Constraints.

---

## 1. Project Overview

The **Enterprise AI Research Agent** does NOT rely on single LLM prompts or static mock responses. It executes an 11-stage pipeline:

```text
Research Question
       ↓
Research Planning
       ↓
Source Search
       ↓
Information Collection
       ↓
Source Storage
       ↓
Finding Extraction
       ↓
Evidence Comparison
       ↓
Finding Classification
       ↓
Contradiction Detection
       ↓
Conclusion Generation
       ↓
Traceable Results
```

---

## 2. Key Features

- **Dynamic Research Pipeline**: Works with any enterprise question (e.g., *"How is AI transforming manufacturing operations?"*, *"What AI technologies are changing retail supply chains?"*, *"How is generative AI changing pharmaceutical research?"*).
- **Rule-Based Source Reliability Evaluator**: Non-LLM scoring formula (0–100) evaluating domain TLD, analyst reputation, content depth, recency, and query alignment with transparent audit breakdowns.
- **Strict Evidence Traceability**: Every conclusion links directly to supporting findings, verbatim quotes, original URLs, and reliability scores (**Why this conclusion?**).
- **Contradiction Detection**: Dedicated conflict analysis engine distinguishing true contradictions from contextual variations (different industry, scale, timeframe, or incomplete info).
- **Grounded Research Interrogation (Q&A)**: Interactive chat widget that queries project findings and provides answers backed by clickable citations.
- **Persistent Knowledge Base**: Reusable SQLite/PostgreSQL relational database maintaining cross-project searchability even after system restarts.
- **Zero-Config Offline Fallback**: Features a clean `AIProvider` abstraction that supports Google Gemini API, OpenAI/Groq, and a built-in `HeuristicAIProvider` so the application runs offline with 0 API keys required.

---

## 3. Technology Stack

- **Frontend**: React 18, Vite, Lucide Icons, Vanilla/Tailwind modern CSS design system.
- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic V2, HTTPX, BeautifulSoup4, `ddgs`.
- **Database**: SQLite (default zero-config local db) / PostgreSQL (SQLAlchemy ORM).
- **AI Abstraction**: `AIProvider` supporting Google Gemini API (`google-genai`), OpenAI/Groq (`openai`), and `HeuristicAIProvider` (NLP & keyword clustering fallback).
- **Retrieval**: In-memory & SQLite hybrid BM25 + Cosine similarity vector retriever.

---

## 4. System Architecture

```text
                USER
                  ↓
            React Frontend
            (Port 5173)
                  ↓ REST + Polling Progress
             FastAPI API
            (Port 8000)
                  ↓
        Research Orchestrator
          ↙       ↓       ↘
   Search       AI       Retrieval
 (DuckDuckGo, (Gemini /  (Hybrid BM25 +
  Wikipedia,  Groq /     Vector Store)
   ArXiv)    Heuristic)      ↓
     ↓           ↓      Knowledge Base
     └───────────┴───────────┘
                 ↓
      Relational SQLite / Postgres DB
```

---

## 5. Environment Setup & Configuration

Copy `.env.example` to `.env`:

```bash
# AI Provider Credentials (Optional: Leave empty for built-in Heuristic AI Engine)
GEMINI_API_KEY=
OPENAI_API_KEY=
OPENAI_BASE_URL=
DEFAULT_AI_PROVIDER=auto

# Database Setup
DATABASE_URL=sqlite:///./research_agent.db

# Server Settings
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

---

## 6. How to Run Backend

```bash
cd backend
python -m pip install -r requirements.txt
python run_backend.py
```

Backend will be live at: `http://127.0.0.1:8000`  
Swagger API Docs: `http://127.0.0.1:8000/docs`

---

## 7. How to Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at: `http://localhost:5173`

---

## 8. Database Schema & Models

The relational database contains foreign key relationships across 10 tables:

- `research_projects`: High-level research project metadata and progress status.
- `research_questions`: Deconstructed sub-questions.
- `sources`: Persisted web/academic source metadata, relevance, and reliability scores.
- `source_contents`: Scraped clean text, word counts, and snippets.
- `findings`: Extracted empirical claims categorized into enterprise taxonomies.
- `evidence`: Verbatim quote snippets tied to findings and source records.
- `evidence_comparisons`: Topic clusters and multi-source perspective summaries.
- `contradictions`: Identified conflicts, tension explanations, and type classifications.
- `conclusions`: Executive conclusions with rank order and reasoning summaries.
- `conclusion_findings`: Association table creating explicit traceability links between Conclusions and Findings.
- `research_runs`: Execution audit logs, step durations, and errors.

---

## 9. API Documentation

### Research API
- `POST /api/research`: Create new research project.
- `GET /api/research`: List all projects.
- `GET /api/research/{id}`: Detailed project information.
- `POST /api/research/{id}/run`: Launch background research pipeline.
- `GET /api/research/{id}/progress`: Real-time pipeline stage & logs.
- `GET /api/research/{id}/sources`: Retrieved sources with reliability breakdowns.
- `GET /api/research/{id}/findings`: Extracted findings with verbatim evidence.
- `GET /api/research/{id}/evidence-comparison`: Multi-source perspective synthesis.
- `GET /api/research/{id}/contradictions`: Contradictions and contextual tensions.
- `GET /api/research/{id}/conclusions`: Synthesized conclusions.
- `GET /api/research/{id}/trace/{conclusion_id}`: Conclusion → Finding → Evidence → Source trace tree.
- `POST /api/research/{id}/ask`: Grounded research interrogation Q&A.

### Knowledge Base & System API
- `GET /api/knowledge/search?q=...`: Cross-project knowledge base search.
- `GET /api/system/stats`: Dashboard KPI metrics.
- `GET /api/system/health`: System health check.

---

## 10. Automated Testing

Run unit & integration tests:

```bash
python -m pytest backend/tests
```

Run live end-to-end pipeline test on a real question:

```bash
python backend/test_live_e2e.py
```

---

## 11. Demonstration Flow for Evaluators

1. Open Dashboard (`http://localhost:5173`).
2. Click **"Start New Research"** or enter a new research question:
   > *"What AI technologies are changing retail supply chains?"*
3. Observe live pipeline execution stages (Research Planning → Source Search → Information Collection → Source Storage → Finding Extraction → Evidence Comparison → Contradiction Detection → Conclusion Generation).
4. Review Results:
   - Click **"Why this conclusion?"** on any conclusion card to inspect the exact **Conclusion → Finding → Evidence Quote → Source URL & Reliability Score** chain.
   - Inspect the **Source Reliability Audit** modal showing domain authority, depth, recency, and relevance scoring factors.
   - Interrogate the research project using the **Research Q&A** box ("Which areas have the strongest evidence?").
5. Enter a completely new surprise question (e.g. *"How is generative AI changing pharmaceutical research?"*) and demonstrate zero code change requirements.

---

## 12. Libraries & Licenses

- FastAPI, Uvicorn, SQLAlchemy, Pydantic, HTTPX, BeautifulSoup4, DDGS (MIT / Apache License).
- React, Vite, Lucide React (MIT License).

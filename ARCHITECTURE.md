# Architecture Specification — Enterprise AI Research Agent

## 1. High-Level Architecture Diagram

```text
                                USER
                                  ↓
                     React 18 + Vite Frontend
       (Dashboard | New Research | Live Tracker | Results & Traceability | Q&A | Knowledge Search)
                                  ↓ REST + Polling / Progress
                         FastAPI Backend API
                                  ↓
                      Research Orchestrator
             (Async Background Tasks + Status Pipeline)
     ┌───────────────┬─────────────────┬──────────────────┐
     ↓               ↓                 ↓                  ↓
Web Search      AI Provider       Reliability       Local Retrieval
(DuckDuckGo,  (Gemini / Groq /    Scoring Engine    (Hybrid Lexical +
 Wikipedia,    OpenAI / Local)   (Rule-based TLD,   Semantic Vector Store)
 ArXiv)                           Recency, Depth)         ↓
     │               │                 │                  │
     └───────────────┴────────┬────────┴──────────────────┘
                              ↓
                  Relational SQLite / Postgres
        (Projects, Subquestions, Sources, Findings,
         Evidence, Contradictions, Conclusions, Runs)
                              ↓
                      Research Results
                              ↓
          Traceable Lineage (Evidence + Conclusions)
```

---

## 2. Core Architectural Subsystems

### A. AI Provider Abstraction (`AIProvider`)
The application defines a unified abstract interface for generative AI services:
- `GeminiAIProvider`: Uses Google Gemini API (`google-genai`).
- `OpenAICompatibleProvider`: Supports OpenAI, Groq, Ollama, and OpenRouter endpoints.
- `HeuristicAIProvider`: Smart deterministic NLP fallback engine executing key-sentence extraction, TF-IDF term ranking, and regex categorization for zero-config offline execution.

### B. Rule-Based Source Evaluator
Calculates source reliability scores (0–100) using a transparent rule matrix:
1. **Domain Authority & Source Type (35 pts)**: High-authority TLDs (`.edu`, `.gov`), analyst organizations, enterprise vendors, and commercial news.
2. **Content Depth (25 pts)**: Substantive word count density.
3. **Recency (20 pts)**: Publication year validity.
4. **Topical Relevance (20 pts)**: Query keyword alignment.

### C. Traceability Engine
Maintains strict relational database lineage:
```text
Conclusion (Table: conclusions)
    ↓ (Table: conclusion_findings)
Supporting Finding (Table: findings)
    ↓ (Table: evidence)
Verbatim Quote (Table: evidence)
    ↓ (Table: sources)
Original Source URL & Reliability Score
```

### D. Grounded Research Q&A Interrogation
When a user asks a question about a completed project:
1. The system executes a hybrid BM25 + Vector search over that project's findings and evidence quotes.
2. Only top matching findings are passed into the AI prompt with strict instructions to answer *exclusively* from retrieved facts.
3. The response is returned with clickable source citations.

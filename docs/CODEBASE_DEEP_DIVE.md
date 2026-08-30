# 🔬 LogPilot AI: Deep Code-Level Architecture & Method Guide

This guide provides a comprehensive **code-level breakdown** of every file, class, method, and function in **LogPilot AI**. It explains **WHY** each component was written, **WHAT** problem it solves, and **HOW** the code functions line-by-line.

---

## 📂 1. Core Architecture Map

```text
production_rag/
├── config/
│   └── settings.py          # Centralized configuration tokens & system thresholds
├── data_ingestion/
│   ├── loader.py            # Log & Markdown file loaders
│   ├── splitter.py          # Log-aware & Markdown structural text chunker
│   └── processor.py         # End-to-end ingestion pipeline orchestrator
├── vector_store/
│   ├── base.py              # Abstract Base Vector Store interface
│   ├── embeddings.py        # OpenAI / HuggingFace embedding factory
│   └── faiss_store.py       # FAISS CPU vector index wrapper
├── retrieval/
│   ├── bm25.py              # Sparse keyword search ranker
│   ├── hybrid.py            # Reciprocal Rank Fusion (RRF) dense+sparse engine
│   ├── reranker.py          # Cross-Encoder candidate context reranker
│   ├── filter.py            # Metadata filter engine for microservices
│   └── engine.py            # Context document formatter & prompt builder
├── core/
│   ├── agent_router.py      # Classifier routing queries into operational domains
│   ├── query_rewriter.py    # Multi-turn conversational query contextualizer
│   ├── cache.py             # Sub-10ms semantic cache with cosine similarity
│   ├── guardrail.py         # Dual-stage SafetyGuardian prompt inspection
│   ├── knowledge_graph.py   # Topological microservice dependency graph
│   ├── log_generator.py     # Background real-time log generator thread
│   ├── telemetry.py         # Latency, success rate & telemetry logger
│   └── evaluation.py        # RAGAS-style faithfulness & answer relevance metrics
├── llm/
│   ├── client.py            # Resilient LLM factory (DeepSeek + OpenAI fallback)
│   └── prompts.py           # Universal Specificity system prompt templates
├── app/
│   ├── service.py           # SysOpsRAGService main orchestrator
│   └── api.py               # FastAPI REST endpoints & static frontend server
└── tests/
    ├── verify_full_application.py  # In-process 5-pillar verification suite
    └── test_live_http_api.py       # Live HTTP REST API verification suite
```

---

## 🔬 2. Detailed Class & Method Breakdown

### 🛠️ Module 1: `production_rag/config/settings.py`

#### **Class**: `Settings(BaseSettings)`
- **Why it exists**: Pydantic settings manager that loads environment variables from `.env` or system environment safely with default fallbacks.
- **Key Fields**:
  - `OPENAI_API_KEY`: API key for OpenAI embedding generation & GPT models.
  - `DEEPSEEK_API_KEY`: API key for DeepSeek LLM.
  - `CHUNK_SIZE` (`512`) & `CHUNK_OVERLAP` (`64`): Controls vector embedding chunk granularity.
  - `SEMANTIC_CACHE_THRESHOLD` (`0.88`): Cosine similarity cutoff for returning instant cache hits.

---

### 📥 Module 2: Ingestion & Vector Storage

#### **File**: `production_rag/data_ingestion/splitter.py`
- **Class**: `LogAwareTextSplitter`
  - **Why it exists**: Standard character splitters break log entries in half (e.g. splitting a stack trace across 2 chunks).
  - **Method `split_documents(docs)`**:
    - **Why added**: Identifies log line boundaries (`YYYY-MM-DD`, `[INFO]`, `[ERROR]`) and keeps complete log entries and stack traces intact inside a single chunk.

#### **File**: `production_rag/vector_store/faiss_store.py`
- **Class**: `FAISSVectorStore(BaseVectorStore)`
  - **Why it exists**: High-performance local vector index wrapper around `faiss-cpu`.
  - **Method `build_from_documents(documents)`**:
    - **Why added**: Converts document chunks to 1536-dimensional dense vector embeddings using OpenAI (`text-embedding-3-small`) or HuggingFace and populates the FAISS L2 index.
  - **Method `similarity_search(query, top_k)`**:
    - **Why added**: Calculates Euclidean ($L_2$) distance between query vector and index embeddings, returning top $k$ nearest candidate documents.

---

### 🔍 Module 3: Hybrid Retrieval & Re-Ranking

#### **File**: `production_rag/retrieval/hybrid.py`
- **Class**: `HybridSearchEngine`
  - **Why it exists**: Dense vector search alone misses exact keyword identifiers (e.g. `usr_54272`, `PID 25687`), while keyword search alone misses semantic intent (e.g. *"database is slow"*).
  - **Method `reciprocal_rank_fusion(dense_results, sparse_results, k=60)`**:
    - **Why added**: Implements Reciprocal Rank Fusion (RRF) to merge dense FAISS rankings and sparse Rank-BM25 rankings into a single score:
      $$RRF(d) = \frac{1}{k + rank_{dense}(d)} + \frac{1}{k + rank_{sparse}(d)}$$
  - **Method `search(query, top_k=15)`**:
    - **Why added**: Executes dense FAISS search and sparse BM25 search in parallel, applies RRF scoring, and returns top 15 candidates.

#### **File**: `production_rag/retrieval/reranker.py`
- **Class**: `ContextualReranker`
  - **Why it exists**: Candidate retrieved chunks may contain noise. Re-ranking ensures only the top 5 highest-relevance chunks enter the LLM prompt.
  - **Method `rerank(query, candidates, top_n=5)`**:
    - **Why added**: Uses Cross-Encoder score calculation or term-overlap weighting to select the top $N$ most relevant chunks.

---

### 🧠 Module 4: Intelligent Core Engine

#### **File**: `production_rag/core/agent_router.py`
- **Class**: `AgentQueryRouter`
  - **Why it exists**: Routes SRE queries to specialized domain handlers based on intent.
  - **Method `route_query(query)`**:
    - **Why added**: Evaluates query keywords using regex patterns and returns domain classifications (`DATABASE`, `AUTHENTICATION`, `INFRASTRUCTURE`, `GENERAL_SRE`) along with confidence scores.

#### **File**: `production_rag/core/query_rewriter.py`
- **Class**: `MultiTurnQueryRewriter`
  - **Why it exists**: Users ask follow-up questions like *"how to fix it?"* which lose context without conversational history.
  - **Method `contextualize_query(query, chat_history)`**:
    - **Why added**: Merges user's latest query with previous turns, producing a standalone context-complete search prompt (e.g. *"How to fix Redis OOM maxmemory error?"*).

#### **File**: `production_rag/core/cache.py`
- **Class**: `SemanticCache`
  - **Why it exists**: Repeated operational queries waste 2-4 seconds of LLM execution time.
  - **Method `get(query)`**:
    - **Why added**: Computes cosine similarity between incoming query embedding and cached entry embeddings. If similarity $\ge 0.88$, returns response in **<10ms**.
  - **Method `set(query, answer)`**:
    - **Why added**: Stores clean query embeddings and answers in memory.

#### **File**: `production_rag/core/guardrail.py`
- **Class**: `SafetyGuardian`
  - **Why it exists**: Protects systems against prompt injection and prevents destructive output generation.
  - **Method `inspect_input(query)`**:
    - **Why added**: Scans input for SQL injection (`DROP TABLE`, `DELETE FROM`) and shell exploits (`rm -rf /`).
  - **Method `inspect_output(output)`**:
    - **Why added**: Sanitizes LLM output to ensure no unsafe destructive scripts are displayed without warnings.

#### **File**: `production_rag/core/knowledge_graph.py`
- **Class**: `ServiceKnowledgeGraph`
  - **Why it exists**: Captures microservice mesh topology to explain cascading failures.
  - **Method `format_graph_context(service_name)`**:
    - **Why added**: Injects topological upstream/downstream dependency info into prompt context (e.g. `gateway-proxy` ➔ `auth-service` ➔ `postgres-primary`).

#### **File**: `production_rag/core/log_generator.py`
- **Class**: `RealtimeLogGenerator`
  - **Why it exists**: Simulates live microservice production activity by writing real-time background log streams to disk (`data/logs/*`).

#### **File**: `production_rag/core/telemetry.py`
- **Class**: `TelemetryCollector`
  - **Why it exists**: Tracks operational metrics (latency, cache hit ratios, query success counts).
  - **Method `get_metrics_summary()`**:
    - **Why added**: Computes total queries, average latency, cache hit %, and guardrail blocks for REST API telemetry endpoints.

---

### 🤖 Module 5: LLM Client & Prompts

#### **File**: `production_rag/llm/client.py`
- **Class**: `LLMFactory`
  - **Why it exists**: Provides resilient multi-provider LLM connectivity with automatic fallback.
  - **Method `get_model(temperature=0.0, max_tokens=3000)`**:
    - **Why added**: Initializes `ChatDeepSeek` or `ChatOpenAI` with exponential backoff retries and a **3,000-token output buffer** to eliminate response truncation.

#### **File**: `production_rag/llm/prompts.py`
- **Constant**: `SYSOPS_PRODUCTION_PROMPT`
  - **Why it exists**: Enforces the **Universal Specificity Principle** and mandates:
    1. Exact PID termination commands (`SELECT pg_terminate_backend(25687);`).
    2. Composite index DDL scripts (`CREATE INDEX CONCURRENTLY idx_orders_status_created_at ON orders (status, created_at DESC);`).
    3. Rewritten DML queries with explicit column projections and safe pagination (`LIMIT 100`).
    4. Structured **High-Level Executive Resolution Matrix** table (Immediate P0, Short-Term P1, Long-Term P2).

---

### 🌐 Module 6: Application Orchestrator & REST API

#### **File**: `production_rag/app/service.py`
- **Class**: `SysOpsRAGService`
  - **Why it exists**: Master orchestrator connecting all 5 pillars into a unified execution flow.
  - **Method `process_query(query, chat_history, service_filter)`**:
    - **Why added**:
      1. Clears cache if explicit service filter selected (preventing stale log IDs).
      2. Routes query intent & rewrites context.
      3. Checks semantic cache (<10ms).
      4. Inspects input safety via `SafetyGuardian`.
      5. Runs two-stage Hybrid RRF Search + Cross-Encoder Reranking.
      6. Injects realtime log tail lines from disk (last 40 lines) scoped strictly to query topic.
      7. Invokes LLM with `max_tokens=3000`.
      8. Evaluates RAGAS metrics & returns structured response object.

#### **File**: `production_rag/app/api.py`
- **FastAPI Endpoints**:
  - `POST /api/query`: Handles web UI & external RAG incident queries.
  - `GET /api/logs`: Full 4,600+ line log viewer with real-time tailing and string searching (`search` parameter).
  - `GET /api/telemetry`: Returns system performance metrics.
  - `GET /api/health`: Health check endpoint returning system status.

---

## 💡 3. Summary of Key Implementation Decisions

| Component | Engineering Decision | Reason for Decision |
| :--- | :--- | :--- |
| **Search Engine** | Hybrid RRF (BM25 + FAISS) | Combines dense semantic understanding with exact sparse log identifier matching. |
| **Log Tail Context** | Real-time Disk Tail Injection | Guarantees live SRE log context without re-indexing FAISS vector embeddings every second. |
| **Context Scoping** | Scoped Service Filter | Prevents log context cross-contamination (e.g. Auth errors polluting Redis queries). |
| **Token Limit** | `max_tokens=3000` | Prevents response truncation when rendering multi-step CLI commands and executive tables. |
| **Safety Guardrail** | Dual-Stage Regex Inspection | Blocks destructive SQL (`DROP DATABASE`) and shell commands (`rm -rf`) before execution. |

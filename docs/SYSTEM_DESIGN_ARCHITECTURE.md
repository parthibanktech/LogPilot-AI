# 🏛️ LogPilot AI System Design Architecture (v5.3)

## 📌 Executive Summary
LogPilot AI is an enterprise-grade SRE Copilot built using Python 3.11, FastAPI, FAISS, and LangChain. It uses a **Hybrid Reciprocal Rank Fusion (RRF)** search engine combining sparse BM25 keyword matching with dense FAISS vector search, dynamic disk-log tail injection, and a sub-10ms semantic cache.

---

## 🏗️ 1. Architecture Flow Diagram

```text
[SRE User Query]
       │
       ▼
[Agentic Query Router] ── (Identifies Database / Auth / Infra Intent)
       │
       ▼
[Multi-Turn Context Rewriter]
       │
       ▼
[Sub-10ms Semantic Cache] ── (Returns Instant Hit if Similarity >= 0.88)
       │ (Cache Miss)
       ▼
[SafetyGuardian Guardrail] ── (Blocks SQL Injections & Exploits)
       │ (Pass)
       ▼
[Hybrid Search Engine]
  ├── Dense Vector Search (FAISS-CPU)
  └── Sparse Keyword Search (Rank-BM25)
       │ (Reciprocal Rank Fusion RRF)
       ▼
[Cross-Encoder Reranker] ── (Selects Top 5 Relevant SOP Chunks)
       │
       ▼
[Realtime Log Tail Injector] ── (Appends Last 40 Lines from Disk Log Stream)
       │
       ▼
[GraphRAG Dependency Matrix] ── (Injects Service Mesh Topology)
       │
       ▼
[LLM Synthesis Engine (max_tokens=3000)]
       │
       ▼
[Post-Output Safety Inspection]
       │
       ▼
[RAGAS Evaluation Engine]
       │
       ▼
[Final Response + Executive Resolution Matrix]
```

---

## ⚡ 2. Core System Components

### 1. Two-Stage Hybrid Retrieval
- **Sparse BM25**: Captures exact log line identifiers, user IDs (`usr_54272`), PIDs (`PID 25687`), and IP addresses.
- **Dense FAISS**: Captures high-level semantic intent (*"PostgreSQL query execution time spike"*).
- **RRF Scoring**: Fuses scores using $RRF(d) = \sum \frac{1}{k + r(d)}$.

### 2. Live Log Stream Inspector
- Scans `/data/logs/*` and dynamically extracts live error tails without requiring vector index re-building.

### 3. Sub-10ms Semantic Cache
- Calculates cosine similarity on 1536-dim vector embeddings. Near-identical queries return in **<10ms**.

### 4. Universal Specificity Engine
- Eliminates generic placeholders. Automatically generates composite index DDL scripts (`CREATE INDEX CONCURRENTLY`), exact PID termination (`SELECT pg_terminate_backend(25687)`), and rewritten DML queries with `LIMIT 100`.

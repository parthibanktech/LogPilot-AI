# Enterprise System Design & Architecture Specification: SentinelOps AI (v5.3)
> **Product Codename**: **SentinelOps AI** (formerly SysOps Copilot)  
> **Tagline**: *Enterprise Autonomous Systems Observability & Incident Diagnosis Engine*

This document provides an exhaustive, production-grade technical specification of the **SentinelOps AI Enterprise RAG Architecture**, comparing every module and code component to how **Google (Vertex AI Search & Conversation, Google Cloud Logging, BigQuery, and Spanner)** builds production AI systems at scale.

---

## 🏛️ Executive Naming & System Positioning

| Product Attribute | Specification |
| :--- | :--- |
| **Primary Title** | **SentinelOps AI** |
| **Subtitle** | *Enterprise Autonomous System Observability & Incident Diagnosis Engine* |
| **Architectural Benchmark** | Google Cloud Platform (Vertex AI Search, Cloud Logging, BigQuery, Spanner) |
| **Dataset Scale** | 18,000+ Real-World Log Lines across 14 Microservice Categories |
| **Core Pillars** | 11 Enterprise System Design Pillars (Hybrid RRF, Live Log Tail Injection, GraphRAG, Semantic Cache, RAGAS Eval) |

---

## 🏛️ Executive Architectural Comparison Matrix: Google vs. SentinelOps AI

| Architectural Pillar | Google Enterprise Reference (Vertex AI / GCP) | Our Production Implementation (`production_rag`) | Why It Matters / System Design Rationale |
| :--- | :--- | :--- | :--- |
| **1. Data Ingestion & Log Hierarchy** | Google Cloud Logging Agent (Fluentd) ingests nested logs grouped by `Project/Region/Cluster/Namespace/Service`. | `data_ingestion/loader.py` recursively walks `data/logs/` across 14 nested subfolders (`auth_service/`, `payment_gateway/`, `cloud_infra/`, `database/`, etc.). | Real-world logs are never single flat files; they exist in nested microservice directory trees. |
| **2. Live Realtime Log Tail Injection** | Google Cloud Operations Suite (Stackdriver) streams live tail log windows to Cloud Run / Vertex AI agents. | `app/service.py` dynamically reads the **latest 40 lines** of the actively selected service log file on disk and injects them into the RAG context. | Guarantees the AI diagnoses the **exact User IDs, IPs, and Timestamps** currently generated and visible on the operator's screen. |
| **3. Hybrid Search (Dense + Sparse)** | Vertex AI Search combines Semantic Dense Vectors with Sparse Lexical BM25 Search. | `retrieval/hybrid.py` & `retrieval/bm25.py` execute parallel FAISS vector + BM25 keyword search fused via **Reciprocal Rank Fusion (RRF)**. | Dense vectors miss exact alphanumeric tokens (IP addresses `192.168.1.50`, SQL states `53300`, Exit codes `Exit Code 137`). BM25 guarantees 100% exact token recall. |
| **4. Two-Stage Re-Ranking** | Vertex AI Ranking API re-ranks top 100 candidates down to top 5. | `retrieval/reranker.py` scores candidate chunks using term overlap density and metadata priority to select the top 5 chunks. | Reduces first-stage noise and prevents LLM context contamination. |
| **5. Semantic Response Cache** | Redis / InMemory Cache returning sub-10ms responses for duplicate queries. | `core/cache.py` computes cosine similarity of incoming query vectors. Returns cached answers in **<10ms** if similarity $\ge 0.92$. | Saves LLM token costs, reduces API throttling, and delivers sub-10ms instant UI responses. |
| **6. Microservices GraphRAG** | Spanner Graph / Graph database linking microservice dependencies. | `core/knowledge_graph.py` executes 2-hop BFS traversal across microservice dependency nodes (`gateway-proxy -> auth-service -> postgres-primary`). | Injects upstream/downstream impact relations into LLM prompts for root-cause diagnosis. |
| **7. Agentic Query Router** | Vertex AI Agent Builder routing queries to tools vs search indexes. | `core/agent_router.py` classifies intent to dynamically trigger log inspectors vs SOP playbooks. | Avoids unnecessary vector search for simple status/log tail queries. |
| **8. RAGAS Quality Metrics** | Vertex AI Evaluation Service computing automated quality scores. | `core/evaluation.py` computes Faithfulness, Answer Relevance, and Context Recall metrics. | Continuous offline & online quality telemetry verification. |
| **9. Safety Guardrails** | Google Cloud Armor & Model Armor inspecting prompts for injection. | `core/guardrail.py` scans input/output for prompt injections and unauthorized commands. | Prevents malicious prompt overrides and code injection. |
| **10. Resilience Backoff** | Google Cloud Client Libraries exponential backoff decorator. | `core/resilience.py` retries failed LLM API calls with jittered exponential backoff. | Prevents transient 429/503 errors from breaking downstream execution. |
| **11. Async SSE Streaming** | Cloud Run SSE streaming for token-by-token output delivery. | `app/api.py` streams tokens via `/api/stream_query` and non-blocking threadpools. | Eliminates perceived latency and prevents main event loop blocking. |

# ⚡ LogPilot AI: Autonomous SRE & System Observability Copilot

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![FAISS Vector DB](https://img.shields.io/badge/FAISS-VectorDB-0052CC?style=for-the-badge)](https://faiss.ai)
[![Docker Ready](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)

> **LogPilot AI** is an autonomous Tier-3 Infrastructure Systems & Reliability Engineering Copilot built for real-time microservices log stream analysis, instant incident root cause diagnosis (RCA), and automated parameter-specific SOP playbooks.

---

## 📚 Technical Documentation & Architecture Guides

Detailed deep-dive documentation files are located in the **[`docs/`](./docs)** folder:

| Guide Name | Description | Link |
| :--- | :--- | :--- |
| 🔬 **Codebase Deep Dive** | Deep class-by-class & method-by-method technical code breakdown | [`docs/CODEBASE_DEEP_DIVE.md`](./docs/CODEBASE_DEEP_DIVE.md) |
| 🎓 **System Architecture & Learning** | High-level system design, 5 core pillars, & mathematical RRF formulas | [`docs/SYSTEM_ARCHITECTURE_LEARNING.md`](./docs/SYSTEM_ARCHITECTURE_LEARNING.md) |
| 🚀 **Deployment Guide** | Step-by-step GitHub push, Docker, Railway & Render deployment | [`docs/DEPLOYMENT_GUIDE.md`](./docs/DEPLOYMENT_GUIDE.md) |
| 🏛️ **System Design Blueprint** | Component flow diagram, RAG pipeline, & vector store specifications | [`docs/SYSTEM_DESIGN_ARCHITECTURE.md`](./docs/SYSTEM_DESIGN_ARCHITECTURE.md) |

---

## 🌟 Key Architectural Features & Pillars

```text
                                ┌────────────────────────────────────────┐
                                │     User Query / Log Incident Request   │
                                └───────────────────┬────────────────────┘
                                                    │
                                ┌───────────────────▼────────────────────┐
                                │     Agentic Intent Classification      │
                                └───────────────────┬────────────────────┘
                                                    │
                                ┌───────────────────▼────────────────────┐
                                │   Multi-Turn Contextual Query Rewriter │
                                └───────────────────┬────────────────────┘
                                                    │
                                ┌───────────────────▼────────────────────┐
                                │   Sub-10ms Semantic Cache Check (<10ms)│
                                └───────┬────────────────────────┬───────┘
                           Cache Hit    │                        │ Cache Miss
                                        ▼                        ▼
                       ┌──────────────────────┐  ┌───────────────────────────────────┐
                       │ Sub-10ms Instant Res │  │  Hybrid Search (BM25 + FAISS RRF) │
                       └──────────────────────┘  └─────────────────┬─────────────────┘
                                                                   │
                                                 ┌─────────────────▼─────────────────┐
                                                 │   Cross-Encoder Context Reranker  │
                                                 └─────────────────┬─────────────────┘
                                                                   │
                                                 ┌─────────────────▼─────────────────┐
                                                 │ Live Realtime Log Tail Injection  │
                                                 └─────────────────┬─────────────────┘
                                                                   │
                                                 ┌─────────────────▼─────────────────┐
                                                 │ GraphRAG Topology Dependency Base │
                                                 └─────────────────┬─────────────────┘
                                                                   │
                                                 ┌─────────────────▼─────────────────┐
                                                 │   Grounded Synthesis + Safety     │
                                                 └───────────────────────────────────┘
```

### 🧠 1. Two-Stage Hybrid RRF Search + Cross-Encoder Reranking
- Merges dense vector embeddings (**FAISS-CPU**) and sparse keyword search (**Rank-BM25**) using **Reciprocal Rank Fusion (RRF)**.
- Reranks top 15 candidate chunks down to the top 5 most relevant SOP playbooks and log definitions.

### 🔍 2. Realtime Log Tail Evidence Extraction
- Reads active log files directly from disk (`data/logs/*`) and extracts exact **PIDs**, **User IDs** (`usr_64665`), **Client IPs** (`192.168.1.131`), **Timestamps**, and **Java Stack Traces**.
- Prevents stale log cache returns by dynamically bypassing cache when service filters are active.

### 🌐 3. Microservice GraphRAG Dependency Mapping
- Incorporates topological service dependency maps for microservice meshes (`gateway-proxy` ➔ `auth-service` ➔ `postgres-primary`).

### 🛡️ 4. SafetyGuardian Protocol & Command Inspection
- Scans input prompts and output generations to prevent destructive SQL commands (`DROP DATABASE`, `DELETE FROM`, `rm -rf`) from executing or displaying.

### ⚡ 5. Universal Specificity Principle & Query Rewriting
- **No Generic Placeholders**: Eliminates generic `<your_query>` placeholders across all 14 incident domains (Kafka, Redis, PostgreSQL, OpenSSH, Apache, AWS S3, Kubernetes).
- **SQL DDL & DML Optimization**: Automatically outputs **`CREATE INDEX CONCURRENTLY`** DDL scripts and **rewritten, optimized SQL queries with `LIMIT` pagination** to eliminate unindexed sequential scans (`seq_scan`).
- **High-Level Resolution Matrix**: Formulates structured executive tables categorizing actions into Immediate (P0), Short-Term (P1), and Long-Term (P2) mitigation levels.

---

## 🖥️ Interactive Web Interface

LogPilot AI features a sleek, dark-mode glassmorphism interface:

- **Live Log Inspector**: Full 4,600+ line log viewer with real-time tail stream viewing and a **`🔍 Search User ID / Error...`** full-file search bar.
- **Resolution Console**: Displays grounded incident diagnoses, executive resolution matrices, step-by-step CLI commands, and execution latency benchmarks.
- **High-Level Architecture Blueprint Modal**: Interactive modal showing system pipeline and Google Cloud reference comparisons.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `3.11` (or Python `3.12`)
- **API Key**: `OPENAI_API_KEY` or `DEEPSEEK_API_KEY`

### 1. Local Setup (with `uv` or `pip`)

```bash
# Clone repository
git clone https://github.com/parthibanktech/LogPilot-AI.git
cd LogPilot-AI

# Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 2. Start Application Server

```bash
# Run FastAPI server and background log generator
uvicorn production_rag.app.api:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**!

---

## 🐳 Docker Deployment (`docker-compose`)

Launch the entire containerized application stack in a single command:

```bash
# Set API Key environment variable
export OPENAI_API_KEY="your-openai-api-key-here"

# Build and start container
docker-compose up --build -d
```

Check container health:
```bash
curl http://localhost:8000/api/health
```

---

## ☁️ Cloud Deployment (Render / Railway / Cloud Run)

### 1-Click Render Deployment (`render.yaml`)
1. Push your repository to GitHub.
2. Log into [Render.com](https://render.com) and click **New +** ➔ **Blueprint**.
3. Connect your GitHub repository. Render will automatically read `render.yaml`, build the Docker container, and deploy your live URL!

---

## 🧪 Automated Test Suite Execution

Run the built-in end-to-end verification suite to validate all 5 system design guarantees:

```bash
python tests/verify_full_application.py
```

Run live REST API endpoint validation:
```bash
python tests/test_live_http_api.py
```

---

## 📡 REST API Endpoint Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/health` | `GET` | Health check endpoint returning status and service version |
| `GET /api/logs` | `GET` | Retrieve service logs with parameters `service`, `search`, and `lines` |
| `POST /api/query` | `POST` | Execute RAG incident query diagnosis with `query` and `service_filter` |
| `GET /api/telemetry` | `GET` | Retrieve system latency, success rates, and query telemetry summary |

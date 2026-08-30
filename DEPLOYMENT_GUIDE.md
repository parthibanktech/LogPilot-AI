# 🚀 LogPilot AI: GitHub & Cloud Deployment Guide

Follow this quick step-by-step guide to push your code to GitHub and deploy **LogPilot AI** to the cloud (Render, Railway, or Docker).

---

## 📌 GitHub Repository Details

- **Repository Name**: `LogPilot-AI`
- **GitHub URL**: `https://github.com/parthibanktech/LogPilot-AI.git`
- **Short Description**:
  > `Autonomous SRE & System Observability Copilot powered by Hybrid RRF Search (BM25 + FAISS), Real-time Log Tail Injection, GraphRAG & Sub-10ms Semantic Cache.`

---

## 📤 Step 1: Push Code to GitHub

Open your terminal in the project directory (`d:\AI_AGENT_HACKTHON\5.0\Rag`) and run:

```bash
# Add files and commit
git add .
git commit -m "feat: initial release of LogPilot AI SRE Copilot (v5.3)"

# Push code to GitHub
git push -u origin main
```

---

## ☁️ Step 2: Cloud Deployment Options

### Option A: Railway 1-Click Deployment (Fastest)

1. Log into [Railway.app](https://railway.app).
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Select **`parthibanktech/LogPilot-AI`**.
4. Click **Variables** and add:
   - `OPENAI_API_KEY`: `your_openai_api_key_here`
5. Railway will automatically build the `Dockerfile` and publish your live domain URL!

---

### Option B: Render Cloud Blueprint (`render.yaml`)

1. Log into [Render.com](https://render.com).
2. Click **New +** ➔ **Blueprint**.
3. Connect **`parthibanktech/LogPilot-AI`**.
4. Set `OPENAI_API_KEY` in environment variables and click **Apply**!

---

### Option C: Local / VPS Docker Compose Deployment

```bash
# Set your API Key
export OPENAI_API_KEY="your-api-key-here"

# Build and start container stack
docker-compose up --build -d
```

Verify container status:
```bash
docker ps
```

---

## 🧪 Step 3: Run Verification Suite

### A. Verify Inside Running Docker Container
```bash
# Execute the full 5-pillar verification suite inside the Docker container
docker exec -it logpilot_ai_container python tests/verify_full_application.py
```

### B. Verify Live HTTP Endpoint (Local Docker or Railway Cloud URL)
```bash
# Run HTTP REST API endpoint tests against running server
python tests/test_live_http_api.py
```

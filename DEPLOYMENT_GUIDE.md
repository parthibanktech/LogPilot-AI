# 🚀 LogPilot AI: GitHub & Cloud Deployment Guide

Follow this quick step-by-step guide to create your GitHub repository, push your code, and deploy **LogPilot AI** to the cloud (Render, Railway, or Docker).

---

## 📌 Recommended GitHub Repository Details

When creating your new repository on GitHub:

- **Repository Name**: `LogPilot-AI` (or `logpilot-ai-copilot`)
- **Short Description**:
  > `Autonomous SRE & System Observability Copilot powered by Hybrid RRF Search (BM25 + FAISS), Real-time Log Tail Injection, GraphRAG & Sub-10ms Semantic Cache.`
- **Visibility**: Public (or Private)
- **Topics / Tags**: `sre`, `rag`, `faiss`, `fastapi`, `observability`, `llm`, `ai-agent`, `system-reliability`, `devops`

---

## 📤 Step 1: Push Code to GitHub

Open your terminal in the project directory (`d:\AI_AGENT_HACKTHON\5.0\Rag`) and run:

```bash
# Initialize git repository (if not already initialized)
git init

# Add all project files
git add .

# Commit changes
git commit -m "feat: initial release of LogPilot AI Enterprise SRE Copilot (v5.3)"

# Rename branch to main
git branch -M main

# Link to your new GitHub repository URL
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/LogPilot-AI.git

# Push code to GitHub
git push -u origin main
```

---

## ☁️ Step 2: Cloud Deployment Options

### Option A: Render (1-Click Blueprint - Recommended)

1. Log into [Render.com](https://render.com).
2. Click **New +** ➔ **Blueprint**.
3. Select your `LogPilot-AI` GitHub repository.
4. Render will automatically detect `render.yaml` and set up the Web Service.
5. In Environment Variables, enter your key:
   - `OPENAI_API_KEY`: `your-openai-api-key-here`
6. Click **Apply**. Your app will build and deploy live!

---

### Option B: Docker Container Deployment (`docker-compose`)

For local Docker testing or VPS deployment (AWS EC2, DigitalOcean, Hetzner):

```bash
# Set your API Key
export OPENAI_API_KEY="your-api-key-here"

# Build and start container in detached mode
docker-compose up --build -d
```

Verify deployment:
```bash
curl http://localhost:8000/api/health
```

---

### Option C: Railway 1-Click Deployment

1. Log into [Railway.app](https://railway.app).
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Select `LogPilot-AI`.
4. Add environment variable `OPENAI_API_KEY`.
5. Railway will automatically build the `Dockerfile` and expose your public domain URL!

---

## 🧪 Step 3: Run Verification Suite

To verify that your deployment is 100% healthy:

```bash
python verify_full_application.py
python test_live_http_api.py
```

All 5 verification tests will execute and confirm 100% pass rates!

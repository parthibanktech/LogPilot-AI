"""
production_rag.app.api - FastAPI REST Endpoints & Web Interface (v5.3)
"""

import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

from production_rag.config.settings import settings
from production_rag.app.service import SysOpsRAGService
from production_rag.core.log_generator import log_generator
from production_rag.core.telemetry import telemetry

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SentinelOps AI Enterprise System REST API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service: Optional[SysOpsRAGService] = None

@app.on_event("startup")
def startup_event():
    global rag_service
    print("[FastAPI Startup] Initializing Enterprise RAG Service Engine...")
    rag_service = SysOpsRAGService()
    log_generator.start()

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[Dict[str, str]]] = []
    service_filter: Optional[str] = "all"

class QueryResponse(BaseModel):
    success: bool
    answer: str
    latency_ms: float
    guardrail_triggered: bool
    is_cache_hit: bool
    route_info: Union[str, Dict[str, Any]]
    eval_metrics: Optional[Dict[str, float]] = None

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/api/telemetry")
async def get_telemetry():
    return telemetry.get_metrics_summary()

@app.get("/api/logs")
async def get_logs(service: Optional[str] = Query(None), search: Optional[str] = Query(None), lines: int = Query(300)):
    """Retrieve service logs with accurate subfolder filtering and search capabilities."""
    if not os.path.exists(settings.LOG_DIR):
        return {"logs": "No log directory found.", "services": []}
        
    def fetch_log_content():
        available_services = []
        combined_logs = []
        
        for root, dirs, files in os.walk(settings.LOG_DIR):
            rel_dir = os.path.relpath(root, start=settings.LOG_DIR).replace("\\", "/")
            if rel_dir != ".":
                available_services.append(rel_dir)
                
            for file in files:
                if file.endswith(".log") or file.endswith(".txt"):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, start=settings.LOG_DIR).replace("\\", "/")
                    
                    if service and service.lower() != "all":
                        if service.lower() not in rel_path.lower():
                            continue
                        
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            all_lines = f.readlines()
                            
                            if search and search.strip():
                                query_str = search.strip().lower()
                                matched_blocks = []
                                for idx, l in enumerate(all_lines):
                                    if query_str in l.lower():
                                        start_idx = max(0, idx - 2)
                                        end_idx = min(len(all_lines), idx + 6)
                                        snippet = "".join(all_lines[start_idx:end_idx])
                                        matched_blocks.append(f"--- MATCH AT LINE {idx + 1} ---\n" + snippet)
                                        
                                if matched_blocks:
                                    combined_logs.append(f"=== SEARCH RESULTS IN: {rel_path} ({len(matched_blocks)} Matches) ===\n" + "\n".join(matched_blocks[:20]))
                                else:
                                    combined_logs.append(f"=== NO SEARCH MATCHES FOR '{search}' IN {rel_path} ===")
                            else:
                                recent_lines = "".join(all_lines[-lines:])
                                combined_logs.append(f"=== SERVICE LOG: {rel_path} (Last {lines} Lines / Total {len(all_lines)} Lines) ===\n" + recent_lines)
                    except Exception as e:
                        print(f"Error reading log file {path}: {e}")
                        
        return {
            "logs": "\n\n".join(combined_logs) if combined_logs else "No logs found matching selected service filter.",
            "services": sorted(list(set(available_services)))
        }
        
    res = await run_in_threadpool(fetch_log_content)
    return res

@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG Service initializing...")
    res = await run_in_threadpool(rag_service.process_query, req.query, req.chat_history, req.service_filter)
    return res

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    frontend_path = os.path.join(settings.BASE_DIR, "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SentinelOps AI Enterprise Web Interface</h1><p>Frontend file index.html not found.</p>"

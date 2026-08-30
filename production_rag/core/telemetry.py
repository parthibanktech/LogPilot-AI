"""
production_rag.core.telemetry - RAG Observability & Monitoring Tracker
"""

import os
import json
import time
from datetime import datetime
from production_rag.config.settings import settings

class TelemetryLogger:
    """Logs system metrics, latency, token usage, and retrieval success."""
    
    def __init__(self, log_path=settings.TELEMETRY_PATH):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump([], f)
                
    def log_query_event(self, query: str, latency_ms: float, chunks_retrieved: int, status: str, guardrail_triggered: bool):
        """Append a telemetry metric event."""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": query[:100],  # Truncate query for privacy/space
            "latency_ms": round(latency_ms, 2),
            "chunks_retrieved": chunks_retrieved,
            "status": status,
            "guardrail_triggered": guardrail_triggered
        }
        
        try:
            with open(self.log_path, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = []
                data.append(event)
                # Keep last 100 metric events
                if len(data) > 100:
                    data = data[-100:]
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Telemetry Error] Failed to log event: {e}")
            
    def get_metrics_summary(self) -> dict:
        """Calculate recent telemetry stats for the dashboard."""
        if not os.path.exists(self.log_path):
            return {"total_queries": 0, "avg_latency_ms": 0, "success_rate": 100}
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return {"total_queries": 0, "avg_latency_ms": 0, "success_rate": 100}
                
            total = len(data)
            avg_latency = sum(d.get("latency_ms", 0) for d in data) / total
            successes = sum(1 for d in data if d.get("status") == "SUCCESS")
            return {
                "total_queries": total,
                "avg_latency_ms": round(avg_latency, 2),
                "success_rate": round((successes / total) * 100, 1),
                "recent_events": data[-5:]
            }
        except Exception:
            return {"total_queries": 0, "avg_latency_ms": 0, "success_rate": 100}

telemetry = TelemetryLogger()

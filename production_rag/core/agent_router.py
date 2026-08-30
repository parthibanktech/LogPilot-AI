"""
production_rag.core.agent_router - Agentic Intent Classifier & Query Router
"""

import re
from typing import Dict

class AgentQueryRouter:
    """Agentic decision engine routing queries to targeted tools or full hybrid RAG pipelines."""
    
    @staticmethod
    def route_query(query: str) -> Dict[str, str]:
        """Classify query intent and return routing strategy."""
        query_lower = query.lower()
        
        # 1. Log Inspection Tool
        if any(kw in query_lower for kw in ["show logs", "recent log", "log stream", "filter log"]):
            return {
                "route": "LOG_INSPECTION_TOOL",
                "reason": "Query requests raw log stream inspection."
            }
            
        # 2. SOP Playbook Tool
        if any(kw in query_lower for kw in ["sop", "playbook", "standard operating procedure", "runbook"]):
            return {
                "route": "SOP_PLAYBOOK_TOOL",
                "reason": "Query requests operational playbook procedure."
            }
            
        # 3. Default: Full Hybrid Agentic Diagnostic Pipeline
        return {
            "route": "HYBRID_DIAGNOSTIC_PIPELINE",
            "reason": "Query requires full incident diagnosis (Logs + SOPs)."
        }

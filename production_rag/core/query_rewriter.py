"""
production_rag.core.query_rewriter - Multi-Turn Conversational Query Contextualizer
"""

from typing import List, Dict

class MultiTurnQueryRewriter:
    """Rewrites ambiguous follow-up questions into standalone explicit search queries using chat history."""
    
    @staticmethod
    def contextualize_query(current_query: str, chat_history: List[Dict[str, str]]) -> str:
        """If current_query is ambiguous (e.g. 'How to fix it?'), append context from recent messages."""
        if not chat_history:
            return current_query
            
        current_lower = current_query.lower().strip()
        ambiguous_triggers = [
            "it", "that", "this error", "the issue", "how to fix it", 
            "what was the ip", "same problem", "resolution", "commands"
        ]
        
        is_ambiguous = any(trigger in current_lower for trigger in ambiguous_triggers)
        if not is_ambiguous:
            return current_query
            
        # Extract last user query or assistant response snippet
        last_context = ""
        for msg in reversed(chat_history[-4:]):
            if msg.get("role") == "user":
                last_context = msg.get("content", "")
                break
                
        if last_context:
            rewritten_query = f"{current_query} (Context regarding previous incident: {last_context})"
            return rewritten_query
            
        return current_query

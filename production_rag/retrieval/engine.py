"""
production_rag.retrieval.engine - Retrieval Engine & Formatter
"""

from typing import List
from langchain_core.documents import Document

class RetrievalEngine:
    """Manages document retrieval and formatting for context injection."""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        
    def get_retriever(self, k: int = 5):
        return self.vector_store.as_retriever(k=k)
        
    @staticmethod
    def format_context_documents(docs: List[Document]) -> str:
        """Format retrieved documents with structured header demarcations."""
        formatted_list = []
        for doc in docs:
            stype = doc.metadata.get("source_type", "unknown")
            source = doc.metadata.get("source", "file")
            
            if stype == "log":
                line_start = doc.metadata.get("line_start", "N/A")
                severities = ", ".join(doc.metadata.get("severities", []))
                formatted_list.append(
                    f"--- REALTIME LOG BLOCK ({source}, Line {line_start}, Levels: [{severities}]) ---\n"
                    f"{doc.page_content}"
                )
            else:
                formatted_list.append(
                    f"--- OPERATIONAL PLAYBOOK / SOP EXCERPT ({source}) ---\n"
                    f"{doc.page_content}"
                )
        return "\n\n".join(formatted_list)

"""
production_rag.retrieval.filter - Metadata & ISO Timestamp Pre-Filtering Engine
"""

import re
from typing import List, Optional
from langchain_core.documents import Document

class MetadataFilterEngine:
    """Pre-filters document chunks based on metadata (service, severity, timestamp range)."""
    
    @staticmethod
    def filter_documents(
        documents: List[Document],
        service_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        start_time_iso: Optional[str] = None,
        end_time_iso: Optional[str] = None
    ) -> List[Document]:
        """Apply metadata filtering criteria while preserving SOP playbooks."""
        filtered = documents
        
        # 1. Filter by Service (Always preserve SOP Playbooks for Incident Resolution)
        if service_filter and service_filter.lower() != "all":
            sf = service_filter.lower()
            filtered = [
                doc for doc in filtered 
                if sf in doc.metadata.get("service", "").lower()
                or sf in doc.metadata.get("source", "").lower()
                or doc.metadata.get("type", "").lower() == "sop"
                or "sop" in doc.metadata.get("source", "").lower()
            ]
            
        # 2. Filter by Severity Level
        if severity_filter:
            filtered = [
                doc for doc in filtered 
                if severity_filter.lower() in doc.page_content.lower()
                or doc.metadata.get("type", "").lower() == "sop"
            ]
            
        # 3. Filter by ISO Timestamp Range
        if start_time_iso or end_time_iso:
            time_filtered = []
            for doc in filtered:
                if doc.metadata.get("type", "").lower() == "sop":
                    time_filtered.append(doc)
                    continue
                    
                timestamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", doc.page_content)
                if not timestamps:
                    time_filtered.append(doc)
                    continue
                    
                doc_time = timestamps[0]
                if start_time_iso and doc_time < start_time_iso:
                    continue
                if end_time_iso and doc_time > end_time_iso:
                    continue
                time_filtered.append(doc)
                
            filtered = time_filtered
            
        return filtered if filtered else documents  # Soft fallback if filters return empty

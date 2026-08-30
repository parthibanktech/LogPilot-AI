"""
production_rag.data_ingestion.processor - Ingestion Orchestrator Pipeline
"""

from typing import List
from langchain_core.documents import Document
from production_rag.config.settings import settings
from production_rag.data_ingestion.loader import SOPLoader, SystemLogLoader
from production_rag.data_ingestion.splitter import DocumentSplitterManager

class IngestionPipeline:
    """Orchestrates loading and chunking of SOPs and logs."""
    
    def __init__(self, sop_path: str = settings.SOP_PATH, log_dir: str = settings.LOG_DIR):
        self.sop_path = sop_path
        self.log_dir = log_dir
        
    def run(self) -> List[Document]:
        """Execute full loading and chunking pipeline."""
        # Load raw docs
        sop_raw = SOPLoader(self.sop_path).load()
        log_raw = SystemLogLoader(self.log_dir).load()
        
        # Chunk docs
        sop_chunks = DocumentSplitterManager.split_sop_documents(sop_raw)
        log_chunks = DocumentSplitterManager.split_log_documents(log_raw)
        
        total_chunks = sop_chunks + log_chunks
        return total_chunks

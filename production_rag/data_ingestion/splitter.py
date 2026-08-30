"""
production_rag.data_ingestion.splitter - Custom Chunking Strategies
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from production_rag.config.settings import settings

class DocumentSplitterManager:
    """Manages chunking logic for various document types."""
    
    @staticmethod
    def split_sop_documents(documents: List[Document]) -> List[Document]:
        """Split Markdown SOPs while respecting header structures."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "]
        )
        return splitter.split_documents(documents)
        
    @staticmethod
    def split_log_documents(documents: List[Document], window_size: int = 5, overlap: int = 2) -> List[Document]:
        """Split raw logs into overlapping blocks to maintain context continuity."""
        log_chunks = []
        for doc in documents:
            lines = doc.page_content.strip().split("\n")
            i = 0
            while i < len(lines):
                chunk_lines = lines[i : i + window_size]
                chunk_content = "[Server Log Event Window]\n" + "\n".join(chunk_lines)
                
                # Metadata enrichment: extract severity levels present in chunk
                severities = []
                for level in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
                    if any(level in line for line in chunk_lines):
                        severities.append(level)
                        
                chunk_doc = Document(
                    page_content=chunk_content,
                    metadata={
                        "source": doc.metadata.get("source", "system_logs.log"),
                        "source_type": "log",
                        "line_start": i + 1,
                        "severities": severities
                    }
                )
                log_chunks.append(chunk_doc)
                i += window_size - overlap
                if i >= len(lines) - 1:
                    break
        return log_chunks

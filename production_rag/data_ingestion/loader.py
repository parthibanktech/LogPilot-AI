"""
production_rag.data_ingestion.loader - Data Loaders for SOPs and Server Logs
"""

import os
from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

class BaseDocumentLoader(ABC):
    """Abstract base loader interface."""
    @abstractmethod
    def load(self) -> List[Document]:
        pass

class SOPLoader(BaseDocumentLoader):
    """Loader for IT Standard Operating Procedures (Markdown)."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def load(self) -> List[Document]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"SOP file not found: {self.file_path}")
        loader = TextLoader(self.file_path, encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_type"] = "sop"
        return docs

class SystemLogLoader(BaseDocumentLoader):
    """Loader for Raw Server / System Logs (supports nested log directory hierarchies)."""
    def __init__(self, target_path: str):
        self.target_path = target_path
        
    def load(self) -> List[Document]:
        if not os.path.exists(self.target_path):
            raise FileNotFoundError(f"Log path not found: {self.target_path}")
            
        documents = []
        if os.path.isfile(self.target_path):
            file_paths = [self.target_path]
        else:
            file_paths = []
            for root, _, files in os.walk(self.target_path):
                for f in files:
                    if f.endswith(".log") or f.endswith(".txt"):
                        file_paths.append(os.path.join(root, f))
                        
        for path in file_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                rel_path = os.path.relpath(path, start=os.path.dirname(self.target_path))
                service_name = os.path.basename(os.path.dirname(path))
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": rel_path,
                        "service": service_name,
                        "source_type": "log"
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"[Loader Warning] Could not read log file {path}: {e}")
                
        return documents

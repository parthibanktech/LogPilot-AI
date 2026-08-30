"""
production_rag.vector_store.base - Base Vector Store Interface
"""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document

class BaseVectorStore(ABC):
    """Abstract interface for vector store providers (FAISS, Chroma, Pinecone)."""
    
    @abstractmethod
    def build_from_documents(self, documents: List[Document]):
        pass
        
    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[Document]:
        pass
        
    @abstractmethod
    def as_retriever(self, k: int = 5):
        pass

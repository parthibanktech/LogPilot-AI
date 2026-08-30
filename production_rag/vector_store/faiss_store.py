"""
production_rag.vector_store.faiss_store - FAISS Vector Database Adapter with Disk Persistence
"""

import os
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from production_rag.vector_store.base import BaseVectorStore
from production_rag.vector_store.embeddings import ResilientEmbeddings

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

INDEX_SAVE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index"))

class FAISSVectorStore(BaseVectorStore):
    """FAISS vector database implementation with disk persistence."""
    
    def __init__(self):
        self.embeddings = ResilientEmbeddings().get_underlying_embeddings()
        self.db = None
        
    def build_from_documents(self, documents: List[Document]):
        """Construct or load cached FAISS index from disk."""
        if os.path.exists(INDEX_SAVE_PATH) and os.path.exists(os.path.join(INDEX_SAVE_PATH, "index.faiss")):
            try:
                print(f"[Vector Store] Loading FAISS index from disk ({INDEX_SAVE_PATH})...")
                self.db = FAISS.load_local(INDEX_SAVE_PATH, self.embeddings, allow_dangerous_deserialization=True)
                return self.db
            except Exception as e:
                print(f"[Vector Store Warning] Failed to load index from disk: {e}. Rebuilding...")
                
        print("[Vector Store] Building new FAISS index from documents...")
        self.db = FAISS.from_documents(documents, self.embeddings)
        try:
            os.makedirs(INDEX_SAVE_PATH, exist_ok=True)
            self.db.save_local(INDEX_SAVE_PATH)
            print(f"[Vector Store] Saved FAISS index to disk ({INDEX_SAVE_PATH}).")
        except Exception as e:
            print(f"[Vector Store Warning] Could not save index to disk: {e}")
            
        return self.db
        
    def search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search."""
        if not self.db:
            raise ValueError("Vector database is not built.")
        return self.db.similarity_search(query, k=k)
        
    def as_retriever(self, k: int = 5):
        """Return standard LangChain retriever interface."""
        if not self.db:
            raise ValueError("Vector database is not built.")
        return self.db.as_retriever(search_kwargs={"k": k})

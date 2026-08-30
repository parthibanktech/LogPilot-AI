"""
production_rag.vector_store.embeddings - Embeddings Adapter with Resilience
"""

from langchain_openai import OpenAIEmbeddings
from production_rag.config.settings import settings
from production_rag.core.resilience import retry_with_backoff

class ResilientEmbeddings:
    """Wraps embedding calls with automatic retry on failure."""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY missing in environment.")
        self._provider = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def embed_documents(self, texts):
        return self._provider.embed_documents(texts)
        
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def embed_query(self, text):
        return self._provider.embed_query(text)
        
    def get_underlying_embeddings(self):
        return self._provider

"""
production_rag.llm.client - Resilient LLM Client Factory (v5.3)
"""

from production_rag.config.settings import settings
from production_rag.core.resilience import retry_with_backoff

class LLMFactory:
    """Factory for chat models supporting DeepSeek and OpenAI fallback."""
    
    @staticmethod
    def get_provider_name() -> str:
        if settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != "your_deepseek_key":
            return "DeepSeek"
        if settings.OPENAI_API_KEY:
            return "OpenAI"
        return "None"
        
    @staticmethod
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def get_model(temperature: float = 0.0, max_tokens: int = 3000):
        provider = LLMFactory.get_provider_name()
        if provider == "DeepSeek":
            from langchain_deepseek import ChatDeepSeek
            return ChatDeepSeek(
                model=settings.DEEPSEEK_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=settings.DEEPSEEK_API_KEY
            )
        elif provider == "OpenAI":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=settings.OPENAI_API_KEY
            )
        else:
            raise RuntimeError("No valid LLM API key (DEEPSEEK_API_KEY or OPENAI_API_KEY) found.")

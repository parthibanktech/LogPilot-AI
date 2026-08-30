"""
models - One place that decides which model we talk to

Every lab imports from here, so no lab hard-codes a provider.

  Chat model : DeepSeek first. If its key is missing, we use OpenAI instead.
  Embeddings : OpenAI text-embedding-3-small.

Why embeddings are always OpenAI: DeepSeek does not offer an embeddings API.
Retrieval in this mission needs embeddings, so OPENAI_API_KEY is required here
even when DeepSeek is answering the questions.

You do not run this file. The labs import it.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"


def deepseek_key():
    key = os.getenv("DEEPSEEK_API_KEY", "")
    return key.strip()


def openai_key():
    key = os.getenv("OPENAI_API_KEY", "")
    return key.strip()


def which_provider():
    """Return the name of the chat provider we will actually use."""
    if deepseek_key() != "" and deepseek_key() != "your_deepseek_api_key_here":
        return "DeepSeek"
    if openai_key() != "":
        return "OpenAI"
    return "none"


def get_model(temperature=0.0, max_tokens=800):
    """Return a chat model. DeepSeek if we have its key, otherwise OpenAI."""
    provider = which_provider()
    if provider == "DeepSeek":
        from langchain_deepseek import ChatDeepSeek
        return ChatDeepSeek(model=DEEPSEEK_MODEL, temperature=temperature, max_tokens=max_tokens)
    if provider == "OpenAI":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=OPENAI_MODEL, temperature=temperature, max_tokens=max_tokens)
    print("No model key found. Please run 00_setup_check.py first.")
    raise SystemExit()


def get_embeddings():
    """Return the embedding model used to turn text into searchable numbers."""
    if openai_key() == "":
        print("No OPENAI_API_KEY found. Retrieval needs it. Run 00_setup_check.py first.")
        raise SystemExit()
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)

"""
05 - A Vector Database (FAISS)

In file 04 you compared the question against every chunk in a Python loop.
That is fine for four chunks. It is hopeless for ten million.

FAISS does exactly what your loop did, but built for scale. You hand it the
chunks, it embeds them and stores the vectors, and it answers searches fast.

FAISS runs inside your program with no server to start. Chroma, Pinecone,
Qdrant and pgvector are the same idea, some of them as a separate service.

RUN:
    uv run 05_introducing_faiss.py
"""

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"   # keeps FAISS quiet on Windows

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


from models import get_embeddings

print("====================================================================")
print("STEP 5 - PUTTING THE CHUNKS IN A VECTOR DATABASE")
print("====================================================================")

raw_document = """
LANGCHAIN BASICS
LangChain is a framework for developing applications powered by language models.
It enables applications that are context-aware and reason.

VECTOR DATABASES
A vector database indexes and stores vector embeddings for fast retrieval and similarity search.
Popular vector databases include Pinecone, Weaviate, Chroma, and FAISS.

RAG (RETRIEVAL-AUGMENTED GENERATION)
RAG retrieves facts from an external knowledge base to ground large language models.
It limits hallucinations.
"""

print("")
print("[..] Splitting the document into chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
doc = Document(page_content=raw_document.strip())
chunks = splitter.split_documents([doc])
print("[OK] " + str(len(chunks)) + " chunks.")

print("")
print("[..] Embedding every chunk and building the database...")

# This one line does the whole of file 04 for you: it loops over the chunks,
# embeds each one, and stores the vectors next to the original text.
vector_db = FAISS.from_documents(chunks, get_embeddings())

print("[OK] FAISS database built, held in memory.")

query = "What exactly is RAG?"
print("")
print("Question:", query)
print("[..] Asking the database for the 2 closest chunks...")

results = vector_db.similarity_search(query, k=2)

number = 1
for result in results:
    print("")
    print("--- Match " + str(number) + " ---")
    print(result.page_content.strip())
    number = number + 1

print("")
print("k=2 means 'give me the 2 closest'. You choose that number, and it is a")
print("real decision: too few and you miss the answer, too many and you pay")
print("for noise. We will use it again in every file from here.")

print("")
print("====================================================================")
print("Ask your own questions. The database returns the 2 closest chunks.")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break
    found = vector_db.similarity_search(typed, k=2)
    position = 1
    for item in found:
        print("  Match " + str(position) + ":", item.page_content.strip().replace("\n", " "))
        position = position + 1 

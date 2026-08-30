"""
08 - The Retriever

A vector database has many settings. A retriever wraps it and exposes ONE
method you already know: .invoke(question) gives back a list of documents.

That matters because it makes the database swappable. Your code asks a
retriever for documents; whether FAISS, Chroma or Pinecone sits behind it is
not your program's business. It is the same idea as MCP in Mission 3: a
standard interface so the thing behind it can change.

RUN:
    uv run 08_the_retriever_abstraction.py
"""

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from models import get_embeddings

print("====================================================================")
print("STEP 8 - ONE STANDARD WAY TO ASK FOR DOCUMENTS")
print("====================================================================")

docs = [
    Document(page_content="Python was created by Guido van Rossum."),
    Document(page_content="Java was originally developed by James Gosling at Sun Microsystems."),
    Document(page_content="JavaScript was invented by Brendan Eich in 10 days."),
]

print("")
print("[..] Building a small FAISS database...")
db = FAISS.from_documents(docs, get_embeddings())
print("[OK] Database ready.")

# search_kwargs={"k": 1} means "return only the single best match".
retriever = db.as_retriever(search_kwargs={"k": 1})

query = "Who made JavaScript?"
print("")
print("Question:", query)

# Notice .invoke(). The same verb you use for a model, a prompt and a chain.
found = retriever.invoke(query)

for document in found:
    print("[OK] Retrieved:", document.page_content)

print("")
print("The retriever gave back a list of documents from one .invoke() call.")
print("Swap FAISS for another database tomorrow and this line does not change.")

print("")
print("====================================================================")
print("Ask about Python, Java or JavaScript. The retriever returns 1 document.")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break
    for document in retriever.invoke(typed):
        print("  Retrieved:", document.page_content)

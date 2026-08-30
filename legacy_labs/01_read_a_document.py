"""
01 - Read a Document

An agent cannot answer questions about a document it has never read. So the
first step of RAG is the least glamorous one: get the text off the disk and
into Python.

LangChain calls the result a Document: the text itself, plus metadata saying
where it came from. That "where from" is what lets you cite a source later.

RUN:
    uv run 01_read_a_document.py
"""

import os

from langchain_community.document_loaders import TextLoader

print("====================================================================")
print("STEP 1 - LOADING A DOCUMENT")
print("====================================================================")

file_path = os.path.join("data", "handbook.txt")

if os.path.exists(file_path) is False:
    print("[!!] Could not find " + file_path)
    print("     Run this file from the mission5 folder.")
    raise SystemExit()

# First, read it as plain Python would, so you can see there is no magic.
print("")
print("--- The raw file, read by ordinary Python ---")
handle = open(file_path, "r", encoding="utf-8")
print(handle.read())
handle.close()

# Now the LangChain way. A loader turns a file into Document objects.
print("--- The same file, loaded by LangChain ---")
loader = TextLoader(file_path, encoding="utf-8")
docs = loader.load()

print("[OK] Loaded " + str(len(docs)) + " document(s).")

doc = docs[0]
print("")
print("Source recorded in metadata:", doc.metadata["source"])
print("First 100 characters:", doc.page_content[:100] + "...")

print("")
print("A Document is just text plus metadata. The metadata is how you tell a")
print("user WHERE an answer came from, which is what makes RAG trustworthy.")

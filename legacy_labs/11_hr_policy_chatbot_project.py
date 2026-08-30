"""
11 - Project: An HR Chatbot Over a Real PDF

Everything so far used text we typed into the file. This one reads an actual
PDF from disk, the kind HR really sends round, and answers questions about it
in a terminal chat.

Two things change once the document is real:
    the PDF has page numbers, so answers can cite a page
    the text is long, so chunking and k start to matter

Type your questions. Type exit to stop.

RUN:
    uv run 11_hr_policy_chatbot_project.py
"""

import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from models import get_model, get_embeddings, which_provider

print("====================================================================")
print("PROJECT - HR CHATBOT OVER A REAL PDF")
print("Running on:", which_provider())
print("====================================================================")

PDF_PATH = "HR_Policy.pdf"

if os.path.exists(PDF_PATH) is False:
    print("[!!] Could not find " + PDF_PATH)
    print("     Run this file from the mission5 folder.")
    sys.exit(1)

print("")
print("[..] 1. Reading the PDF...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()
print("[OK] " + str(len(documents)) + " pages.")

print("[..] 2. Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(documents)
print("[OK] " + str(len(chunks)) + " chunks.")

print("[..] 3. Embedding them and building the database...")
print("     (this is the slow step, and it happens once)")
db = FAISS.from_documents(chunks, get_embeddings())
retriever = db.as_retriever(search_kwargs={"k": 4})
print("[OK] Knowledge base ready.")

HR_TEMPLATE = """You are HR-Bot, an assistant for employees.

POLICY EXCERPTS:
{context}

QUESTION: {question}

Answer using only the excerpts above. If they contain the answer, give it
plainly and mention the page. Only if the answer is genuinely absent, reply:
I cannot find that in the handbook. Please contact HR directly.
"""

prompt = PromptTemplate.from_template(HR_TEMPLATE)


def format_docs(docs):
    """Show each excerpt with its page number, so the answer can cite it."""
    lines = []
    for doc in docs:
        page = doc.metadata.get("page", "unknown")
        lines.append("[Page " + str(page) + "]\n" + doc.page_content)
    return "\n\n".join(lines)


chatbot = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | get_model(temperature=0.0, max_tokens=400)
    | StrOutputParser()
)

print("")
print("Ask about the policy. Type 'exit' to stop.")
print("====================================================================")

while True:
    question = input("\nYou: ").strip()
    if question == "":
        continue
    if question.lower() == "exit" or question.lower() == "quit":
        print("Bye.")
        break
    answer = chatbot.invoke(question)
    print("HR-Bot:", answer.strip())

"""
10 - Project: A Contract Assistant

Everything from files 01 to 09, on a real job.

A contract is a good test for RAG. The answers are in there, but they are
buried in clause language, and getting one wrong matters. Notice the last
question in the run: it asks about something the contract never mentions.
Refusing that one is the most important result in this file.

RUN:
    uv run 10_legal_agent_project.py
"""

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from models import get_model, get_embeddings, which_provider

print("====================================================================")
print("PROJECT - A CONTRACT ASSISTANT")
print("Running on:", which_provider())
print("====================================================================")

contract_text = """
MASTER SERVICES AGREEMENT

1. TERM AND TERMINATION.
This Agreement shall commence on January 1, 2026, and shall continue for a period
of one (1) year. Either party may terminate this Agreement without cause upon
sixty (60) days prior written notice.

2. PAYMENT TERMS.
Client shall pay Contractor within thirty (30) days of receiving an invoice.
Late payments will incur an interest charge of 1.5% per month. Invoices must be
submitted on the first business day of the month.

3. CONFIDENTIALITY.
Both parties agree to hold all proprietary information in strict confidence for a
period of five (5) years following the termination of this Agreement. Confidential
Information includes trade secrets, customer lists, and financial data.

4. INDEMNIFICATION.
Contractor agrees to indemnify and hold harmless Client from any claims arising
from Contractor's gross negligence or willful misconduct. This indemnification
is capped at $500,000.
"""

print("")
print("[..] Reading the contract and building the database...")

splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=60)
doc = Document(page_content=contract_text.strip(), metadata={"source": "MSA_Contract_2026"})
chunks = splitter.split_documents([doc])

db = FAISS.from_documents(chunks, get_embeddings())
retriever = db.as_retriever(search_kwargs={"k": 3})

print("[OK] " + str(len(chunks)) + " clauses indexed.")

# Context first, question next, rules last. Same shape as files 07 and 09.
LEGAL_TEMPLATE = """You are a legal assistant reviewing a contract.

CONTRACT CLAUSES:
{context}

QUESTION: {question}

Answer using only the clauses above, and follow these rules:
1. If the clauses do not cover it, say exactly: The contract does not specify this.
2. Cite the section you used.
3. Keep the answer under three sentences.
"""

prompt = PromptTemplate.from_template(LEGAL_TEMPLATE)


def format_docs(docs):
    """Show each clause with the document it came from, so answers can cite it."""
    lines = []
    for doc in docs:
        lines.append("[Source: " + doc.metadata["source"] + "]\n" + doc.page_content)
    return "\n\n".join(lines)


assistant = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | get_model(temperature=0.0, max_tokens=300)
    | StrOutputParser()
)

questions = [
    "How much notice is required to terminate the contract?",
    "What happens if I pay an invoice late?",
    "For how long must confidential information be kept secret?",
    "Who owns the intellectual property created during this contract?",
]

for question in questions:
    print("")
    print("--------------------------------------------------------------------")
    print("Q:", question)
    answer = assistant.invoke(question)
    print("A:", answer.strip())

print("")
print("====================================================================")
print("Look at the last answer again. The contract says nothing about")
print("intellectual property, and the assistant said so instead of inventing")
print("a clause. On a real contract that refusal is worth more than the")
print("three answers above it.")

print("")
print("====================================================================")
print("Now ask your own questions about the contract.")
print("Try something it does covers, then something it does not.")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break
    print("Assistant:", assistant.invoke(typed).strip())

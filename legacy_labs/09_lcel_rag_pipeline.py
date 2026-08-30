"""
09 - The Same RAG, As a Pipeline

File 07 did RAG by hand: search, build a string, paste, call the model. It
worked, and it was a page of code you would have to repeat every time.

Here the same four steps become one chain, joined with the | symbol you met in
Mission 1. Read each | as the word "then".

    retrieve  then  fill the prompt  then  ask the model  then  clean the text

One .invoke() runs the lot.

RUN:
    uv run 09_lcel_rag_pipeline.py
"""

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from models import get_model, get_embeddings, which_provider

print("====================================================================")
print("STEP 9 - RAG AS A PIPELINE")
print("Running on:", which_provider())
print("====================================================================")

policy_docs = [
    Document(page_content="TechCorp Dress Code: Business casual on Monday to Thursday.",
             metadata={"source": "HR_Policy.txt"}),
    Document(page_content="TechCorp Remote Policy: Remote work is permitted unconditionally for 2 days each week, on Tuesdays and Thursdays.",
             metadata={"source": "HR_Policy.txt"}),
    Document(page_content="TechCorp IT Policy: Do not install personal games on company laptops.",
             metadata={"source": "IT_Policy.txt"}),
]

print("")
print("[..] Building the database and the retriever...")
db = FAISS.from_documents(policy_docs, get_embeddings())
retriever = db.as_retriever(search_kwargs={"k": 2})

# Same prompt shape as file 07: context first, question next, instruction last.
# The {context} and {question} are blanks the chain fills in.
RAG_TEMPLATE = """You are an HR assistant.

CONTEXT FROM THE POLICY:
{context}

QUESTION: {question}

Answer the question using only the context above. If the context contains the
answer, state it plainly. Only if it is genuinely absent, reply: I cannot find
this in the policy.
"""

prompt = PromptTemplate.from_template(RAG_TEMPLATE)


def format_docs(docs):
    """Turn the retrieved documents into one block of text. Same as file 07."""
    lines = []
    for doc in docs:
        lines.append(doc.page_content)
    return "\n\n".join(lines)


model = get_model(temperature=0.0, max_tokens=300)
parser = StrOutputParser()

print("[..] Assembling the chain...")

# Read this from the inside out.
#   RunnablePassthrough() hands the question straight through, untouched.
#   retriever | format_docs sends the question to the database, then formats
#   the documents it returns.
# Both land in the prompt at the same time, as {question} and {context}.
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)

print("[OK] Chain ready.")

question = "At TechCorp, how many days of remote work are unconditionally allowed each week?"
print("")
print("Question:", question)
print("[..] One call runs retrieve, fill, ask and clean...")

answer = rag_chain.invoke(question)

print("")
print("--- The answer ---")
print(answer.strip())

print("")
print("Compare this file with 07. Same steps, same result, far less code.")
print("The chain is worth having because you will reuse it for every question")
print("and every document set from here on.")
print("")
print("TRY NEXT: ask 'What is the dress code?' and then 'Where do I park?'")
print("The second one has no matching policy, so it should refuse.")

print("")
print("====================================================================")
print("Ask your own. One call runs retrieve, fill, ask and clean each time.")
print("Try a question the policy does not cover and watch it refuse.")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break
    print("Assistant:", rag_chain.invoke(typed).strip())

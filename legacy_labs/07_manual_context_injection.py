"""
07 - RAG, By Hand

This is where RAG stops sounding clever and starts looking obvious.

There is no special technology here. We search for the relevant chunks, paste
them into the prompt as plain text, and ask the model to answer using only
those. That is the whole idea:

    RETRIEVE the relevant text  ->  AUGMENT the prompt with it  ->  GENERATE

Retrieval-Augmented Generation. The name describes those three steps.

We deliberately ask the SAME question that failed in file 06.

RUN:
    uv run 07_manual_context_injection.py
"""

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from models import get_model, get_embeddings, which_provider

print("====================================================================")
print("STEP 7 - RAG, WRITTEN OUT BY HAND")
print("Running on:", which_provider())
print("====================================================================")

# 1. The handbook the model has never seen.
documents = [
    Document(page_content="TechCorp Dress Code: Business casual on Monday to Thursday."),
    Document(page_content="TechCorp Remote Policy: Remote work is permitted unconditionally for 2 days each week, on Tuesdays and Thursdays."),
    Document(page_content="TechCorp IT Policy: Do not install personal games on company laptops."),
]

print("")
print("[..] 1. Building the vector database...")
db = FAISS.from_documents(documents, get_embeddings())

question = "At TechCorp, how many days of remote work are unconditionally allowed each week?"
print("[OK] Ready. Same question that failed in file 06.")

# 2. RETRIEVE
print("[..] 2. Searching for the chunks that relate to the question...")
results = db.similarity_search(question, k=2)

context_string = ""
number = 1
for document in results:
    context_string = context_string + "Chunk " + str(number) + ": " + document.page_content + "\n"
    number = number + 1

# 3. AUGMENT - ordinary string building, nothing more.
#
# The ORDER matters more than people expect. Context first, then the question,
# then the instruction. Put the instruction first instead and the model fixes
# on the refusal rule and claims it cannot find an answer that is sitting right
# there in the context. That is not a bug in the model; it is prompt design,
# and it is why "context first" is the standard shape for RAG prompts.
print("[..] 3. Pasting those chunks into the prompt...")

prompt = (
    "You are an HR assistant.\n\n"
    "CONTEXT FROM THE POLICY:\n" + context_string + "\n"
    "QUESTION: " + question + "\n\n"
    "Answer the question using only the context above. If the context contains "
    "the answer, state it plainly. Only if it is genuinely absent, reply: "
    "I cannot find this in the policy.\n"
)

print("")
print("********************************************************************")
print("THE EXACT TEXT BEING SENT TO THE MODEL")
print("********************************************************************")
print(prompt)
print("********************************************************************")

# 4. GENERATE
print("")
print("[..] 4. Sending it...")
model = get_model(temperature=0.0, max_tokens=300)
response = model.invoke(prompt)

print("")
print("--- The answer ---")
print(response.content.strip())

print("")
print("Same model, same question, a correct answer this time. The only thing")
print("that changed is that the facts were in the prompt.")
print("")
print("Three things in that prompt are doing quiet, important work:")
print("  context BEFORE the question  the model reads the facts first")
print("  'using only the context'     stops it falling back on invention")
print("  'reply: I cannot find this'  a safe way to admit it does not know")
print("")
print("TRY NEXT: ask about the dress code, then ask about parking. It answers")
print("the first and refuses the second. Refusing is the CORRECT answer.")

print("")
print("====================================================================")
print("Ask your own. You will see the chunks it retrieved, then the answer.")
print("Try the dress code (covered) and then parking (not covered).")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break

    # The same three steps, every time: retrieve, augment, generate.
    found = db.similarity_search(typed, k=2)
    retrieved = ""
    count = 1
    for item in found:
        print("  retrieved " + str(count) + ":", item.page_content)
        retrieved = retrieved + "Chunk " + str(count) + ": " + item.page_content + "\n"
        count = count + 1

    turn_prompt = (
        "You are an HR assistant.\n\n"
        "CONTEXT FROM THE POLICY:\n" + retrieved + "\n"
        "QUESTION: " + typed + "\n\n"
        "Answer the question using only the context above. If the context contains "
        "the answer, state it plainly. Only if it is genuinely absent, reply: "
        "I cannot find this in the policy.\n"
    )
    print("Answer:", model.invoke(turn_prompt).content.strip())

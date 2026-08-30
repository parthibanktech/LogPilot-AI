"""
12 - Capstone: The HR Chatbot With a Web Screen

The same assistant as file 11, now behind a browser screen anyone can use.

The RAG part is unchanged. That is the point worth noticing: the retrieval
chain you built does not care whether it is called from a terminal, a web
page, or a scheduled job.

RUN:
    uv run 12_hr_policy_gradio_chatbot.py

Then open the http://127.0.0.1:7871 link it prints.
"""

import os
import socket
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import gradio as gr

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from models import get_model, get_embeddings, which_provider

PDF_PATH = "HR_Policy.pdf"

if os.path.exists(PDF_PATH) is False:
    print("[!!] Could not find " + PDF_PATH)
    print("     Run this file from the mission5 folder.")
    sys.exit(1)

print("[..] Reading the PDF and building the knowledge base...")
print("     This happens once, at startup. Give it a moment.")

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(documents)

db = FAISS.from_documents(chunks, get_embeddings())
retriever = db.as_retriever(search_kwargs={"k": 4})

print("[OK] " + str(len(documents)) + " pages, " + str(len(chunks)) + " chunks indexed.")

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


chatbot_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | get_model(temperature=0.0, max_tokens=400)
    | StrOutputParser()
)


def answer(message, history):
    """Called by the screen each time someone asks something."""
    if message.strip() == "":
        return "Please type a question."
    return chatbot_chain.invoke(message)


with gr.Blocks(title="HR Policy Chatbot") as demo:
    gr.Markdown(
        "# HR Policy Chatbot\n"
        "Ask about the policy document. Every answer comes from the PDF, "
        "with the page it came from.\n\n"
        "Running on: **" + which_provider() + "** with OpenAI embeddings"
    )
    gr.ChatInterface(
        fn=answer,
        examples=[
            "What is this policy about?",
            "How do I report a concern?",
            "Who investigates a complaint?",
            "How many days of casual leave do I get?",
        ],
    )


def find_free_port(preferred):
    """Use our own port, or the next free one if something else has it."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    busy = probe.connect_ex(("127.0.0.1", preferred))
    probe.close()
    if busy != 0:
        return preferred
    return 0        # 0 lets the operating system pick any free port


port = find_free_port(7871)
print("Opening http://127.0.0.1:" + str(port))
print("Press Ctrl+C in this terminal to stop.")
demo.launch(server_name="127.0.0.1", server_port=port, inbrowser=True)

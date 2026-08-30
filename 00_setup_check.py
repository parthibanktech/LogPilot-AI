"""
00 - Setup Check

Run this FIRST. It proves your machine is ready before you start the labs:
Python, the packages, both API keys, one real chat call and one real embedding
call. If something is wrong it tells you exactly what to fix.

RUN:
    uv run 00_setup_check.py
"""

import os
import sys

print("====================================================================")
print("MISSION 5 - SETUP CHECK")
print("====================================================================")

problems = []

# 1. Python version
if sys.version_info < (3, 11):
    problems.append("Python 3.11 or newer is needed. You have " + sys.version.split()[0] + ".")
    print("[!!] Python", sys.version.split()[0], "is too old.")
else:
    print("[OK] Python version is fine.")

# 2. Packages
try:
    from dotenv import load_dotenv
    import langchain
    import numpy
    import gradio
    import faiss
    from langchain_community.vectorstores import FAISS
    from langchain_community.document_loaders import PyPDFLoader
    print("[OK] Packages are installed (uv sync worked).")
except Exception as error:
    problems.append("Packages are missing. Run: uv sync   (details: " + str(error) + ")")
    print("[!!] Packages are missing.")
    print("====================================================================")
    print("Run  uv sync  in this folder, then run this file again.")
    raise SystemExit()

load_dotenv()

# 3. The .env file must be in THIS folder
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    print("[OK] Found the .env file in this folder.")
else:
    problems.append("No .env file in this folder. Create one next to these lab files.")
    print("[!!] No .env file in this folder.")

# 4. The PDF the last two labs need
if os.path.exists("HR_Policy.pdf"):
    print("[OK] Found HR_Policy.pdf.")
else:
    problems.append("HR_Policy.pdf is missing. Labs 11 and 12 need it.")
    print("[!!] HR_Policy.pdf is missing.")

# 5. Keys
deepseek = os.getenv("DEEPSEEK_API_KEY", "").strip()
openai = os.getenv("OPENAI_API_KEY", "").strip()

if deepseek != "" and deepseek != "your_deepseek_api_key_here":
    print("[OK] DEEPSEEK_API_KEY found (chat).")
else:
    print("[--] No DEEPSEEK_API_KEY. We will use OpenAI for chat instead.")

if openai != "":
    print("[OK] OPENAI_API_KEY found (embeddings, and chat backup).")
else:
    problems.append("OPENAI_API_KEY is missing. Every search in this mission needs it.")
    print("[!!] No OPENAI_API_KEY. Retrieval needs it from lab 03 onwards.")

if deepseek == "" and openai == "":
    problems.append("No chat key at all. Add DEEPSEEK_API_KEY (or OPENAI_API_KEY) to .env.")

# 6. One real chat call
if len(problems) == 0:
    import models
    print("[..] Sending one small message to", models.which_provider(), "...")
    try:
        reply = models.get_model(max_tokens=5).invoke("Reply with exactly: ready")
        print("[OK]", models.which_provider(), "replied:", reply.content.strip())
    except Exception as error:
        message = str(error)
        problems.append("The chat call failed: " + message)
        print("[!!] The chat call failed.")
        if "missing_scope" in message:
            print("     Your API key is restricted. Create a new one with All permissions.")
        if "insufficient_quota" in message or "credit" in message:
            print("     That account has no credit left. Top it up or use another key.")

# 7. One real embedding call000000000000000000000000
if len(problems) == 0:
    print("[..] Making one embedding (every search in this mission uses these)...")
    try:
        vector = models.get_embeddings().embed_query("hello")
        print("[OK] Embeddings work. Each piece of text becomes", len(vector), "numbers.")
    except Exception as error:
        message = str(error)
        problems.append("The embedding call failed: " + message)
        print("[!!] The embedding call failed.")
        if "missing_scope" in message:
            print("     Your OpenAI key is restricted. Create a new one with All permissions.")

print("====================================================================")
if len(problems) == 0:
    print("ALL GOOD - you are ready.")
    print("Open 01_read_a_document.py next.")
else:
    print("PLEASE FIX THESE:")
    number = 1
    for problem in problems:
        print("  " + str(number) + ". " + problem)
        number = number + 1
print("====================================================================")

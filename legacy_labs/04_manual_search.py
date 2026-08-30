"""
04 - Searching By Meaning, By Hand

Now put embeddings to work. We take a few chunks of a handbook, turn each one
into numbers, turn the QUESTION into numbers too, and pick the chunk whose
numbers sit closest.

That is a search engine in about twenty lines. Building it by hand once means
the vector database in the next file will hold no mystery.

RUN:
    uv run 04_manual_search.py
"""

import numpy as np

from models import get_embeddings

print("====================================================================")
print("STEP 4 - FINDING THE RIGHT CHUNK, BY HAND")
print("====================================================================")


def similarity(first, second):
    """How close two vectors point in the same direction. 1.0 is identical."""
    return np.dot(first, second) / (np.linalg.norm(first) * np.linalg.norm(second))


embeddings = get_embeddings()

chunks = [
    "All full-time employees are entitled to 20 days of paid vacation per year.",
    "The office is closed on all public holidays listed by the government.",
    "Employees may work remotely for up to 10 days each month with approval.",
    "Reimbursement claims must be submitted within 30 days of the expense.",
]

print("")
print("We have " + str(len(chunks)) + " chunks of the handbook.")
print("[..] Turning each chunk into numbers (this happens once, up front)...")

chunk_vectors = []
for chunk in chunks:
    chunk_vectors.append(embeddings.embed_query(chunk))

print("[OK] Stored " + str(len(chunk_vectors)) + " vectors.")


def search(question):
    """Score every chunk against the question and show the winner."""
    print("")
    print("====================================================================")
    print("Question:", question)
    question_vector = embeddings.embed_query(question)

    best_score = -1.0
    best_chunk = ""
    position = 0
    for vector in chunk_vectors:
        score = similarity(question_vector, vector)
        print("  ", round(score, 4), "|", chunks[position])
        if score > best_score:
            best_score = score
            best_chunk = chunks[position]
        position = position + 1

    print("   WINNER ->", best_chunk)


# Neither question shares a single important word with the chunk it finds.
search("Can I do my job from home?")
search("How do I get money back for something I bought for work?")

print("")
print("====================================================================")
print("Now ask your own. Every chunk gets scored, so you see the whole race.")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break
    search(typed)

print("")
print("A vague question retrieves a vague match. Try 'How much time off do I")
print("get?' and watch it pick the wrong one, because two chunks mention days.")

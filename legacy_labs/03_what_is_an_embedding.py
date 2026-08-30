"""
03 - What an Embedding Is

An embedding turns a sentence into a long list of numbers that stands for its
MEANING. Sentences that mean similar things end up with similar numbers, even
when they share no words at all.

That is the trick behind every "search by meaning" feature you have used. This
file proves it with three sentences and one piece of school maths.

RUN:
    uv run 03_what_is_an_embedding.py
"""

import numpy as np

from models import get_embeddings

print("====================================================================")
print("STEP 3 - TURNING SENTENCES INTO NUMBERS")
print("====================================================================")


def similarity(first, second):
    """How close two vectors point in the same direction. 1.0 is identical."""
    return np.dot(first, second) / (np.linalg.norm(first) * np.linalg.norm(second))


embeddings = get_embeddings()

sentence1 = "The furry pet is barking loudly at the mailman."
sentence2 = "A dog makes a lot of noise when the postman arrives."
sentence3 = "Stock prices fell sharply today on Wall Street."

print("")
print("1:", sentence1)
print("2:", sentence2)
print("3:", sentence3)
print("")
print("Read 1 and 2 again. They mean the same thing and share almost no words.")
print("")
print("[..] Turning each sentence into numbers...")

vector1 = embeddings.embed_query(sentence1)
vector2 = embeddings.embed_query(sentence2)
vector3 = embeddings.embed_query(sentence3)

print("[OK] Each sentence is now " + str(len(vector1)) + " numbers.")
print("First three numbers of sentence 1:", round(vector1[0], 4), round(vector1[1], 4), round(vector1[2], 4))

print("")
print("--- Comparing meanings ---")
print("1 vs 2:", round(similarity(vector1, vector2), 4), " both about a dog and a postman")
print("1 vs 3:", round(similarity(vector1, vector3), 4), " nothing in common")

print("")
print("The high score for 1 vs 2 came from MEANING, not shared words.")
print("Search that works this way is what makes RAG possible.")

print("")
print("====================================================================")
print("Now try your own pairs. Type two sentences and see how close they are.")
print("Try a pair that means the same thing using different words.")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    first = input("\nSentence A: ").strip()
    if first == "":
        continue
    if first.lower() == "exit" or first.lower() == "quit":
        print("Bye.")
        break
    second = input("Sentence B: ").strip()
    if second == "":
        continue
    if second.lower() == "exit" or second.lower() == "quit":
        print("Bye.")
        break
    score = similarity(embeddings.embed_query(first), embeddings.embed_query(second))
    print("Similarity:", round(score, 4))
    if score > 0.5:
        print("   Close in meaning.")
    elif score > 0.3:
        print("   Loosely related.")
    else:
        print("   Different subjects.")

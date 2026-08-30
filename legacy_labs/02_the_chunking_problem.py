"""
02 - The Chunking Problem

You cannot hand a 500-page manual to a model in one go. There is a limit on
how much it can read at once, and even within that limit, burying the useful
paragraph in hundreds of pages makes the answer worse.

So we split the document into small pieces called chunks. Later we will search
those chunks and send only the ones that matter.

Two settings decide the split:
    chunk_size    - how big each piece may be
    chunk_overlap - how much of the previous piece to repeat at the start of
                    the next one, so a sentence cut in half is not lost

RUN:
    uv run 02_the_chunking_problem.py
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

print("====================================================================")
print("STEP 2 - SPLITTING A DOCUMENT INTO CHUNKS")
print("====================================================================")

long_text = """
The United States of America (USA), commonly known as the United States (U.S.)
or America, is a country primarily located in North America. It is a federal
republic consisting of 50 states, a federal district, five major unincorporated
territories, nine Minor Outlying Islands, and 326 Indian reservations. It is the
world's third-largest country by both land and total area. It shares land borders
with Canada to its north and with Mexico to its south. It has maritime borders
with the Bahamas, Cuba, Russia, and other nations. With a population of over
336 million, it is the most populous country in the Americas and the third-most
populous in the world. The national capital is Washington, D.C., and its most
populous city and principal financial center is New York City.
"""

doc = Document(page_content=long_text, metadata={"source": "wikipedia.txt"})

print("")
print("One document, " + str(len(long_text)) + " characters.")
print("Small enough to send whole. A 500-page manual would not be.")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,      # at most this many characters per chunk
    chunk_overlap=80,    # repeat this much from the previous chunk
)

chunks = splitter.split_documents([doc])

print("")
print("[OK] Split into " + str(len(chunks)) + " chunks.")

number = 1
for chunk in chunks:
    print("")
    print("--- Chunk " + str(number) + " (" + str(len(chunk.page_content)) + " characters) ---")
    print(chunk.page_content.strip())
    number = number + 1

print("")
print("Look at where one chunk ends and the next begins. The overlap means a")
print("sentence split across the boundary still appears whole in one of them.")
print("")
print("TRY NEXT: set chunk_overlap to 0 and run again. Watch sentences break.")

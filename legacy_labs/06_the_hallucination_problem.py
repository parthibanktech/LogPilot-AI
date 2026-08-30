"""
06 - Why RAG Exists

Everything so far was machinery. This file shows the problem it solves.

We ask about a handbook the model has never seen. It cannot know the answer.
So it does one of two things, and both are a problem at work:

    it refuses, which is useless to the employee who asked, or
    it invents a policy that sounds completely reasonable

The second one is what people mean by hallucination, and it is dangerous
precisely because the wording is confident and professional.

RUN:
    uv run 06_the_hallucination_problem.py
"""

from models import get_model, which_provider

print("====================================================================")
print("STEP 6 - THE PROBLEM RAG SOLVES")
print("Running on:", which_provider())
print("====================================================================")

# temperature 0.7 so you see it reach, the way it would on a real question.
model = get_model(temperature=0.7, max_tokens=300)

question = "At TechCorp, how many days of remote work are unconditionally allowed each week?"

print("")
print("Question:", question)
print("")
print("TechCorp is invented. This handbook does not exist anywhere.")
print("[..] Asking the model, with no documents at all...")

response = model.invoke(question)

print("")
print("--- The answer ---")
print(response.content.strip())

print("")
print("Whatever it said, it could not have known. It never read the handbook.")
print("")
print("Notice there is no way to tell a right answer from an invented one by")
print("reading it. That is the whole difficulty. The next file fixes this by")
print("giving the model the handbook before it answers.")

print("")
print("====================================================================")
print("Ask it anything about TechCorp. It has never heard of the company.")
print("Try: What is the notice period? How many sick days? Who is the CEO?")
print("Type 'exit' to quit.")
print("====================================================================")

while True:
    typed = input("\nYou: ").strip()
    if typed == "":
        continue
    if typed.lower() == "exit" or typed.lower() == "quit":
        print("Bye.")
        break
    print("Model:", model.invoke(typed).content.strip())

print("")
print("Some answers were refusals. Some were inventions. You cannot tell")
print("which is which by reading them, and that is the whole problem.")

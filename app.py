from google import genai
from config import GEMINI_API_KEY
from rag import retrieve_context

client = genai.Client(api_key=GEMINI_API_KEY)

print("\n===== UNIVERSITY STUDY ASSISTANT =====")
print("1. Ask Questions")
print("2. Generate MCQs")
print("3. Generate Flashcards")
print("4. Generate Summary")
print("5. Important Exam Questions")

choice = input("\nChoose option: ")

topic = input("\nEnter topic/question: ")

results = retrieve_context(topic)

context = "\n".join(results)

if choice == "1":

    prompt = f"""
    Answer the question using only the provided context.

    Context:
    {context}

    Question:
    {topic}
    """

elif choice == "2":

    prompt = f"""
    Using only the provided context, generate 10 multiple-choice questions.

    Requirements:
    - 4 options each
    - Mention the correct answer
    - Questions should be exam style

    Context:
    {context}
    """

elif choice == "3":

    prompt = f"""
    Using only the provided context, generate 10 flashcards.

    Format:

    Q: Question
    A: Answer

    Context:
    {context}
    """

elif choice == "4":

    prompt = f"""
    Create a concise study summary using only the provided context.

    Include:
    - Key concepts
    - Important facts
    - Exam-relevant points

    Context:
    {context}
    """

elif choice == "5":

    prompt = f"""
    Using only the provided context, generate 10 important exam questions.

    Include:
    - Short questions
    - Long questions
    - Conceptual questions

    Context:
    {context}
    """

else:

    print("Invalid choice.")
    exit()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print("\n")
print(response.text)

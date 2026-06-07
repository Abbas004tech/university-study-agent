import os
import time
import streamlit as st
from google import genai
from config import GEMINI_API_KEY

from rag import (
    retrieve_context,
    extract_text_from_pdf,
    extract_text_from_pptx,
    chunk_text,
    store_chunks
)

client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="University Study Assistant",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 University Study Assistant")

# =====================
# CHAT HISTORY
# =====================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================
# FILE UPLOAD
# =====================

uploaded_file = st.file_uploader(
    "Upload PDF or PPTX",
    type=["pdf", "pptx"]
)

if uploaded_file:

    os.makedirs("data", exist_ok=True)

    file_path = os.path.join(
        "data",
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:

        if uploaded_file.name.endswith(".pdf"):

            text = extract_text_from_pdf(
                file_path
            )

        elif uploaded_file.name.endswith(".pptx"):

            text = extract_text_from_pptx(
                file_path
            )

        else:
            text = ""

        chunks = chunk_text(text)

        store_chunks(chunks)

        st.success(
            f"{uploaded_file.name} uploaded and indexed successfully!"
        )

    except Exception as e:

        st.error(
            f"Indexing Error: {e}"
        )

st.divider()

# =====================
# OPTIONS
# =====================

option = st.selectbox(
    "Choose Action",
    [
        "Ask Questions",
        "Generate MCQs",
        "Generate Flashcards",
        "Generate Summary",
        "Important Exam Questions"
    ]
)

topic = st.text_input(
    "Enter topic or question"
)

# =====================
# GENERATE
# =====================

if st.button("Generate"):

    if not topic:

        st.warning(
            "Please enter a topic or question."
        )

    else:

        results = retrieve_context(topic)

        context = "\n".join(results)

        if option == "Ask Questions":

            prompt = f"""
Answer the question using only the provided context.

Context:
{context}

Question:
{topic}
"""

        elif option == "Generate MCQs":

            prompt = f"""
Generate 10 MCQs using only the provided context.

Requirements:
- 4 options each
- Mention the correct answer
- Exam-style questions

Context:
{context}
"""

        elif option == "Generate Flashcards":

            prompt = f"""
Generate 10 flashcards using only the provided context.

Format:

Q: Question
A: Answer

Context:
{context}
"""

        elif option == "Generate Summary":

            prompt = f"""
Create a study summary using only the provided context.

Include:
- Key concepts
- Important facts
- Exam points

Context:
{context}
"""

        else:

            prompt = f"""
Generate 10 important exam questions using only the provided context.

Include:
- Short questions
- Long questions
- Conceptual questions

Context:
{context}
"""

        response = None

        with st.spinner("Generating response..."):

            for attempt in range(3):

                try:

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    break

                except Exception:

                    time.sleep(5)

        if response:

            st.session_state.messages.append(
                {
                    "question": topic,
                    "answer": response.text
                }
            )

            st.success("Done!")

            st.write(response.text)

        else:

            st.error(
                "Gemini servers are busy right now. Please try again in a minute."
            )

# =====================
# CHAT HISTORY
# =====================

if st.session_state.messages:

    st.divider()

    st.subheader("Chat History")

    for item in reversed(
        st.session_state.messages
    ):

        st.markdown(
            f"### ❓ {item['question']}"
        )

        st.write(
            item['answer']
        )

        st.markdown("---")

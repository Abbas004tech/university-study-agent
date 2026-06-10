import os
import time
import streamlit as st
from google import genai

from rag import (
    extract_text_from_pdf,
    extract_text_from_pptx,
    chunk_text
)

from config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)

st.set_page_config(
    page_title="University Study Assistant",
    page_icon="🎓"
)

st.title("🎓 University Study Assistant")

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

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

    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)

    else:
        text = extract_text_from_pptx(file_path)

    st.session_state.document_text = text

    st.success("File uploaded successfully!")

st.divider()

option = st.selectbox(
    "Choose Action",
    [
        "Ask Questions",
        "Generate MCQs",
        "Generate Flashcards",
        "Generate Summary",
        "Generate Notes",
        "Important Exam Questions"
    ]
)

topic = st.text_input(
    "Enter topic or question"
)

if st.button("Generate"):

    if not st.session_state.document_text:

        st.warning(
            "Please upload a file first."
        )

    else:

        context = st.session_state.document_text[:20000]

        if option == "Ask Questions":

            prompt = f"""
Use the following study material.

{context}

Question:
{topic}
"""

        elif option == "Generate MCQs":

            prompt = f"""
Generate 10 MCQs from:

{context}
"""

        elif option == "Generate Flashcards":

            prompt = f"""
Generate 10 flashcards from:

{context}
"""

        elif option == "Generate Summary":

            prompt = f"""
Generate a study summary from:

{context}
"""
        elif option == "Generate Notes":

            prompt = f"""
Create detailed study notes from the provided study material.

Requirements:
- Use proper headings and subheadings
- Explain concepts in simple language
- Include definitions
- Include important facts
- Include exam-focused points
- Use bullet points where needed
- Organize notes for easy revision
- Make notes detailed and comprehensive

Study Material:

{context}
"""
        else:

            prompt = f"""
Generate important exam questions from:

{context}
"""

        try:

            with st.spinner("Generating..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.write(response.text)

        except Exception as e:

            st.error(str(e))

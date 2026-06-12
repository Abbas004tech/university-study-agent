import os
import time
import streamlit as st
from google import genai

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from datetime import date

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
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.stButton > button {
    width: 100%;
    border-radius: 15px;
    height: 55px;
    font-size: 18px;
    font-weight: bold;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 15px;
}

div[data-testid="metric-container"] {
    background-color: #262730;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #444;
}

div[data-testid="stFileUploader"] {
    border-radius: 15px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
padding:25px;
border-radius:15px;
background:linear-gradient(90deg,#1e3c72,#2a5298);
color:white;
text-align:center;
">

<h1>🎓 University Study Assistant</h1>

<h3>AI Powered Study Companion</h3>

<p>
Generate Notes • MCQs • Flashcards • Summaries • Exam Questions
</p>

</div>
""", unsafe_allow_html=True)
if "history" not in st.session_state:
    st.session_state.history = []

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

st.subheader("📂 Upload Study Material")

uploaded_files = st.file_uploader(
    "Upload PDF or PPTX Files",
    type=["pdf", "pptx"],
    accept_multiple_files=True
)

if uploaded_files:

    all_text = ""

    os.makedirs("data", exist_ok=True)

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            "data",
            uploaded_file.name
        )

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.endswith(".pdf"):

            text = extract_text_from_pdf(
                file_path
            )

        else:

            text = extract_text_from_pptx(
                file_path
            )

        all_text += "\n\n" + text

    st.session_state.document_text = all_text

    st.success(
        f"{len(uploaded_files)} file(s) uploaded successfully!"
    )

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📂 Files Uploaded",
        len(uploaded_files) if uploaded_files else 0
    )

with col2:
    st.metric(
        "📜 History Items",
        len(st.session_state.history)
    )

with col3:
    st.metric(
        "🤖 Features",
        6
    )
if uploaded_files:

    st.markdown("### 📁 Uploaded Files")

    for file in uploaded_files:

        st.success(f"✅ {file.name}")

st.divider()

with st.sidebar:

    st.title("🎓 Study Assistant")

    st.markdown("---")

    option = st.selectbox(
        "Choose Action",
        [
            "Ask Questions",
            "Generate MCQs",
            "Generate Flashcards",
            "Generate Summary",
            "Generate Notes",
            "Important Exam Questions",
            "Quiz Mode",
            "Study Planner"
        ]
    )

st.markdown("---")

st.success("📚 Upload Study Material")
st.success("📝 Generate Notes")
st.success("🎯 Generate MCQs")
st.success("📄 Download PDF")
st.success("📅 Study Planner")

topic = st.text_input(
    "Enter topic or question"
)

exam_date = None
study_hours = None

if option == "Study Planner":

    exam_date = st.date_input(
        "Select Exam Date"
    )

    study_hours = st.number_input(
        "Study Hours Per Day",
        min_value=1,
        max_value=12,
        value=3
    )
if st.button(
    "🚀 Generate",
    use_container_width=True
):

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
        elif option == "Important Exam Questions":

            prompt = f"""
Generate important exam questions from:

{context}
"""

        elif option == "Quiz Mode":

            prompt = f"""
Create a quiz from the study material.

Requirements:
- Generate 10 MCQs
- Give 4 options for each question
- Clearly mention the correct answer
- Cover important concepts
- Make it exam-focused

Study Material:

{context}
"""
        elif option == "Study Planner":

            if exam_date < date.today():

                st.error(
                    "Please select a future exam date."
                )

                st.stop()

            prompt = f"""
Create a complete study plan.

Current Date: {date.today()}

Exam Date: {exam_date}

Requirements:

- Start the study plan from the Current Date
- End the study plan on the Exam Date
- Do not mention weekdays
- Use only calendar dates
- Never generate dates before the Current Date
- Student can study {study_hours} hours per day
- Create a day-by-day study schedule
- Divide topics evenly
- Include revision sessions
- Include final preparation days
- Present the schedule in a clean table

Study Material:

{context}
"""

        try:

            with st.spinner("Generating..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.write(response.text)

            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer)

            styles = getSampleStyleSheet()

            content = [
                Paragraph(
                    response.text.replace("\n", "<br/>"),
                    styles["BodyText"]
                )
            ]

            doc.build(content)

            pdf_buffer.seek(0)

            st.download_button(
                label="📄 Download as PDF",
                data=pdf_buffer,
                file_name=f"{option}.pdf",
                mime="application/pdf"
            )
            docx_buffer = BytesIO()

            document = Document()

            document.add_heading(
            option,
            level=1
            )

            document.add_paragraph(
            response.text
            )

            document.save(docx_buffer)

            docx_buffer.seek(0)

            st.download_button(
                label="📝 Download DOCX",
                data=docx_buffer,
                file_name=f"{option}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            st.session_state.history.append(
                {
                    "type": option,
                    "question": topic,
                    "answer": response.text
                }
            )

        except Exception as e:

            st.error(str(e))

st.divider()

st.subheader("📚 Study History")

if st.session_state.history:

    for item in reversed(
        st.session_state.history
    ):

        st.markdown(
            f"### {item['type']}"
        )

        st.markdown(
            f"**Prompt:** {item['question']}"
        )

        st.write(
            item['answer']
        )

        st.markdown("---")

st.markdown("---")

st.caption(
    "🚀 Built with Streamlit + Gemini AI"
)

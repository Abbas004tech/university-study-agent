from pptx import Presentation
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="study_material"
)


def extract_text_from_pptx(file_path):
    prs = Presentation(file_path)

    text = ""

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"

    return text


def extract_text_from_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def chunk_text(text, chunk_size=500):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def store_chunks(chunks):

    existing = collection.count()

    for i, chunk in enumerate(chunks):

        embedding = embedding_model.encode(
            chunk
        ).tolist()

        collection.add(
            ids=[str(existing + i)],
            embeddings=[embedding],
            documents=[chunk]
        )


def retrieve_context(question):

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return results["documents"][0]

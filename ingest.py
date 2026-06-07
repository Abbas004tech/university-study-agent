import os

from rag import (
    extract_text_from_pptx,
    extract_text_from_pdf,
    chunk_text,
    store_chunks
)

DATA_FOLDER = "data"

all_chunks = []

for file_name in os.listdir(DATA_FOLDER):

    file_path = os.path.join(
        DATA_FOLDER,
        file_name
    )

    if file_name.endswith(".pptx"):

        print(f"Reading PPTX: {file_name}")

        text = extract_text_from_pptx(
            file_path
        )

        chunks = chunk_text(text)

        all_chunks.extend(chunks)

    elif file_name.endswith(".pdf"):

        print(f"Reading PDF: {file_name}")

        text = extract_text_from_pdf(
            file_path
        )

        chunks = chunk_text(text)

        all_chunks.extend(chunks)

print(f"\nTotal Chunks: {len(all_chunks)}")

store_chunks(all_chunks)

print("\nAll files stored successfully!")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from ingest import extract_text, PDF_PATH


def create_recursive_chunks(pages):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, #characters
        chunk_overlap=200, #characters
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(page["text"])

        for chunk in page_chunks:
            chunks.append({
                "page": page["page"],
                "text": chunk
            })

    return chunks



if __name__ == "__main__":

    pages = extract_text(PDF_PATH)

    chunks = create_recursive_chunks(pages)

    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i + 1}")
        print("Page:", chunk["page"])
        print(chunk["text"])

        chunk_lengths = [
        len(chunk["text"])
        for chunk in chunks
    ]

    print("\nChunk statistics:")
    print("Smallest chunk:", min(chunk_lengths), "characters")
    print("Largest chunk:", max(chunk_lengths), "characters")
    print(
        "Average chunk size:",
        round(sum(chunk_lengths) / len(chunk_lengths), 2),
        "characters"
    )

# The splitter tries to retain approximately 200 characters from the previous chunk.

# Also notice that Chunk 1 contains a complete introductory section, while Chunk 2 contains the next section. This is one advantage of recursive splitting: it tries to respect paragraph and sentence boundaries.
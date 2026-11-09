
from ingest import extract_text, PDF_PATH

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def create_chunks(pages):

    chunks = []

    for page in pages:

        words = page["text"].split()

        start = 0

        while start < len(words):

            end = start + CHUNK_SIZE

            chunk_text = " ".join(words[start:end])

            chunks.append({
                "text": chunk_text,
                "page": page["page"]
            })

            start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


if __name__ == "__main__":

    pages = extract_text(PDF_PATH)

    chunks = create_chunks(pages)

    print(f"\nTotal chunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks[:3]):

        print(f"\n--- Chunk {i + 1} ---")
        print(f"Page: {chunk['page']}")
        print(chunk["text"][:500])

import re
import numpy as np

from ingest import extract_text, PDF_PATH
from embeddings import generate_embeddings


def cosine_similarity(vec1, vec2):

    dot_product = np.dot(vec1, vec2)

    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def create_semantic_chunks(
    pages,
    threshold=0.65,
    min_chunk_size=300,
    max_chunk_size=1000
):

    # Step 1: Extract sentences from all pages
    page_sentences = []
    all_sentence_records = []

    for page in pages:

        sentences = re.split(
            r'(?<=[.!?])\s+',
            page["text"]
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        page_sentences.append({
            "page": page["page"],
            "sentences": sentences
        })

        for sentence in sentences:
            all_sentence_records.append({
                "text": sentence,
                "page": page["page"]
            })

    if not all_sentence_records:
        return []

    # Step 2: Generate embeddings in larger batches
    print("\nGenerating sentence embeddings...")

    all_embeddings = generate_embeddings(
        all_sentence_records,
        batch_size=90
    )

    # Step 3: Group sentences based on semantic similarity
    chunks = []
    embedding_index = 0

    for page_data in page_sentences:

        sentences = page_data["sentences"]

        if not sentences:
            continue

        page_embeddings = all_embeddings[
            embedding_index:
            embedding_index + len(sentences)
        ]

        embedding_index += len(sentences)

        current_sentences = [sentences[0]]
        current_embeddings = [page_embeddings[0]]

        for i in range(1, len(sentences)):

            current_text = " ".join(current_sentences)

            candidate_text = (
                current_text + " " + sentences[i]
            )

            current_embedding = np.mean(
                current_embeddings,
                axis=0
            )

            similarity = cosine_similarity(
                current_embedding,
                page_embeddings[i]
            )

            should_split = (
                similarity < threshold
                and len(current_text) >= min_chunk_size
            )

            exceeds_max_size = (
                len(candidate_text) > max_chunk_size
            )

            if should_split or exceeds_max_size:

                chunks.append({
                    "page": page_data["page"],
                    "text": current_text
                })

                current_sentences = [sentences[i]]
                current_embeddings = [page_embeddings[i]]

            else:

                current_sentences.append(sentences[i])
                current_embeddings.append(page_embeddings[i])

        if current_sentences:

            chunks.append({
                "page": page_data["page"],
                "text": " ".join(current_sentences)
            })

    return chunks


if __name__ == "__main__":

    pages = extract_text(PDF_PATH)

    chunks = create_semantic_chunks(pages)

    if chunks:

        lengths = [
            len(chunk["text"])
            for chunk in chunks
        ]

        print("\nTotal semantic chunks:", len(chunks))
        print("Smallest chunk:", min(lengths), "characters")
        print("Largest chunk:", max(lengths), "characters")

        print(
            "Average chunk size:",
            round(sum(lengths) / len(lengths), 2),
            "characters"
        )

        for i, chunk in enumerate(chunks[:3]):

            print(f"\nChunk {i + 1}")
            print("Page:", chunk["page"])
            print(chunk["text"])

    else:
        print("No semantic chunks created.")

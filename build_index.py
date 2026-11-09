
import argparse

from ingest import extract_text, PDF_PATH
from embeddings import generate_embeddings
from vector_store import store_embeddings


def build_index(strategy):

    print(f"\nBuilding index using: {strategy}")

    # Step 1: Extract PDF text
    pages = extract_text(PDF_PATH)

    print(f"Extracted {len(pages)} pages")

    # Step 2: Select chunking strategy
    if strategy == "fixed":

        from chunking import create_chunks
        chunks = create_chunks(pages)

    elif strategy == "recursive":

        from recursive_chunking import create_recursive_chunks
        chunks = create_recursive_chunks(pages)

    elif strategy == "semantic":

        from semantic_chunking import create_semantic_chunks
        chunks = create_semantic_chunks(pages)

    else:
        raise ValueError("Unsupported strategy")

    print(f"Created {len(chunks)} chunks")

    # Step 3: Generate embeddings
    embeddings = generate_embeddings(chunks)

    print("Embeddings generated")

    # Step 4: Store embeddings in ChromaDB
    store_embeddings(
        chunks,
        embeddings,
        strategy
    )

    print("\nIndex building completed!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--strategy",
        choices=["fixed", "recursive", "semantic"],
        default="fixed"
    )

    args = parser.parse_args()

    build_index(args.strategy)

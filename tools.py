
from embeddings import generate_query_embedding
from vector_store import get_collection
from config import ACTIVE_STRATEGY

from websearchtool import web_search


def search_document(query: str):

    print("\n[TOOL CALLED] Searching document...")
    print("Active strategy:", ACTIVE_STRATEGY)

    # Generate question embedding using Gemini
    query_embedding = generate_query_embedding(query)

    # Get selected ChromaDB collection
    collection = get_collection(ACTIVE_STRATEGY)

    # Search for the 3 most relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    retrieved_chunks = []

    if not results["documents"] or not results["documents"][0]:
        return retrieved_chunks

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        retrieved_chunks.append({
            "text": document,
            "page": metadata["page"],
            "distance": distance
        })

    return retrieved_chunks

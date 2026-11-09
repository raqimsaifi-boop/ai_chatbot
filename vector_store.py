
import chromadb

client = chromadb.PersistentClient(path="./database")

COLLECTION_NAMES = {
    "fixed": "last_signal_fixed",
    "recursive": "last_signal_recursive",
    "semantic": "last_signal_semantic",
    "hierarchical": "last_signal_hierarchical"
}


def get_collection(strategy="fixed"):

    if strategy not in COLLECTION_NAMES:
        raise ValueError(
            f"Unknown chunking strategy: {strategy}"
        )

    collection_name = COLLECTION_NAMES[strategy]

    collection = client.get_or_create_collection(
        name=collection_name
    )

    return collection


def store_embeddings(chunks, embeddings, strategy="fixed"):

    collection = get_collection(strategy)

    # Remove old records before rebuilding this collection
    existing_ids = collection.get()["ids"]

    if existing_ids:
        collection.delete(ids=existing_ids)

    ids = [
        f"chunk_{i}"
        for i in range(len(chunks))
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {"page": chunk["page"]}
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(
        f"Stored {len(chunks)} chunks "
        f"in {collection.name}"
    )

    return collection

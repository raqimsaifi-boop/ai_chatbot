
from vector_store import collection
from embeddings import model

query = "What is The Last Signal series about?"

# Convert question into embedding
query_embedding = model.encode(query).tolist()

# Search vector database
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

# Display results
for i, document in enumerate(results["documents"][0]):

    print(f"\nResult {i + 1}")

    print("Page:", results["metadatas"][0][i]["page"])

    print("Text:", document[:500])

    print("Distance:", results["distances"][0][i])

from vector_store import get_collection

collection = get_collection("fixed")

print("Collection:", collection.name)
print("Total vectors:", collection.count())

sample = collection.peek(limit=1)

print("\nSample document:")
print(sample["documents"][0])

print("\nVector dimensions:")
print(len(sample["embeddings"][0]))
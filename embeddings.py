
import os
import numpy as np

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


def generate_embeddings(chunks, batch_size=90):
    """
    Generate embeddings for document chunks.
    Uses RETRIEVAL_DOCUMENT because these are documents
    that we want to search later.
    """

    texts = [chunk["text"] for chunk in chunks]

    all_embeddings = []

    for i in range(0, len(texts), batch_size):

        batch = texts[i:i + batch_size]

        response = client.models.embed_content(
            model=MODEL_NAME,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )

        batch_embeddings = [
            item.values for item in response.embeddings
        ]

        all_embeddings.extend(batch_embeddings)

        print(
            f"Embedded {min(i + batch_size, len(texts))}"
            f"/{len(texts)} chunks"
        )

    return np.array(all_embeddings, dtype=np.float32)


def generate_query_embedding(query):
    """
    Generate an embedding for a user's question.
    Uses RETRIEVAL_QUERY for document retrieval.
    """

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    return response.embeddings[0].values

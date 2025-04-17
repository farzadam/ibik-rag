import json
import logging
from pathlib import Path

import numpy as np
from config import DATA_PATH, OPENAI_API_KEY
from fastapi import HTTPException
from numpy.linalg import norm
from openai import OpenAI

from app.models import Document

logger = logging.getLogger(__name__)


openai_client = OpenAI(api_key=OPENAI_API_KEY)
embedded_docs = []


# similarity metric
def cosine_sim(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))


def ingest_documents():
    logger.info(f"Ingesting and embedding documents from {DATA_PATH}")
    global embedded_docs
    path = Path(DATA_PATH)
    with open(path, "r") as f:
        raw_docs = json.load(f)

    # embed abstracts using openai
    texts = [doc["abstract"] for doc in raw_docs]
    try:
        response = openai_client.embeddings.create(
            input=texts, model="text-embedding-3-small"
        )
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate documents embeddings."
        )

    embedded_docs = []

    # enrich the local db with embeddings
    for i, doc in enumerate(raw_docs):
        embedded_docs.append(
            {
                "id": f"doc{i}",
                "embedding": response.data[i].embedding,
                "document": doc["abstract"],
                "metadata": {"title": doc["title"], "pubmed_id": doc["pubmed_id"]},
            }
        )

    return len(embedded_docs)


def query_documents(query: str, top_k: int):
    if not embedded_docs:
        raise RuntimeError("No documents ingested")

    # embed the query
    try:
        query_embedding = np.array(
            openai_client.embeddings.create(
                input=[query], model="text-embedding-3-small"
            )
            .data[0]
            .embedding
        )
    except Exception as e:
        logger.error(f"Unexpected error during query embedding: {e}")
        raise RuntimeError("Unexpected error during query embedding.")

    # calculate similarity scores between the query and the documents
    scores = [
        cosine_sim(query_embedding, np.array(doc["embedding"])) for doc in embedded_docs
    ]

    # select top_k most similar documents
    top_k_indices = np.argsort(scores)[::-1][:top_k]
    return [embedded_docs[i] for i in top_k_indices]


def format_context_docs(raw_docs):
    return [
        Document(
            title=doc.get("metadata", {}).get("title", "Untitled"),
            pubmed_id=doc.get("metadata", {}).get("pubmed_id", "unknown"),
            abstract=doc.get("document", ""),
        )
        for doc in raw_docs
    ]


def build_prompt(query: str, context_docs: list[Document]) -> str:
    context_str = "\n\n".join(
        f"Title: {d.title}\nAbstract: {d.abstract}" for d in context_docs
    )
    return (
        f"You are a helpful assistant with access to scientific PubMed abstracts.\n"
        f"Based on the following context, answer the question accurately.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {query}\nAnswer:"
    )


def generate_answer(prompt: str) -> str:

    # query openai model for response
    response = openai_client.responses.create(model="gpt-4o-mini", input=prompt)
    return response.output_text.strip()

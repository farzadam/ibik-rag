import logging

from fastapi import FastAPI, HTTPException

from app.models import QueryRequest, QueryResponse
from app.rag import (
    build_prompt,
    format_context_docs,
    generate_answer,
    ingest_documents,
    query_documents,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG API", description="Minimal RAG API", version="1.0")


@app.get("/")
def root():
    return {
        "message": "Welcome to the my RAG Pipeline. Use /ingest first and then you can use /query."
    }


@app.post("/ingest")
def ingest():
    try:
        count = ingest_documents()
        logger.info(f"Successfully embedded and stored {count} documents.")
        return {"status": "success", "documents_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        top_docs = query_documents(req.query, req.top_k)
        logger.info(f"{len(top_docs)} documents retrieved.")
        context_docs = format_context_docs(top_docs)
        prompt = build_prompt(req.query, context_docs)
        answer = generate_answer(prompt)
        logger.info(f"Generated answer for query: {req.query}")
        return QueryResponse(answer=answer, context=context_docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

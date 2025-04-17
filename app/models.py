from typing import List

from pydantic import BaseModel


class Document(BaseModel):
    title: str
    pubmed_id: str
    abstract: str


class QueryRequest(BaseModel):
    query: str
    top_k: int = 1


class QueryResponse(BaseModel):
    answer: str
    context: List[Document]

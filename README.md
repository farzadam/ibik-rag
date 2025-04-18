# Retrieval-Augmented Generation (RAG) API

This project implements a minimal, Retrieval-Augmented Generation (RAG) pipeline that allows question answering over scientific PubMed abstracts using OpenAI models.

It satisfies the requirements for a lightweight, end-to-end Dockerized system.

---

## Features

- Ingests scientific abstracts from a local `.json` file
- Dynamically generates document embeddings using OpenAI Embeddings API
- Stores documents and embeddings in memory (no persistent DB)
- Retrieves top-K most relevant documents using cosine similarity
- Generates answers using OpenAI's LLM (`gpt-4o-mini`)
- Clean FastAPI interface: `/ingest` and `/query`
- Small Docker image size (~340 MB) for fast builds and portability

---

## Project Structure

```
├── app/
│   ├── main.py         # FastAPI app (only routing logic)
│   ├── rag.py          # Embedding, retrieval, and generation logic
│   ├── models.py       # Pydantic data models
│   └── config.py       # Config loader from .env
├── data/
│   └── pubmed_docs.json  # Input document store
├── .env
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Running the App

### 1. Create `.env` file

```env
OPENAI_API_KEY=sk-...
DATA_PATH=data/pubmed_docs.json
```

### 2. Start the service

```bash
docker image prune -f           # optional: clean old images
docker-compose up --build
```

---

## API Usage

### `POST /ingest`

- Reads the JSON document file
- Embeds all abstracts using OpenAI
- Stores embedded documents in memory

```bash
curl -X POST http://localhost:8000/ingest
```

---

### `POST /query`

Takes a query, finds most relevant documents, and generates an answer using the LLM.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the RET gene?",
    "top_k": 1
}'
```

Response:

```json
{
  "answer": "The RET gene plays a crucial role in ...",
  "context": [
    {
      "title": "...",
      "pubmed_id": "...",
      "abstract": "..."
    }
  ]
}
```

---

## Design Decisions

### Dynamic Embedding on Ingest
- **Why**: Ensures embeddings match current document content.
- **Avoids**: Stale or incorrect vectors if `pubmed_docs.json` changes.

### In-Memory Store (No ChromaDB/FAISS)
- **Why**: Simpler, smaller image, faster iteration.
- **Tradeoff**: No persistence across container restarts (acceptable for small datasets or demos).

### OpenAI for Both Embedding and Generation
- **Why**: Removes GPU/CPU dependency, minimizes Docker image size.
- **Result**: Lightweight build and cloud-powered intelligence.

### Dockerized with `docker-compose`
- **Why**: Allows quick, reproducible setup without system dependencies.
- **Improvement**: Uses `.env` and `config.py` to inject secrets safely.

### Code Structure (FastAPI + RAG module)
- Keeps routing clean and logic isolated.
- Makes the code maintainable and easy to test.

---

## Future Improvements

- Add persistent storage (SQLite, ChromaDB, TinyDB)
- Add file upload or UI for dynamic document addition
- Add chunking for long documents
- Add chat history support
- Use LangChain or LlamaIndex for more features (if needed)
- Add unit tests
- Add evaluation

---

## Example Document Format

```json
[
  {
    "title": "The role of ret gene in the pathogenesis of Hirschsprung disease.",
    "pubmed_id": "15858239",
    "abstract": "Hirschsprung disease is a congenital disorder ..."
  },
  ...
]
```

---

## Tools Used

- **FastAPI** – Web framework
- **OpenAI Python SDK** – Embedding & generation
- **NumPy** – Vector math
- **Docker + Compose** – Containerization
- **dotenv** – Secure config loading

---

import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from docsassist.index import Index

ROOT = Path(__file__).resolve().parents[2]
SOURCE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,60}\.md$")
MAX_DOCUMENT = 20_000
MAX_DOCUMENTS = 50

app = FastAPI(title="Docs assistant")
INDEX = Index()


def load_corpus():
    INDEX.documents.clear()
    INDEX.chunks.clear()
    for path in sorted((ROOT / "corpus").glob("*.md")):
        INDEX.add(str(path.relative_to(ROOT)), path.read_text(encoding="utf-8"))


load_corpus()


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class Document(BaseModel):
    name: str
    text: str = Field(min_length=1)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "documents": len(INDEX.documents), "chunks": len(INDEX.chunks)}


@app.post("/ask")
def ask(body: Question):
    return INDEX.answer(body.question, body.top_k)


@app.get("/documents")
def documents():
    return {"documents": [{"source": source, "chunks": sum(1 for item in INDEX.chunks if item["source"] == source)} for source in sorted(INDEX.documents)]}


@app.post("/documents", status_code=201)
def add_document(body: Document):
    if not SOURCE.fullmatch(body.name):
        raise HTTPException(status_code=422, detail="name must be a lowercase markdown file name such as runbook.md")
    if len(body.text) > MAX_DOCUMENT:
        raise HTTPException(status_code=413, detail=f"document is over {MAX_DOCUMENT} characters")
    source = f"uploaded/{body.name}"
    if source not in INDEX.documents and len(INDEX.documents) >= MAX_DOCUMENTS:
        raise HTTPException(status_code=409, detail=f"the index already holds {MAX_DOCUMENTS} documents")
    INDEX.add(source, body.text)
    return {"source": source, "chunks": sum(1 for item in INDEX.chunks if item["source"] == source)}

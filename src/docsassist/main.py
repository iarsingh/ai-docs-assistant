from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from docsassist.index import answer

app = FastAPI(title="Docs assistant")
CORPUS = [
    (str(path.relative_to(Path(__file__).resolve().parents[2])), path.read_text(encoding="utf-8"))
    for path in sorted((Path(__file__).resolve().parents[2] / "corpus").glob("*.md"))
]


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(body: Question):
    return answer(CORPUS, body.question)

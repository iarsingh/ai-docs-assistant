import hashlib
import math
import re
from pathlib import Path

DIM = 64


def embed(text):
    vector = [0.0] * DIM
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode()).digest()
        vector[digest[0] % DIM] += 1.0 if digest[1] % 2 == 0 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left, right):
    return sum(a * b for a, b in zip(left, right))


def search(corpus, question, limit=2):
    query = embed(question)
    scored = []
    for path, text in corpus:
        score = cosine(query, embed(text))
        scored.append({"source": path, "text": text.strip(), "score": round(score, 4)})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]


STOP = {"the", "a", "an", "is", "of", "and", "to", "in", "what", "why", "does"}


def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOP


def answer(corpus, question):
    hits = search(corpus, question)
    overlap = words(question) & words(hits[0]["text"]) if hits else set()
    if not hits or len(overlap) < 2:
        return {"answered": False, "answer": "No corpus passage is close enough. I will not answer from outside these files.", "passages": hits}
    best = hits[0]
    return {"answered": True, "answer": best["text"], "passages": hits}

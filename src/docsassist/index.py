import hashlib
import math
import re

DIM = 256
MIN_OVERLAP = 2
STOP = {"the", "a", "an", "is", "of", "and", "to", "in", "what", "why", "does", "do", "it", "on", "for", "how", "i", "we", "be"}


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def words(text):
    return set(tokens(text)) - STOP


def embed(text):
    vector = [0.0] * DIM
    for token in tokens(text):
        if token in STOP:
            continue
        digest = hashlib.sha256(token.encode()).digest()
        vector[int.from_bytes(digest[:2], "big") % DIM] += 1.0 if digest[2] % 2 == 0 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left, right):
    return sum(a * b for a, b in zip(left, right))


def chunk(source, text):
    chunks = []
    heading = None
    buffer = []
    start = None

    def flush():
        if buffer:
            body = " ".join(line.strip() for line in buffer).strip()
            if body:
                chunks.append({"source": source, "heading": heading, "line": start, "text": body})
        buffer.clear()

    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("#"):
            flush()
            heading = line.lstrip("#").strip()
            start = None
            continue
        if not line.strip():
            flush()
            start = None
            continue
        if start is None:
            start = number
        buffer.append(line)
    flush()
    return chunks


class Index:
    def __init__(self):
        self.documents = {}
        self.chunks = []

    def add(self, source, text):
        self.documents[source] = text
        self.chunks = [item for item in self.chunks if item["source"] != source]
        for item in chunk(source, text):
            searchable = f"{item['heading'] or ''} {item['text']}"
            self.chunks.append({**item, "vector": embed(searchable), "words": words(searchable)})

    def search(self, question, limit=3):
        query = embed(question)
        query_words = words(question)
        scored = []
        for item in self.chunks:
            overlap = query_words & item["words"]
            scored.append(
                {
                    "source": item["source"],
                    "heading": item["heading"],
                    "line": item["line"],
                    "text": item["text"],
                    "score": round(cosine(query, item["vector"]), 4),
                    "overlap": sorted(overlap),
                }
            )
        scored.sort(key=lambda hit: (len(hit["overlap"]), hit["score"]), reverse=True)
        return scored[:limit]

    def answer(self, question, limit=3):
        hits = self.search(question, limit)
        if not hits or len(hits[0]["overlap"]) < MIN_OVERLAP:
            return {
                "answered": False,
                "answer": "No corpus passage is close enough. I will not answer from outside these files.",
                "citations": [],
                "passages": hits,
            }
        best = hits[0]
        citation = f"{best['source']}:{best['line']}" + (f" ({best['heading']})" if best["heading"] else "")
        return {"answered": True, "answer": best["text"], "citations": [citation], "passages": hits}


def answer(corpus, question):
    index = Index()
    for source, text in corpus:
        index.add(source, text)
    return index.answer(question)

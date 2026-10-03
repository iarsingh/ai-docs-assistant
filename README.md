# AI documentation assistant

Level: Advanced

Skills: Retrieval, hashed embeddings, a local vector index, FastAPI

Questions are embedded with a hashed bag of tokens and compared to the markdown files in `corpus/`. The answer is the closest passage. If nothing is close, the API says so and does not invent a paragraph.

There is no hosted model and no API key. The index is the list of vectors built at startup from those files.

```bash
pip install -r requirements.txt
pytest -q
PYTHONPATH=src uvicorn docsassist.main:app --reload
```


# AI documentation assistant

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/docsassist/main.py`](src/docsassist/main.py) | HTTP handlers: `GET /healthz`, `POST /ask`, `GET /documents`, `POST /documents` |
| [`src/docsassist/index.py`](src/docsassist/index.py) | Functions: `tokens`, `words`, `embed`, `cosine`, `chunk`, `answer`, `flush` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`tests/test_docs.py`](tests/test_docs.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`corpus/metric.md`](corpus/metric.md) | Project explanations or operating notes |
| [`corpus/refusals.md`](corpus/refusals.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn docsassist.main:app --reload
```

<!-- project-guide:end -->

Level: Advanced

Skills: retrieval, chunking, hashed embeddings, a local vector index, citations, FastAPI

Markdown in `corpus/` is split into chunks at each heading and blank line. Each chunk keeps its file, heading, and starting line. A question is embedded with a hashed bag of tokens and ranked against the chunks. The answer is the best chunk, with a citation such as `corpus/rollback.md:7 (Who approves)`.

If the best chunk does not share at least two meaningful words with the question, the API says so and does not invent a paragraph. "What is the cafeteria menu?" is refused.

There is no hosted model and no API key. The index lives in memory and is rebuilt from `corpus/` at startup.

```bash
pip install -r requirements.txt
pytest -q
PYTHONPATH=src uvicorn docsassist.main:app --reload
```

| Method and path | Does |
| --- | --- |
| `POST /ask` | `question` and optional `top_k` (1 to 10). Returns the answer, citations, and ranked passages |
| `GET /documents` | Indexed files and their chunk counts |
| `POST /documents` | Add `name` (for example `oncall.md`) and `text`. Stored under `uploaded/` |
| `GET /healthz` | Document and chunk counts |

```bash
curl -s -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question":"Who approves a staging pull request?"}'
```

## Limits

- An uploaded name must be a plain lowercase `.md` file name, so it cannot point outside the index.
- A document can be up to 20,000 characters, and the index holds up to 50 documents.
- Uploaded documents live in memory and disappear on restart.

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.

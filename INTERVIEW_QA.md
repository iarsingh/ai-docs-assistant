# ai-docs-assistant — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does ai-docs-assistant address, and what can you demonstrate?

Markdown in `corpus/` is split into chunks at each heading and blank line. Each chunk keeps its file, heading, and starting line. A question is embedded with a hashed bag of tokens and ranked against the chunks. The answer is the best chunk, with a citation such as `corpus/rollback.md:7 (Who approves)`.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/docsassist/main.py`](src/docsassist/main.py): Implementation or supporting configuration.
- [`src/docsassist/ops.py`](src/docsassist/ops.py): Implementation or supporting configuration.
- [`src/docsassist/index.py`](src/docsassist/index.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.
- [`tests/test_docs.py`](tests/test_docs.py): Executable checks and regression examples.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `chunk` and explain the decision it makes?

The main walkthrough here is `chunk(source, text)` in [`src/docsassist/index.py`](src/docsassist/index.py#L33).

```python
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
```

This is an excerpt; follow the source link for the rest of the branches.

The implementation calls `' '.join`, `' '.join((line.strip() for line in buffer)).strip`, `buffer.append`, `buffer.clear`, `chunks.append`, `enumerate`, `flush`, `line.lstrip`, `line.lstrip('#').strip`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `search` have?

`search(self, question, limit=3)` is defined in [`src/docsassist/index.py`](src/docsassist/index.py#L75).

Its return expressions include:

- `scored[:limit]`

It uses `cosine`, `embed`, `len`, `round`, `scored.append`, `scored.sort`, `sorted`, `words`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail='name must be a lowercase markdown file name such as runbook.md')` in [`src/docsassist/main.py`](src/docsassist/main.py#L58).
- `HTTPException(status_code=413, detail=f'document is over {MAX_DOCUMENT} characters')` in [`src/docsassist/main.py`](src/docsassist/main.py#L60).
- `HTTPException(status_code=409, detail=f'the index already holds {MAX_DOCUMENTS} documents')` in [`src/docsassist/main.py`](src/docsassist/main.py#L63).
- `HTTPException(status_code=404, detail='workspace not found')` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_docs.py`](tests/test_docs.py#L19) contains `test_prod_question_quotes_the_corpus`:

```python
def test_prod_question_quotes_the_corpus():
    body = ask("platform refuses prod latest")
    assert body["answered"] is True
    assert "refuses prod" in body["answer"]
    assert body["citations"] == ["corpus/refusals.md:1"]
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/docsassist/main.py`](src/docsassist/main.py#L41).
- `POST /ask` → `ask` in [`src/docsassist/main.py`](src/docsassist/main.py#L46).
- `GET /documents` → `documents` in [`src/docsassist/main.py`](src/docsassist/main.py#L51).
- `POST /documents` → `add_document` in [`src/docsassist/main.py`](src/docsassist/main.py#L56).
- `GET /readyz` → `readyz` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L44).
- `POST /workspaces` → `create_workspace` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L49).
- `GET /workspaces` → `list_workspaces` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L66).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/docsassist/ops.py`](src/docsassist/ops.py#L73).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `STOP` in [`src/docsassist/index.py`](src/docsassist/index.py); `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/docsassist/ops.py`](src/docsassist/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `chunk`?

In [`src/docsassist/index.py`](src/docsassist/index.py#L33), `chunk(source, text)` receives the inputs. The function computes these intermediate values:

- `chunks = []`
- `heading = None`
- `buffer = []`
- `start = None`

Its result is defined by:

- `chunks`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/docsassist/index.py`](src/docsassist/index.py#L33) branches on:

- `buffer`
- `line.startswith('#')`
- `not line.strip()`
- `start is None`
- `body`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 14. What does the operations plane add, and where is its limit?

[`src/docsassist/ops.py`](src/docsassist/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.

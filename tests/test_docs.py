import pytest
from fastapi.testclient import TestClient

from docsassist.index import chunk
from docsassist.main import app, load_corpus

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_index():
    load_corpus()


def ask(question, **extra):
    return client.post("/ask", json={"question": question, **extra}).json()


def test_prod_question_quotes_the_corpus():
    body = ask("platform refuses prod latest")
    assert body["answered"] is True
    assert "refuses prod" in body["answer"]
    assert body["citations"] == ["corpus/refusals.md:1"]


def test_unrelated_question_is_refused():
    body = ask("What is the cafeteria menu?")
    assert body["answered"] is False
    assert body["citations"] == []


def test_heading_is_part_of_the_citation():
    body = ask("Who approves a staging pull request?")
    assert body["answered"] is True
    assert body["citations"] == ["corpus/rollback.md:7 (Who approves)"]


def test_rollback_question_finds_the_right_chunk():
    body = ask("How do we rollback with Argo CD?")
    assert "reverting the commit" in body["answer"]


def test_chunks_split_on_headings_and_blank_lines():
    chunks = chunk("x.md", "# One\nfirst line\nsecond line\n\nthird\n# Two\nfourth\n")
    assert [(item["heading"], item["line"], item["text"]) for item in chunks] == [
        ("One", 2, "first line second line"),
        ("One", 5, "third"),
        ("Two", 7, "fourth"),
    ]


def test_uploaded_document_becomes_searchable():
    created = client.post("/documents", json={"name": "oncall.md", "text": "# Paging\nThe pager changes hands every Monday at nine."})
    assert created.status_code == 201
    body = ask("When does the pager change hands?")
    assert body["answered"] is True
    assert body["citations"][0].startswith("uploaded/oncall.md")


def test_bad_document_name_is_refused():
    response = client.post("/documents", json={"name": "../../etc/passwd", "text": "x"})
    assert response.status_code == 422


def test_top_k_limits_passages_and_documents_are_listed():
    assert len(ask("platform prod latest", top_k=1)["passages"]) == 1
    sources = [row["source"] for row in client.get("/documents").json()["documents"]]
    assert sources == ["corpus/metric.md", "corpus/refusals.md", "corpus/rollback.md"]

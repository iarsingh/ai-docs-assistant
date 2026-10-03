from fastapi.testclient import TestClient

from docsassist.main import app

client = TestClient(app)


def test_prod_question_quotes_the_corpus():
    body = client.post("/ask", json={"question": "platform refuses prod latest"}).json()
    assert body["answered"] is True
    assert "refuses prod" in body["answer"]


def test_unrelated_question_is_refused():
    body = client.post("/ask", json={"question": "What is the cafeteria menu?"}).json()
    assert body["answered"] is False

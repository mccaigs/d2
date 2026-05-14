import json

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _collect(message: str) -> str:
    response = client.post("/api/chat/stream", json={"message": message})
    assert response.status_code == 200
    body = response.text
    assert "data:" in body
    return body


def test_chat_stream_product_query() -> None:
    body = _collect("What is Bidworx?")
    assert "Bidworx" in body
    assert "metadata" in body


def test_chat_stream_compliance_query() -> None:
    body = _collect("What are the likely compliance risks?")
    assert "Compliance" in body or "compliance" in body


def test_metadata_is_json() -> None:
    body = _collect("What evidence do we need to support this claim?")
    metadata_lines = [
        line.removeprefix("data: ").strip()
        for line in body.splitlines()
        if line.startswith("data:") and '"type": "metadata"' in line
    ]
    assert metadata_lines
    parsed = json.loads(metadata_lines[-1])
    assert parsed["sources"]

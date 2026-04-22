import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_profile_endpoint() -> None:
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "headline" in data


def test_suggestions_endpoint() -> None:
    response = client.get("/api/suggestions")
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
    assert len(data["prompts"]) > 0


def test_chat_stream_endpoint() -> None:
    response = client.post(
        "/api/chat/stream",
        json={"message": "What does David do?"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


def _collect(message: str) -> str:
    response = client.post("/api/chat/stream", json={"message": message})
    assert response.status_code == 200
    return response.text


def _events(body: str) -> list[dict]:
    events: list[dict] = []
    for raw in body.split("\n\n"):
        line = raw.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        events.append(json.loads(payload))
    return events


def _metadata(body: str) -> dict:
    for event in _events(body):
        if event.get("type") == "metadata":
            return event
    raise AssertionError("metadata event not found")


def _answer_text(body: str) -> str:
    parts = [
        event.get("content", "")
        for event in _events(body)
        if event.get("type") == "chunk"
    ]
    return "".join(parts)


def test_profile_query_uses_cv_profile_overview() -> None:
    body = _collect("What does David do?")
    metadata = _metadata(body)
    answer = _answer_text(body)
    assert metadata["intent"] == "profile_overview"
    assert "AI architect" in answer


def test_stack_query_returns_grouped_stack() -> None:
    body = _collect("What tech stack does he use?")
    metadata = _metadata(body)
    answer = _answer_text(body)
    assert metadata["intent"] == "technical_stack"
    assert "Backend" in answer
    assert "Frontend" in answer


def test_contact_query_returns_cta_without_phone() -> None:
    body = _collect("How do I contact David?")
    metadata = _metadata(body)
    answer = _answer_text(body)
    assert metadata["intent"] == "contact"
    assert metadata["cta"] == {
        "type": "link",
        "label": "Open contact form",
        "href": "/contact?intent=general",
    }
    assert "contact page" in answer.lower()
    assert "07565" not in answer
    assert "@" not in answer


def test_day_rate_query_routes_to_engagement_preferences_with_cta() -> None:
    body = _collect("What are David's day rates?")
    metadata = _metadata(body)
    answer = _answer_text(body)
    assert metadata["intent"] == "engagement_preferences"
    assert metadata["cta"] == {
        "type": "link",
        "label": "Open contact form",
        "href": "/contact?intent=hire",
    }
    assert "Commercial guide" in answer

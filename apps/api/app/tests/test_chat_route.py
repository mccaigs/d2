import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_profile_endpoint():
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "headline" in data


def test_suggestions_endpoint():
    response = client.get("/api/suggestions")
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
    assert len(data["prompts"]) > 0


def test_chat_stream_endpoint():
    response = client.post(
        "/api/chat/stream",
        json={"message": "What is David strongest at?"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


def _collect(message: str) -> str:
    response = client.post("/api/chat/stream", json={"message": message})
    assert response.status_code == 200
    return response.text


def test_chat_stream_contact_query_sets_form_flag():
    body = _collect("How do I contact David?")
    assert '"intent": "contact"' in body
    assert '"show_contact_form": true' in body
    assert '"contact_reason": "high_intent"' in body


def test_chat_stream_rates_query_sets_form_flag():
    body = _collect("What are David's day rates?")
    assert '"intent": "contact"' in body
    assert '"show_contact_form": true' in body


def test_chat_stream_projects_query_does_not_set_form_flag():
    body = _collect("Has David built recruiter tools?")
    assert '"intent": "projects"' in body
    assert '"show_contact_form": false' in body


def test_chat_stream_role_fit_does_not_set_form_flag():
    body = _collect("Would David suit a solutions architect role?")
    assert '"intent": "role_fit"' in body
    assert '"show_contact_form": false' in body


def test_chat_stream_engagement_with_high_intent_sets_flag():
    body = _collect("Can David be hired for a short project?")
    # engagement intent with "hire" token → conversion CTA
    assert '"show_contact_form": true' in body


def _answer_text(body: str) -> str:
    # Stitch the streamed chunks back into the answer body for shape checks.
    import json as _json
    out: list[str] = []
    for raw in body.split("\n\n"):
        line = raw.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            event = _json.loads(payload)
        except ValueError:
            continue
        if event.get("type") == "chunk":
            out.append(event.get("content", ""))
    return "".join(out)


def test_contact_rates_subtype_leads_with_pricing():
    body = _collect("What are David's day rates?")
    answer = _answer_text(body)
    assert "indicative" in answer.lower()
    # Pricing block should precede the engagements block
    assert answer.find("indicative view of pricing") < answer.find("engagements that fit him best")


def test_contact_details_subtype_leads_with_contact_route():
    body = _collect("How do I contact David?")
    answer = _answer_text(body)
    assert "reach david" in answer.lower()
    # Should not lead with a pricing block
    assert "indicative view of pricing" not in answer


def test_contact_project_enquiry_subtype_leads_with_fit():
    body = _collect("Can David help us build an MVP?")
    answer = _answer_text(body)
    assert "strong fit" in answer.lower()
    # Fit / engagements must come before pricing in this subtype
    assert answer.find("engagements that fit him best") < answer.find("indicative view of pricing")

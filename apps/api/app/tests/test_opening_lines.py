"""Integration tests: question → intent → answer opening line.

These prove that the full pipeline (classify_question_intent → ResponseStyle
→ build_answer) produces the correct opening shape for each question type.
"""

import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _answer_text(body: str) -> str:
    """Stitch streamed chunks back into the full answer."""
    out: list[str] = []
    for raw in body.split("\n\n"):
        line = raw.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            event = json.loads(payload)
        except ValueError:
            continue
        if event.get("type") == "chunk":
            out.append(event.get("content", ""))
    return "".join(out)


def _get_answer(message: str) -> str:
    response = client.post("/api/chat/stream", json={"message": message})
    assert response.status_code == 200
    return _answer_text(response.text)


# 1. "What can David do?" → starts with "David"
def test_capability_opening():
    answer = _get_answer("What can David do?")
    assert answer.startswith("David"), f"Expected 'David...', got: {answer[:80]}"
    assert not answer.startswith("Yes"), f"Must not start with 'Yes', got: {answer[:80]}"


# 2. "Is David a good fit for this role?" → starts with "Yes — David"
def test_fit_yes_no_opening():
    answer = _get_answer("Is David a good fit for this role?")
    assert answer.startswith("Yes"), f"Expected 'Yes — David...', got: {answer[:80]}"
    assert "David" in answer[:40], f"Expected 'David' near start, got: {answer[:80]}"


# 3. "What is David strongest at technically?" → starts with "David is strongest at"
def test_strengths_opening():
    answer = _get_answer("What is David strongest at technically?")
    assert answer.startswith("David is strongest at"), f"Expected 'David is strongest at...', got: {answer[:80]}"


# 4. "What has David built?" → starts with "David has built"
def test_experience_opening():
    answer = _get_answer("What has David built?")
    assert answer.startswith("David has built"), f"Expected 'David has built...', got: {answer[:80]}"


# 5. "Who is David?" → starts with "David is"
def test_identity_summary_opening():
    answer = _get_answer("Who is David?")
    assert answer.startswith("David is"), f"Expected 'David is...', got: {answer[:80]}"


# 6. "How does David work?" → starts with "David works best"
def test_working_style_opening():
    answer = _get_answer("How does David work?")
    assert answer.startswith("David works best"), f"Expected 'David works best...', got: {answer[:80]}"


# 7. "Is David available for short projects or contract work?" → starts with "Yes — David is available"
def test_availability_commercial_opening():
    answer = _get_answer("Is David available for short projects or contract work?")
    assert answer.startswith("Yes"), f"Expected 'Yes — David is available...', got: {answer[:80]}"
    assert "available" in answer[:60].lower(), f"Expected 'available' near start, got: {answer[:80]}"


# 8. fallback: "Tell me more about David in general" → natural, no "Yes —"
def test_general_profile_fallback():
    answer = _get_answer("Tell me more about David in general")
    assert answer.startswith("David"), f"Expected 'David...', got: {answer[:80]}"
    assert not answer.startswith("Yes"), f"Must not start with 'Yes', got: {answer[:80]}"


# 9. streaming: streamed output is multiple chunks, not one large dump
def test_streaming_emits_multiple_chunks():
    response = client.post(
        "/api/chat/stream",
        json={"message": "What is David strongest at?"},
    )
    assert response.status_code == 200
    chunk_count = 0
    for raw in response.text.split("\n\n"):
        line = raw.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            event = json.loads(payload)
        except ValueError:
            continue
        if event.get("type") == "chunk":
            chunk_count += 1
    assert chunk_count > 1, f"Expected multiple chunks, got {chunk_count}"

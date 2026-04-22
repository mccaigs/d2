import pytest
from app.services.answer_builder import build_answer, get_follow_ups


def test_build_answer_skills():
    data = {
        "technical_skills": [
            {"name": "Python", "category": "backend", "strength": "strong"}
        ],
        "working_style": ["Builds quickly"],
    }
    answer = build_answer("skills", data)
    assert "Python" in answer
    assert "Backend" in answer


def test_build_answer_unknown():
    answer = build_answer("unknown", {})
    assert "professional background" in answer.lower()


def test_get_follow_ups():
    follow_ups = get_follow_ups("skills")
    assert len(follow_ups) > 0
    assert isinstance(follow_ups[0], str)

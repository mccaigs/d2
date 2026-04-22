"""Tests for the centralised response-style selection."""

import pytest
from app.services.question_intent import QuestionIntent
from app.services.response_style import ResponseStyle, select_response_style


def test_capability_style_forbids_yes_no():
    style = select_response_style(QuestionIntent.CAPABILITY)
    assert not style.allow_yes_no_prefix
    assert "David" in style.opening_pattern
    assert "Yes" not in style.opening_pattern


def test_fit_yes_no_style_allows_yes_no():
    style = select_response_style(QuestionIntent.FIT_YES_NO)
    assert style.allow_yes_no_prefix
    assert style.opening_pattern.startswith("Yes")


def test_strengths_style():
    style = select_response_style(QuestionIntent.STRENGTHS)
    assert not style.allow_yes_no_prefix
    assert "strongest" in style.opening_pattern


def test_experience_style():
    style = select_response_style(QuestionIntent.EXPERIENCE)
    assert not style.allow_yes_no_prefix
    assert "built" in style.opening_pattern


def test_identity_summary_style():
    style = select_response_style(QuestionIntent.IDENTITY_SUMMARY)
    assert not style.allow_yes_no_prefix
    assert style.opening_pattern.startswith("David is")


def test_working_style_style():
    style = select_response_style(QuestionIntent.WORKING_STYLE)
    assert not style.allow_yes_no_prefix
    assert "works best" in style.opening_pattern


def test_availability_commercial_style():
    style = select_response_style(QuestionIntent.AVAILABILITY_COMMERCIAL)
    assert style.allow_yes_no_prefix
    assert "available" in style.opening_pattern


def test_general_profile_style_forbids_yes_no():
    style = select_response_style(QuestionIntent.GENERAL_PROFILE)
    assert not style.allow_yes_no_prefix
    assert "Yes" not in style.opening_pattern


def test_all_intents_have_styles():
    for intent in QuestionIntent:
        style = select_response_style(intent)
        assert isinstance(style, ResponseStyle)
        assert "{detail}" in style.opening_pattern


def test_style_is_frozen():
    style = select_response_style(QuestionIntent.CAPABILITY)
    with pytest.raises(AttributeError):
        style.allow_yes_no_prefix = True  # type: ignore[misc]

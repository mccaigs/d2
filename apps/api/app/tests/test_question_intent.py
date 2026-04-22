"""Tests for the deterministic question-shape classifier."""

import pytest
from app.services.question_intent import QuestionIntent, classify_question_intent


# ---- capability ----

@pytest.mark.parametrize("question", [
    "What can David do?",
    "What does David do?",
    "What kind of work does David do?",
    "What is David able to help with?",
])
def test_capability(question: str):
    assert classify_question_intent(question) == QuestionIntent.CAPABILITY


# ---- fit_yes_no ----

@pytest.mark.parametrize("question", [
    "Is David a good fit for this role?",
    "Would David suit this role?",
    "Can David do this role?",
    "Is David suitable for this position?",
    "Would David be a good fit for a solutions architect role?",
])
def test_fit_yes_no(question: str):
    assert classify_question_intent(question) == QuestionIntent.FIT_YES_NO


# ---- strengths ----

@pytest.mark.parametrize("question", [
    "What is David strongest at?",
    "What is David strongest at technically?",
    "What are David's strongest skills?",
    "Where is David best technically?",
    "What does David do best?",
])
def test_strengths(question: str):
    assert classify_question_intent(question) == QuestionIntent.STRENGTHS


# ---- experience ----

@pytest.mark.parametrize("question", [
    "What has David built?",
    "What projects has David worked on?",
    "What production AI systems has David built?",
    "What has he actually made?",
])
def test_experience(question: str):
    assert classify_question_intent(question) == QuestionIntent.EXPERIENCE


# ---- identity_summary ----

@pytest.mark.parametrize("question", [
    "Who is David?",
    "Tell me about David",
    "Summarise David",
    "Give me an overview of David",
])
def test_identity_summary(question: str):
    assert classify_question_intent(question) == QuestionIntent.IDENTITY_SUMMARY


# ---- working_style ----

@pytest.mark.parametrize("question", [
    "How does David work?",
    "What is David like to work with?",
    "How does he approach projects?",
    "What is his working style?",
])
def test_working_style(question: str):
    assert classify_question_intent(question) == QuestionIntent.WORKING_STYLE


# ---- availability_commercial ----

@pytest.mark.parametrize("question", [
    "Is David available for contract work?",
    "Can I hire David for a short project?",
    "Does David do advisory work?",
    "Is he open to consulting?",
    "Is David available for short projects or contract work?",
])
def test_availability_commercial(question: str):
    assert classify_question_intent(question) == QuestionIntent.AVAILABILITY_COMMERCIAL


# ---- general_profile (fallback) ----

@pytest.mark.parametrize("question", [
    "Tell me more about David in general",
    "David",
    "Hello",
    "",
])
def test_general_profile_fallback(question: str):
    assert classify_question_intent(question) == QuestionIntent.GENERAL_PROFILE

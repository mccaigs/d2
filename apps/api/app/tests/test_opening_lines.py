from app.services.answer_builder import build_answer
from app.services.classifier import classify
from app.services.question_intent import classify_question_intent
from app.services.retriever import retrieve


def _answer(question: str) -> str:
    intent = classify(question)
    q_intent = classify_question_intent(question)
    data, _ = retrieve(intent, question)
    return build_answer(intent, data, question, q_intent)


def test_capability_opening() -> None:
    assert _answer("What can Bidworx do?").startswith("Bidworx")


def test_readiness_opening() -> None:
    assert _answer("Score this opportunity").startswith("Yes")


def test_identity_opening() -> None:
    assert _answer("What is Bidworx?").startswith("Bidworx is")

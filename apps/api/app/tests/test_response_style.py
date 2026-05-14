from app.services.question_intent import QuestionIntent
from app.services.response_style import select_response_style


def test_response_styles_reference_bidworx() -> None:
    for intent in QuestionIntent:
        style = select_response_style(intent)
        assert "Bidworx" in style.opening_pattern

from app.services.question_intent import QuestionIntent, classify_question_intent


def test_identity_summary() -> None:
    assert classify_question_intent("What is Bidworx?") == QuestionIntent.IDENTITY_SUMMARY


def test_bid_readiness_yes_no() -> None:
    assert classify_question_intent("Should we bid?") == QuestionIntent.FIT_YES_NO


def test_strengths() -> None:
    assert classify_question_intent("What makes Bidworx reliable?") == QuestionIntent.STRENGTHS


def test_working_style() -> None:
    assert classify_question_intent("How does Bidworx score tenders?") == QuestionIntent.WORKING_STYLE

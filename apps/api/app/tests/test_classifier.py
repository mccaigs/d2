from app.services.classifier import classify


def test_classify_product_overview() -> None:
    assert classify("What is Bidworx?") == "profile_overview"


def test_classify_tender_workflow() -> None:
    assert classify("Analyse this tender opportunity") == "role_fit"


def test_classify_compliance_risk() -> None:
    assert classify("What are the likely compliance risks?") == "procurement_examples"


def test_classify_evidence_question() -> None:
    assert classify("What evidence do we need to support this claim?") == "capabilities"


def test_unknown() -> None:
    assert classify("What is the capital of France?") == "unknown"

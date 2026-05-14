from app.services.bid_readiness import (
    analyse_tender_text,
    build_tender_analysis_answer,
    tender_source_chips,
)


TENDER_TEXT = """
Contracting authority: Southport NHS Trust.
The supplier must deliver a patient engagement service with mobilisation support.
Responses must include implementation methodology, case study evidence, pricing schedule,
declarations, and cyber security policy.
Evaluation will consider delivery quality, evidence, compliance, and commercial pricing.
"""


def test_bid_readiness_analyser_returns_structured_analysis() -> None:
    analysis = analyse_tender_text(TENDER_TEXT)

    assert analysis.buyer == "Southport NHS Trust"
    assert analysis.buyer_requirements
    assert analysis.submission_requirements
    assert analysis.compliance_risks
    assert 0 <= analysis.readiness.score <= 100


def test_tender_answer_contains_required_sections() -> None:
    analysis = analyse_tender_text(TENDER_TEXT)
    answer = build_tender_analysis_answer(analysis)

    assert "**Opportunity summary**" in answer
    assert "**Buyer requirements**" in answer
    assert "**Submission requirements**" in answer
    assert "**Compliance risks**" in answer
    assert "**Evidence needed**" in answer
    assert "**Bid readiness score**" in answer
    assert "**Recommended next step**" in answer


def test_tender_source_chips_include_rules_and_evidence() -> None:
    analysis = analyse_tender_text(TENDER_TEXT)
    labels = {chip.label for chip in tender_source_chips(analysis)}

    assert "Pasted Tender Text" in labels
    assert "Compliance Rules" in labels
    assert "Scoring Rules" in labels
    assert "Evidence Categories" in labels

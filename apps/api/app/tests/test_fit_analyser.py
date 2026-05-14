from app.services.fit_analyser import analyse_fit


TENDER_TEXT = """
The contracting authority requires a supplier to deliver a software service.
Responses must include implementation methodology, case study evidence,
security policy, pricing schedule, declarations, and risk management plan.
Evaluation will consider requirement coverage, evidence, compliance, and value for money.
"""


def test_bid_readiness_scoring_returns_procurement_shape() -> None:
    result = analyse_fit(TENDER_TEXT)
    assert result["overall_score"] > 50
    assert "bid readiness" in result["fit_label"].lower()
    assert result["breakdown"]["technical"] > 0
    assert result["breakdown"]["product_architecture"] > 0
    assert result["relevant_projects"]


def test_empty_tender_text_returns_no_input() -> None:
    result = analyse_fit("")
    assert result["overall_score"] == 0
    assert result["fit_label"] == "No input"

from app.services.tender_parser import looks_like_tender_text, parse_tender_text


TENDER_TEXT = """
Buyer: Northshire Council.
Tender notice for adult social care services.
The supplier must provide a secure case management service for adult social care.
The solution shall include implementation methodology, service reporting, and data protection controls.
Responses must include a pricing schedule, signed declaration, insurance certificate,
and risk management plan.
Submission is via the procurement portal by 12 May.
The buyer requires case study evidence, GDPR policy detail, social value evidence, and value for money.
Pass/fail checks apply to mandatory documents and eligibility.
"""


def test_looks_like_tender_text_detects_pasted_tender() -> None:
    assert looks_like_tender_text(TENDER_TEXT)


def test_parse_tender_text_extracts_procurement_structure() -> None:
    analysis = parse_tender_text(TENDER_TEXT)

    assert analysis.buyer == "Northshire Council"
    assert analysis.opportunity_type == "Tender"
    assert analysis.buyer_requirements
    assert analysis.submission_requirements
    assert analysis.evidence_needed
    assert analysis.readiness.score > 0


def test_parse_tender_text_flags_compliance_and_scores_rules() -> None:
    analysis = parse_tender_text(TENDER_TEXT)
    risk_areas = {risk.area for risk in analysis.compliance_risks}

    assert "Mandatory documents" in risk_areas
    assert "Pass/fail criteria" in risk_areas
    assert "Unsupported claims" in risk_areas
    assert "compliance_readiness" in analysis.readiness.dimensions
    assert analysis.readiness.dimensions["requirement_coverage"] > 0

from pathlib import Path

from app.services.bid_readiness import analyse_tender_text
from app.services.tender_parser import looks_like_tender_text


SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample_tenders"


def _read_sample(filename: str) -> str:
    return (SAMPLE_DIR / filename).read_text(encoding="utf-8")


def test_clear_strong_sample_is_bid_ready_with_checks() -> None:
    text = _read_sample("clear_strong_opportunity.txt")
    analysis = analyse_tender_text(text)

    assert looks_like_tender_text(text)
    assert analysis.readiness.label == "Bid-ready with checks"
    assert analysis.readiness.score >= 75
    assert analysis.buyer_requirements
    assert analysis.submission_requirements
    assert analysis.evidence_needed


def test_risky_sample_needs_review_before_bid() -> None:
    text = _read_sample("risky_missing_compliance_evidence.txt")
    analysis = analyse_tender_text(text)

    assert looks_like_tender_text(text)
    assert analysis.readiness.label == "Review before bid"
    assert 55 <= analysis.readiness.score < 75
    assert any(risk.severity == "blocker" for risk in analysis.compliance_risks)


def test_poor_fit_sample_returns_cautious_no_bid_band() -> None:
    text = _read_sample("poor_fit_cautious_no_bid.txt")
    analysis = analyse_tender_text(text)

    assert looks_like_tender_text(text)
    assert analysis.readiness.label == "No-bid risk"
    assert analysis.readiness.score < 55
    assert any(risk.area == "Pass/fail criteria" for risk in analysis.compliance_risks)

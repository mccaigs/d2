from pathlib import Path

from app.models.tender import SampleTender

_SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample_tenders"

_SAMPLES = [
    {
        "id": "clear-strong-opportunity",
        "title": "Clear strong opportunity",
        "description": "Well-scoped SaaS tender with explicit evidence, delivery, compliance, and commercial signals.",
        "expected_band": "Bid-ready with checks",
        "filename": "clear_strong_opportunity.txt",
    },
    {
        "id": "risky-missing-compliance-evidence",
        "title": "Risky missing compliance evidence",
        "description": "Promising opportunity with mandatory evidence gaps and pass/fail compliance exposure.",
        "expected_band": "Review before bid",
        "filename": "risky_missing_compliance_evidence.txt",
    },
    {
        "id": "poor-fit-cautious-no-bid",
        "title": "Poor-fit cautious no-bid",
        "description": "Construction-led tender with accreditations and delivery requirements outside the Bidworx evidence base.",
        "expected_band": "No-bid risk",
        "filename": "poor_fit_cautious_no_bid.txt",
    },
]


def list_sample_tenders() -> list[SampleTender]:
    samples: list[SampleTender] = []
    for item in _SAMPLES:
        text = (_SAMPLE_DIR / item["filename"]).read_text(encoding="utf-8")
        samples.append(
            SampleTender(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                expected_band=item["expected_band"],
                text=text,
            )
        )
    return samples

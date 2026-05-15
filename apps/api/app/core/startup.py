import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

REQUIRED_JSON_FILES = [
    "buyer_roles.json",
    "capabilities.json",
    "compliance_rules.json",
    "evidence_categories.json",
    "faqs.json",
    "frameworks.json",
    "procurement_examples.json",
    "product.json",
    "proof_points.json",
    "scoring_rules.json",
    "tenders.json",
    "workflows.json",
]

REQUIRED_SAMPLE_TENDERS = [
    "sample_tenders/clear_strong_opportunity.txt",
    "sample_tenders/risky_missing_compliance_evidence.txt",
    "sample_tenders/poor_fit_cautious_no_bid.txt",
]


def validate_required_data_files(data_dir: Path = DATA_DIR) -> None:
    missing: list[str] = []
    invalid_json: list[str] = []

    for filename in REQUIRED_JSON_FILES:
        path = data_dir / filename
        if not path.exists():
            missing.append(filename)
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            invalid_json.append(filename)

    for filename in REQUIRED_SAMPLE_TENDERS:
        path = data_dir / filename
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            missing.append(filename)

    if missing or invalid_json:
        details: list[str] = []
        if missing:
            details.append(f"missing required data files: {', '.join(missing)}")
        if invalid_json:
            details.append(f"invalid JSON data files: {', '.join(invalid_json)}")
        raise RuntimeError("Bidworx startup check failed: " + "; ".join(details))

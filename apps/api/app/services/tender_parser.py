import json
import re
from pathlib import Path
from typing import Any

from app.models.tender import (
    ComplianceRisk,
    EvidenceNeed,
    ExtractedRequirement,
    ReadinessScore,
    TenderAnalysis,
)

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load(filename: str) -> Any:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _lines(text: str) -> list[str]:
    candidates = re.split(r"[\n\r]+|(?<=[.!?])\s+(?=[A-Z0-9])", text or "")
    return [
        _normalise(line.strip(" -*\t"))
        for line in candidates
        if _normalise(line.strip(" -*\t"))
    ]


def looks_like_tender_text(text: str) -> bool:
    norm = (text or "").lower()
    if len(norm.split()) < 25:
        return False
    signals = [
        "tender",
        "rfp",
        "contracting authority",
        "supplier",
        "submission",
        "deadline",
        "must",
        "shall",
        "evaluation",
        "pricing schedule",
        "mandatory",
        "framework",
    ]
    return sum(1 for signal in signals if signal in norm) >= 2


def _extract_buyer(text: str) -> str | None:
    patterns = [
        r"\b(?:buyer|client|contracting authority|authority)\s*[:\-]\s*([A-Z][A-Za-z0-9 &,.()'-]{2,80})",
        r"\bfor\s+([A-Z][A-Za-z0-9 &,.()'-]{2,80})\s+(?:requires|seeks|is seeking)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" .")
    return None


def _opportunity_type(text: str) -> str:
    norm = text.lower()
    if "framework" in norm or "call-off" in norm or "call off" in norm:
        return "Framework or call-off opportunity"
    if "rfp" in norm or "request for proposal" in norm:
        return "RFP"
    if "tender" in norm:
        return "Tender"
    return "Procurement opportunity"


def _contains_any(text: str, terms: list[str]) -> bool:
    norm = text.lower()
    return any(term in norm for term in terms)


def _extract_requirements(lines: list[str]) -> tuple[list[ExtractedRequirement], list[ExtractedRequirement]]:
    buyer_terms = [
        "requires",
        "requirement",
        "must",
        "shall",
        "deliver",
        "provide",
        "demonstrate",
        "implementation",
        "service",
        "solution",
        "methodology",
    ]
    submission_terms = [
        "submit",
        "submission",
        "deadline",
        "portal",
        "attachment",
        "pricing schedule",
        "declaration",
        "format",
        "word limit",
        "certificate",
    ]

    buyer_requirements: list[ExtractedRequirement] = []
    submission_requirements: list[ExtractedRequirement] = []
    for line in lines:
        if _contains_any(line, submission_terms):
            submission_requirements.append(
                ExtractedRequirement(
                    id=f"sub-{len(submission_requirements) + 1}",
                    text=line,
                    requirement_type="submission",
                    confidence=(
                        "high"
                        if _contains_any(line, ["must", "shall", "deadline", "mandatory"])
                        else "medium"
                    ),
                )
            )
        elif _contains_any(line, buyer_terms):
            buyer_requirements.append(
                ExtractedRequirement(
                    id=f"req-{len(buyer_requirements) + 1}",
                    text=line,
                    requirement_type=(
                        "mandatory"
                        if _contains_any(line, ["must", "shall", "mandatory"])
                        else "scored"
                    ),
                    confidence=(
                        "high"
                        if _contains_any(line, ["must", "shall", "requires"])
                        else "medium"
                    ),
                )
            )
    return buyer_requirements[:8], submission_requirements[:8]


def _extract_evidence(lines: list[str]) -> list[EvidenceNeed]:
    evidence_map = [
        ("Case study", "case_study", ["case study", "case studies", "example", "examples", "reference"]),
        (
            "Delivery methodology",
            "delivery_methodology",
            ["methodology", "implementation plan", "mobilisation", "mobilization"],
        ),
        ("Security policy", "security", ["security", "cyber", "iso", "gdpr", "data protection"]),
        (
            "Insurance or certification",
            "certification",
            ["insurance", "certificate", "certification", "accreditation"],
        ),
        ("Social value evidence", "social_value", ["social value", "community", "sustainability"]),
        ("Risk management", "risk_management", ["risk", "risks", "risk management"]),
        ("Pricing assumption", "pricing_assumption", ["pricing", "price", "commercial", "value for money"]),
        ("Quality assurance", "quality_assurance", ["quality", "qa", "assurance"]),
    ]

    needs: list[EvidenceNeed] = []
    matched_categories: set[str] = set()
    for line in lines:
        for label, category, terms in evidence_map:
            if category in matched_categories:
                continue
            if _contains_any(line, terms):
                needs.append(EvidenceNeed(label=label, category=category, reason=line))
                matched_categories.add(category)
    return needs[:8]


def _compliance_risks(
    lines: list[str],
    submission_requirements: list[ExtractedRequirement],
    evidence_needed: list[EvidenceNeed],
) -> list[ComplianceRisk]:
    rules = _load("compliance_rules.json").get("rules", [])
    norm = " ".join(lines).lower()
    risks: list[ComplianceRisk] = []

    if _contains_any(
        norm,
        ["mandatory", "must", "shall", "attachment", "declaration", "pricing schedule", "certificate"],
    ):
        rule = next((r for r in rules if r.get("id") == "mandatory-documents"), {})
        risks.append(
            ComplianceRisk(
                area=rule.get("label", "Mandatory documents"),
                note=(
                    "The tender contains mandatory or document-led language. Confirm every required "
                    "attachment, declaration, schedule, certificate, and format before proceeding."
                ),
                severity="blocker" if submission_requirements else "risk",
                evidence_needed=[need.label for need in evidence_needed[:4]],
            )
        )

    if _contains_any(norm, ["pass/fail", "pass fail", "fail", "eligibility"]):
        rule = next((r for r in rules if r.get("id") == "pass-fail-criteria"), {})
        risks.append(
            ComplianceRisk(
                area=rule.get("label", "Pass/fail criteria"),
                note="Pass/fail language should be treated separately from scored quality responses.",
                severity="blocker",
                evidence_needed=["Compliance matrix"],
            )
        )

    if _contains_any(
        norm,
        ["demonstrate", "evidence", "case study", "experience", "certification", "policy"],
    ):
        rule = next((r for r in rules if r.get("id") == "unsupported-claims"), {})
        risks.append(
            ComplianceRisk(
                area=rule.get("label", "Unsupported claims"),
                note="Any claim in the response must be mapped to an approved proof point before drafting.",
                severity="risk",
                evidence_needed=[need.label for need in evidence_needed] or ["Approved proof point"],
            )
        )

    if not risks:
        risks.append(
            ComplianceRisk(
                area="Low tender signal",
                note="The pasted text does not expose clear compliance rules. More tender detail is needed before a reliable submission check.",
                severity="review",
                evidence_needed=["Full tender instructions"],
            )
        )
    return risks[:6]


def _dimension_score(count: int, target: int) -> int:
    return max(0, min(round((count / max(target, 1)) * 100), 100))


def _score(
    buyer_requirements: list[ExtractedRequirement],
    submission_requirements: list[ExtractedRequirement],
    compliance_risks: list[ComplianceRisk],
    evidence_needed: list[EvidenceNeed],
    text: str,
) -> ReadinessScore:
    dimensions = _load("scoring_rules.json").get("dimensions", [])
    weights = {item["id"]: float(item["weight"]) for item in dimensions}
    blocker_count = sum(1 for risk in compliance_risks if risk.severity == "blocker")
    risk_count = sum(1 for risk in compliance_risks if risk.severity == "risk")

    dimension_scores = {
        "requirement_coverage": _dimension_score(len(buyer_requirements), 5),
        "evidence_strength": _dimension_score(len(evidence_needed), 5),
        "compliance_readiness": max(0, 100 - (30 * blocker_count) - (15 * risk_count)),
        "delivery_risk": (
            75
            if _contains_any(text, ["implementation", "mobilisation", "mobilization", "risk", "sla", "kpi"])
            else 45
        ),
        "commercial_fit": (
            75
            if _contains_any(
                text,
                ["price", "pricing", "value for money", "budget", "commercial", "contract value"],
            )
            else 45
        ),
    }

    weighted = sum(dimension_scores[key] * weights.get(key, 0) for key in dimension_scores)
    score = max(0, min(round(weighted), 100))
    if score >= 75:
        label = "Bid-ready with checks"
    elif score >= 55:
        label = "Review before bid"
    else:
        label = "No-bid risk"
    return ReadinessScore(score=score, label=label, dimensions=dimension_scores)


def _summary(
    buyer: str | None,
    opportunity_type: str,
    buyer_requirements: list[ExtractedRequirement],
    submission_requirements: list[ExtractedRequirement],
    compliance_risks: list[ComplianceRisk],
) -> str:
    buyer_text = buyer or "the buyer"
    requirement_count = len(buyer_requirements)
    submission_count = len(submission_requirements)
    blocker_count = sum(1 for risk in compliance_risks if risk.severity == "blocker")
    return (
        f"{opportunity_type} for {buyer_text}. "
        f"Bidworx extracted {requirement_count} buyer requirement"
        f"{'' if requirement_count == 1 else 's'} and {submission_count} submission requirement"
        f"{'' if submission_count == 1 else 's'}. "
        f"{blocker_count} blocker risk{'' if blocker_count == 1 else 's'} need review before drafting."
    )


def parse_tender_text(text: str) -> TenderAnalysis:
    clean_text = _normalise(text)
    lines = _lines(text)
    buyer = _extract_buyer(text)
    opportunity_type = _opportunity_type(text)
    buyer_requirements, submission_requirements = _extract_requirements(lines)
    evidence_needed = _extract_evidence(lines)
    compliance_risks = _compliance_risks(lines, submission_requirements, evidence_needed)
    readiness = _score(
        buyer_requirements,
        submission_requirements,
        compliance_risks,
        evidence_needed,
        clean_text.lower(),
    )

    return TenderAnalysis(
        buyer=buyer,
        opportunity_type=opportunity_type,
        opportunity_summary=_summary(
            buyer,
            opportunity_type,
            buyer_requirements,
            submission_requirements,
            compliance_risks,
        ),
        buyer_requirements=buyer_requirements,
        submission_requirements=submission_requirements,
        compliance_risks=compliance_risks,
        evidence_needed=evidence_needed,
        readiness=readiness,
    )

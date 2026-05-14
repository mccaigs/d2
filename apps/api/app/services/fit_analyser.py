"""Deterministic bid readiness analyser.

The route and response model keep the existing "fit" contract so the frontend
stream stays stable, but the domain is now procurement opportunity scoring.

No LLM. Scoring is token / phrase-based against tender text and structured
Bidworx rules.
"""

import re
from typing import Any


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenise(text: str) -> set[str]:
    norm = _normalise(text)
    norm = re.sub(r"[^\w\s\-\/\.]", " ", norm)
    return {t for t in norm.split() if len(t) > 1}


def _any_hit(norm: str, tokens: set[str], terms: list[str]) -> bool:
    for term in terms:
        if " " in term or "-" in term or "/" in term:
            if term in norm:
                return True
        elif term in tokens:
            return True
    return False


def _count_hits(norm: str, tokens: set[str], terms: list[str]) -> int:
    return sum(1 for term in terms if (term in norm if " " in term or "-" in term or "/" in term else term in tokens))


_REQUIREMENT_COVERAGE = {
    "target": 7,
    "terms": [
        "requirement", "requirements", "scope", "deliverables", "specification",
        "methodology", "implementation", "service", "services", "solution",
        "outcomes", "evaluation", "question", "questions", "lot", "lots",
        "buyer", "authority", "contracting authority",
    ],
}

_EVIDENCE_STRENGTH = {
    "target": 5,
    "terms": [
        "evidence", "case study", "case studies", "example", "examples",
        "experience", "reference", "references", "certification",
        "accreditation", "policy", "proof", "demonstrate", "demonstrates",
    ],
}

_COMPLIANCE_READINESS = {
    "target": 5,
    "terms": [
        "mandatory", "pass/fail", "pass fail", "shall", "must", "declaration",
        "attachment", "attachments", "certificate", "insurance", "gdpr",
        "security", "iso", "modern slavery", "social value", "pricing schedule",
        "deadline", "portal", "format",
    ],
}

_DELIVERY_RISK = {
    "target": 4,
    "terms": [
        "mobilisation", "mobilization", "implementation plan", "transition",
        "risk", "risks", "sla", "kpi", "complex", "integration",
        "regulated", "critical", "support", "resourcing",
    ],
}

_COMMERCIAL_FIT = {
    "target": 4,
    "terms": [
        "budget", "price", "pricing", "commercial", "value for money",
        "contract value", "term", "duration", "framework", "call-off",
        "call off", "lot", "lots",
    ],
}

_DIMENSIONS = {
    "technical": _REQUIREMENT_COVERAGE,
    "applied_ai": _EVIDENCE_STRENGTH,
    "product_architecture": _COMPLIANCE_READINESS,
    "domain": _DELIVERY_RISK,
    "seniority": _COMMERCIAL_FIT,
}

_DIM_LABELS = {
    "technical": "requirement coverage",
    "applied_ai": "evidence strength",
    "product_architecture": "compliance readiness",
    "domain": "delivery risk clarity",
    "seniority": "commercial fit",
}

_WEIGHTS = {
    "technical": 0.30,
    "applied_ai": 0.30,
    "product_architecture": 0.20,
    "domain": 0.10,
    "seniority": 0.10,
}

_PUBLIC_WEIGHTS = {
    "technical": 0.30,
    "applied_ai": 0.30,
    "product_architecture": 0.20,
    "domain": 0.10,
    "seniority": 0.10,
}


def _dim_score(norm: str, tokens: set[str], dim: dict[str, Any]) -> float:
    hits = _count_hits(norm, tokens, dim["terms"])
    return min(hits / max(dim["target"], 1), 1.0)


def _overall_score(scores: dict[str, float]) -> int:
    weighted = sum(scores[k] * _WEIGHTS[k] for k in _WEIGHTS)

    if scores["product_architecture"] < 0.25:
        weighted = min(weighted, 0.68)
    if scores["applied_ai"] < 0.25:
        weighted = min(weighted, 0.72)

    return round(max(0.0, min(weighted, 1.0)) * 100)


def _label(score: int) -> str:
    if score >= 80:
        return "Strong bid readiness"
    if score >= 65:
        return "Good bid readiness"
    if score >= 50:
        return "Partial bid readiness"
    return "High-risk opportunity"


def _evidence_label(score: float) -> str:
    if score >= 0.75:
        return "direct"
    if score >= 0.55:
        return "strong_adjacent"
    if score > 0:
        return "partial_inference"
    return "not_central"


def _confidence(scores: dict[str, float], token_count: int) -> tuple[str, str]:
    strong = [k for k, v in scores.items() if v >= 0.65]
    if token_count < 20:
        return "low", "Very short tender text; scoring is indicative only"
    if len(strong) >= 3:
        return "high", "Direct signal across requirement coverage, evidence, and compliance dimensions"
    if len(strong) >= 2:
        return "medium", "Useful tender signal with some evidence or compliance areas still requiring review"
    return "low", "Sparse tender signal; more buyer detail and evidence records are needed"


def _select_strengths(norm: str, tokens: set[str]) -> list[str]:
    strengths: list[str] = []
    if _any_hit(norm, tokens, ["requirement", "scope", "deliverables", "question", "evaluation"]):
        strengths.append("Buyer requirements are explicit enough to structure a response plan.")
    if _any_hit(norm, tokens, ["evidence", "case study", "experience", "reference", "demonstrate"]):
        strengths.append("The tender asks for evidence that can be mapped to proof categories.")
    if _any_hit(norm, tokens, ["mandatory", "shall", "must", "declaration", "attachment"]):
        strengths.append("Compliance obligations are visible and can be separated from scored quality answers.")
    if _any_hit(norm, tokens, ["framework", "call-off", "lot", "pricing", "commercial"]):
        strengths.append("Commercial and framework signals are present for opportunity triage.")
    if not strengths:
        strengths.append("The tender can still be triaged, but more buyer detail would improve confidence.")
    return strengths[:5]


def _select_gaps(norm: str, tokens: set[str], scores: dict[str, float]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if scores["applied_ai"] < 0.45:
        gaps.append({
            "area": "Evidence strength",
            "note": "The text does not provide enough signal about required proof points, case studies, policies, or certifications.",
            "tier": "hard",
        })
    if scores["product_architecture"] < 0.45:
        gaps.append({
            "area": "Compliance readiness",
            "note": "Mandatory documents, declarations, pass/fail rules, or submission instructions are not yet clear enough.",
            "tier": "hard",
        })
    if _any_hit(norm, tokens, ["iso", "cyber essentials", "security clearance", "accreditation"]) and not _any_hit(norm, tokens, ["evidence", "certificate", "certification"]):
        gaps.append({
            "area": "Certification evidence",
            "note": "Certification language appears, but the available text does not confirm the supporting evidence needed.",
            "tier": "soft",
        })
    if scores["seniority"] < 0.35:
        gaps.append({
            "area": "Commercial fit",
            "note": "The tender text does not yet expose enough budget, pricing, lot, or contract-term signal.",
            "tier": "risk",
        })
    return gaps[:5]


def _select_projects(norm: str, tokens: set[str]) -> list[dict[str, str]]:
    matches = [
        {
            "name": "Tender opportunity triage",
            "reason": "Relevant for extracting buyer requirements, scoring readiness, and deciding whether to pursue.",
        },
        {
            "name": "Evidence coverage review",
            "reason": "Relevant for mapping response claims to approved proof points and identifying unsupported statements.",
        },
        {
            "name": "Compliance and submission check",
            "reason": "Relevant for mandatory criteria, missing attachments, declarations, and pass/fail risks.",
        },
    ]
    if _any_hit(norm, tokens, ["framework", "call-off", "lot"]):
        matches.append({
            "name": "Framework call-off readiness",
            "reason": "Relevant where the opportunity sits under a framework or lot-specific buying route.",
        })
    return matches[:4]


def _talking_points(norm: str, tokens: set[str], scores: dict[str, float]) -> list[str]:
    points = [
        "Which buyer requirements are mandatory, scored, or implied rather than explicit?",
        "Which claims need approved case studies, policies, certifications, or delivery examples?",
        "Which submission artefacts are missing or unclear?",
    ]
    if scores["product_architecture"] < 0.6:
        points.append("Confirm pass/fail criteria, declaration wording, document formats, and portal submission rules.")
    if scores["seniority"] < 0.5:
        points.append("Clarify pricing model, contract duration, lot structure, and commercial assumptions.")
    return points[:5]


def _build_summary(score: int, label: str, scores: dict[str, float], gaps: list[dict[str, str]]) -> str:
    strongest = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:2]
    strongest_labels = " and ".join(_DIM_LABELS[key] for key, value in strongest if value > 0)
    if not strongest_labels:
        strongest_labels = "limited tender signal"

    if score >= 80:
        opening = f"This is a **strong bid readiness** signal at **{score}/100**."
    elif score >= 65:
        opening = f"This is a **good bid readiness** signal at **{score}/100**, with a few areas to confirm before committing."
    elif score >= 50:
        opening = f"This is a **partial bid readiness** signal at **{score}/100**. There is enough overlap to analyse, but material gaps remain."
    else:
        opening = f"This is a **high-risk opportunity** as written at **{score}/100**. The team should not rely on unsupported assumptions."

    risk_line = "No major blockers were identified from the supplied text."
    if gaps:
        first = gaps[0]
        risk_line = f"The main risk is **{first['area']}**: {first['note']}"

    return (
        f"{opening}\n\n"
        f"The strongest available signal is on {strongest_labels}. {risk_line}\n\n"
        "Recommended next step: map each buyer requirement to approved evidence, then re-score once missing compliance and proof records are captured."
    )


_EMPTY_EVIDENCE = {
    "technical": "not_central",
    "applied_ai": "not_central",
    "product_architecture": "not_central",
    "domain": "not_central",
    "seniority": "not_central",
}


def analyse_fit(job_description: str) -> dict:
    if not job_description or not job_description.strip():
        return {
            "summary": "No tender text was provided, so there is nothing to score against. Paste the tender requirements and try again.",
            "overall_score": 0,
            "fit_label": "No input",
            "breakdown": {
                "technical": 0,
                "applied_ai": 0,
                "product_architecture": 0,
                "domain": 0,
                "seniority": 0,
            },
            "confidence": "low",
            "confidence_reason": "No tender text provided",
            "strengths": [],
            "gaps": [],
            "relevant_projects": [],
            "talking_points": [],
            "role_type": "tender_opportunity",
            "dimension_weights": _PUBLIC_WEIGHTS,
            "dimension_evidence": _EMPTY_EVIDENCE,
        }

    norm = _normalise(job_description)
    tokens = _tokenise(job_description)

    raw_scores = {
        key: _dim_score(norm, tokens, dim)
        for key, dim in _DIMENSIONS.items()
    }
    overall = _overall_score(raw_scores)
    label = _label(overall)
    confidence, confidence_reason = _confidence(raw_scores, len(tokens))
    gaps = _select_gaps(norm, tokens, raw_scores)

    return {
        "summary": _build_summary(overall, label, raw_scores, gaps),
        "overall_score": overall,
        "fit_label": label,
        "breakdown": {key: round(value * 100) for key, value in raw_scores.items()},
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "strengths": _select_strengths(norm, tokens),
        "gaps": gaps,
        "relevant_projects": _select_projects(norm, tokens),
        "talking_points": _talking_points(norm, tokens, raw_scores),
        "role_type": "tender_opportunity",
        "dimension_weights": _PUBLIC_WEIGHTS,
        "dimension_evidence": {key: _evidence_label(value) for key, value in raw_scores.items()},
    }

"""Deterministic answer builder.

Answers are assembled from structured procurement records only. No LLM and no
raw JSON dumping. The pipeline remains:

classifier -> retriever -> answer_builder -> response_style
"""

import re
from typing import Any

from app.services.classifier import Intent
from app.services.question_intent import QuestionIntent
from app.services.response_style import ResponseStyle, select_response_style


FOLLOW_UPS: dict[Intent, list[str]] = {
    "capabilities": [
        "What evidence do we need to support this claim?",
        "What are the likely compliance risks?",
        "Score this opportunity",
    ],
    "technical_stack": [
        "How does deterministic scoring work?",
        "What data does Bidworx analyse?",
        "What evidence sources are supported?",
    ],
    "workflows": [
        "Summarise the buyer requirements",
        "Identify missing submission requirements",
        "What are the likely compliance risks?",
    ],
    "workflows_overview": [
        "Analyse this tender opportunity",
        "What does Bidworx analyse?",
        "Score this opportunity",
    ],
    "procurement_examples": [
        "Identify missing submission requirements",
        "What evidence do we need to support this claim?",
        "Summarise the buyer requirements",
    ],
    "procurement_summary": [
        "What are the likely compliance risks?",
        "Score this opportunity",
        "What evidence do we need to support this claim?",
    ],
    "strengths": [
        "How does Bidworx avoid unsupported claims?",
        "What are the likely compliance risks?",
        "What does Bidworx analyse?",
    ],
    "role_fit": [
        "What evidence do we need to improve the score?",
        "What are the likely compliance risks?",
        "Identify missing submission requirements",
    ],
    "preferred_roles": [
        "Who uses Bidworx?",
        "What does Bidworx analyse?",
        "Score this opportunity",
    ],
    "availability": [
        "Analyse this tender opportunity",
        "What evidence sources are supported?",
        "What are the likely compliance risks?",
    ],
    "proof_points": [
        "How does Bidworx avoid unsupported claims?",
        "What evidence do we need to support this claim?",
        "What source chips are returned?",
    ],
    "engagement": [
        "Analyse this tender opportunity",
        "Score this opportunity",
        "Identify missing submission requirements",
    ],
    "contact": [
        "What does Bidworx analyse?",
        "How does deterministic scoring work?",
        "What are the likely compliance risks?",
    ],
    "faq": [
        "What does Bidworx analyse?",
        "What evidence do we need to support this claim?",
        "Score this opportunity",
    ],
    "profile_overview": [
        "What does Bidworx analyse?",
        "How does Bidworx avoid unsupported claims?",
        "Analyse this tender opportunity",
    ],
    "engagement_preferences": [
        "Who uses Bidworx?",
        "What are the likely compliance risks?",
        "Score this opportunity",
    ],
    "unknown": [],
}


_OUT_OF_SCOPE = (
    "I can only answer questions about Bidworx procurement intelligence, "
    "including tender analysis, buyer requirements, evidence mapping, scoring, "
    "compliance risk, and submission readiness."
)

_INSUFFICIENT_EVIDENCE = (
    "I do not have enough approved procurement evidence to answer that cleanly, "
    "so I would rather flag the gap than invent support."
)

_CONTEXT_PATTERNS: list[tuple[str, str]] = [
    (r"compliance", "compliance risk"),
    (r"evidence|proof|claim", "evidence coverage"),
    (r"buyer|requirement", "buyer requirements"),
    (r"score|readiness|go/no-go", "bid readiness scoring"),
    (r"framework", "framework procurement"),
    (r"submission|attachment", "submission checks"),
]


def _query_context(message: str) -> str | None:
    lowered = (message or "").lower()
    for pattern, label in _CONTEXT_PATTERNS:
        if re.search(pattern, lowered):
            return label
    return None


def _join_lines(parts: list[str]) -> str:
    return "\n".join(part for part in parts if part is not None).strip()


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        cleaned = (item or "").strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
    return ordered


def _comma_list(items: list[str], limit: int | None = None) -> str:
    cleaned = _dedupe(items)
    if limit is not None:
        cleaned = cleaned[:limit]
    return ", ".join(cleaned)


def _bullet_block(title: str, items: list[str], limit: int) -> list[str]:
    cleaned = _dedupe(items)[:limit]
    if not cleaned:
        return []
    return [title, *[f"- {item}" for item in cleaned]]


def _pipe_title(title: str) -> str:
    return title.replace("|", ",").replace("  ", " ").strip(" ,")


def _styled_intro(
    q_intent: QuestionIntent,
    style: ResponseStyle,
    detail: str,
    message: str = "",
) -> str:
    detail_text = detail
    for prefix in ["is ", "supports ", "works best "]:
        if detail_text.startswith(prefix):
            detail_text = detail_text[len(prefix):]
    base = style.opening_pattern.format(subject="Bidworx", detail=detail_text).strip()
    if not base.endswith("."):
        base = f"{base}."
    context = _query_context(message)
    if context and context not in base.lower():
        base = base[:-1] + f", especially for {context}."
    return base


def _answer_profile_overview(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    title = _pipe_title(data.get("title", "procurement intelligence platform"))
    profile = data.get("profile", "")
    capabilities = data.get("capabilities") or []
    ideal_roles = data.get("ideal_roles") or []
    focus = data.get("focus", "")

    if not title and not profile:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, f"is {title}", message),
        "",
        profile,
    ]
    if capabilities:
        lines.append(f"Core operating strengths: {_comma_list(capabilities, 5)}.")
    if ideal_roles:
        lines.append(f"Designed for: {_comma_list(ideal_roles, 5)}.")
    if focus:
        lines.extend(["", focus])
    return _join_lines(lines)


def _answer_capabilities(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    capabilities = data.get("capabilities") or []
    working_style = data.get("working_style") or []
    if not capabilities:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "maps tender requirements to evidence, risk, and scoring outputs", message),
        "",
        "Core capabilities:",
    ]
    for item in capabilities[:6]:
        name = item.get("name", "")
        notes = item.get("notes", "")
        if name:
            lines.append(f"- **{name}:** {notes}")
    if working_style:
        lines.extend(["", *_bullet_block("Operating principles:", working_style, 4)])
    return _join_lines(lines)


def _answer_strengths(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    strengths = data.get("core_strengths") or []
    working_style = data.get("working_style") or []
    if not strengths:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "evidence control, deterministic scoring, and compliance-aware tender analysis", message),
        "",
        *_bullet_block("The strongest themes are:", strengths, 6),
    ]
    if working_style:
        lines.extend(["", *_bullet_block("That shows up as:", working_style, 3)])
    lines.append("")
    lines.append("The important product principle is simple: Bidworx should flag unsupported claims before they reach a buyer.")
    return _join_lines(lines)


def _answer_workflows(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    workflows = data.get("workflows") or []
    if not workflows:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "structured procurement workflows from tender triage through submission readiness", message),
    ]
    for workflow in workflows[:4]:
        name = workflow.get("name", "")
        workflow_type = workflow.get("type", "")
        summary = workflow.get("summary", "")
        if not name:
            continue
        lines.extend(["", f"**{name}**" + (f" - {workflow_type}" if workflow_type else "")])
        if summary:
            lines.append(summary)
        highlights = workflow.get("highlights") or []
        if highlights:
            lines.append(f"Key checks: {_comma_list(highlights, 3)}.")
    return _join_lines(lines)


def _answer_workflows_overview(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    workflows = data.get("workflows") or []
    scoring_rules = data.get("scoring_rules") or []
    evidence_categories = data.get("evidence_categories") or []
    if not workflows:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "tender opportunity triage, evidence coverage review, and compliance checks", message),
        "",
        *_bullet_block("What Bidworx analyses:", [w.get("name", "") for w in workflows], 5),
    ]
    if scoring_rules:
        lines.extend(["", *_bullet_block("Deterministic scoring dimensions:", [r.get("label", "") for r in scoring_rules], 6)])
    if evidence_categories:
        lines.append(f"Evidence categories include: {_comma_list(evidence_categories, 8)}.")
    return _join_lines(lines)


def _answer_procurement_examples(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    examples = data.get("experience") or []
    capabilities = data.get("capabilities") or []
    compliance_rules = data.get("compliance_rules") or []
    if not examples and not compliance_rules:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "surfaces procurement risks before the bid team drafts unsupported answers", message),
    ]
    if compliance_rules:
        lines.extend(["", *_bullet_block("Compliance checks currently modelled:", [f"{r.get('label', '')}: {r.get('description', '')}" for r in compliance_rules], 4)])
    if examples:
        lines.extend(["", *_bullet_block("Example analysis contexts:", [f"{e.get('title', '')} - {e.get('summary', '')}" for e in examples], 3)])
    if capabilities:
        lines.extend(["", *_bullet_block("Typical outputs:", capabilities, 5)])
    return _join_lines(lines)


def _answer_procurement_summary(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    workflows = data.get("workflows") or []
    capabilities = data.get("capabilities") or []
    lines = [
        _styled_intro(q_intent, style, "turns buyer requirements into structured requirements, risks, evidence needs, and actions", message),
        "",
        "For a tender summary, Bidworx separates the material into:",
        "- Mandatory compliance requirements",
        "- Scored buyer questions and implied evaluation themes",
        "- Evidence required to support each claim",
        "- Submission instructions and missing artefacts",
        "- Risks, blockers, and next actions",
    ]
    if workflows:
        lines.append(f"Relevant workflows: {_comma_list([w.get('name', '') for w in workflows], 3)}.")
    if capabilities:
        lines.extend(["", *_bullet_block("Available analysis outputs:", capabilities, 5)])
    return _join_lines(lines)


def _answer_technical_stack(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    stack = data.get("tech_stack") or {}
    if not stack:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "preserves the deterministic FastAPI and Next.js architecture", message),
        "",
        "The platform structure remains deliberately simple:",
    ]
    for label, items in stack.items():
        lines.append(f"- **{label.title()}:** {_comma_list(items)}")
    lines.extend([
        "",
        "The key architectural point is that the product brain is structured data, classifiers, retrievers, scoring rules, and answer templates. Any LLM layer should be optional polish, not the source of truth.",
    ])
    return _join_lines(lines)


def _answer_role_fit(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    scoring_rules = data.get("scoring_rules") or []
    capabilities = data.get("capabilities") or []
    key_systems = data.get("key_systems") or []
    if not scoring_rules and not capabilities:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "can score opportunity readiness when tender requirements and evidence records are available", message),
        "",
        "A deterministic opportunity score should consider:",
    ]
    for rule in scoring_rules:
        label = rule.get("label", "")
        weight = rule.get("weight", "")
        if label:
            lines.append(f"- **{label}:** weight {weight}")
    if capabilities:
        lines.extend(["", *_bullet_block("Evidence used to explain the score:", capabilities, 5)])
    if key_systems:
        lines.append(f"Relevant workflows: {_comma_list(key_systems, 4)}.")
    lines.append("")
    lines.append("If the evidence library cannot support a claim, Bidworx should lower confidence or flag the gap rather than fill it with generic bid language.")
    return _join_lines(lines)


def _answer_preferred_roles(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    roles = data.get("preferred_roles") or []
    buyer_roles = data.get("relevant_job_titles") or []
    lines = [
        _styled_intro(q_intent, style, "is designed for operational bid and procurement teams", message),
    ]
    if roles:
        lines.append(f"Primary users: {_comma_list(roles)}.")
    if buyer_roles:
        lines.append(f"Buyer-side roles it reasons about: {_comma_list(buyer_roles, 6)}.")
    return _join_lines(lines)


def _answer_availability(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    summary = data.get("availability_summary", "")
    cta = data.get("contact_cta", "")
    if not summary and not cta:
        return _INSUFFICIENT_EVIDENCE
    return _join_lines([
        _styled_intro(q_intent, style, "for tender triage, evidence mapping, and submission readiness checks", message),
        "",
        summary,
        cta,
    ])


def _answer_proof_points(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    proof_points = data.get("achievements") or []
    if not proof_points:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "uses proof points to keep bid claims grounded", message),
    ]
    for point in proof_points[:5]:
        title = point.get("title", "")
        description = point.get("description", "")
        if title:
            lines.extend(["", f"**{title}**", description])
    return _join_lines(lines)


def _answer_engagement(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    source = data.get("custom_services") or data.get("engagement_options") or []
    pricing_notes = data.get("pricing_notes", "")
    stack_highlight = data.get("stack_highlight", "")
    if not source:
        return _INSUFFICIENT_EVIDENCE
    lines = [
        _styled_intro(q_intent, style, "can be piloted around focused procurement intelligence workflows", message),
    ]
    if stack_highlight:
        lines.append(f"Delivery bias: {stack_highlight}.")
    lines.extend(["", "Practical starting points:"])
    for item in source[:4]:
        name = item.get("name") or item.get("type", "")
        description = item.get("description", "")
        if name:
            lines.append(f"- **{name}** - {description}")
    if pricing_notes:
        lines.extend(["", pricing_notes])
    return _join_lines(lines)


def _answer_contact(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    availability = data.get("availability", "")
    focus = data.get("focus", "")
    return _join_lines([
        "The best next step is to analyse a tender opportunity or capture the evidence library needed for one.",
        availability or focus,
    ])


def _answer_faq(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    faqs = data.get("faqs") or []
    if not faqs:
        return _INSUFFICIENT_EVIDENCE
    lines: list[str] = []
    for faq in faqs[:3]:
        question = faq.get("question", "")
        answer = faq.get("answer", "")
        if question and answer:
            lines.extend([f"**{question}**", answer, ""])
    return _join_lines(lines)


def _answer_engagement_preferences(
    data: dict[str, Any], message: str, q_intent: QuestionIntent, style: ResponseStyle
) -> str:
    work_type = data.get("work_type") or []
    full_time_preferences = data.get("full_time_preferences") or {}
    focus = data.get("focus", "")
    lines = [
        _styled_intro(q_intent, style, "fits teams that need procurement intelligence before drafting", message),
    ]
    if work_type:
        lines.append(f"Use cases: {_comma_list(work_type)}.")
    if full_time_preferences.get("ideal_roles"):
        lines.append(f"Teams and roles: {_comma_list(full_time_preferences.get('ideal_roles', []), 6)}.")
    if focus:
        lines.extend(["", focus])
    return _join_lines(lines)


_HANDLERS = {
    "profile_overview": _answer_profile_overview,
    "capabilities": _answer_capabilities,
    "strengths": _answer_strengths,
    "workflows": _answer_workflows,
    "workflows_overview": _answer_workflows_overview,
    "procurement_examples": _answer_procurement_examples,
    "procurement_summary": _answer_procurement_summary,
    "technical_stack": _answer_technical_stack,
    "role_fit": _answer_role_fit,
    "preferred_roles": _answer_preferred_roles,
    "availability": _answer_availability,
    "proof_points": _answer_proof_points,
    "engagement": _answer_engagement,
    "contact": _answer_contact,
    "faq": _answer_faq,
    "engagement_preferences": _answer_engagement_preferences,
}


def build_answer(
    intent: Intent,
    data: dict[str, Any],
    message: str = "",
    question_intent: QuestionIntent | None = None,
) -> str:
    if intent == "unknown":
        return _OUT_OF_SCOPE

    handler = _HANDLERS.get(intent)
    if handler is None:
        return _OUT_OF_SCOPE
    if not data:
        return _INSUFFICIENT_EVIDENCE

    q_intent = question_intent or QuestionIntent.GENERAL_PROFILE
    style = select_response_style(q_intent)
    return handler(data, message or "", q_intent, style)


def get_follow_ups(intent: Intent) -> list[str]:
    return FOLLOW_UPS.get(intent, [])

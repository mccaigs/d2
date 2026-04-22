"""Deterministic answer builder.

Answers are assembled from structured records only. No LLM and no raw JSON
dumping. The response-style selector still controls how first sentences are
framed so the pipeline remains:

classifier -> retriever -> answer_builder -> response_style
"""

import re
from typing import Any

from app.services.classifier import Intent
from app.services.question_intent import QuestionIntent
from app.services.response_style import ResponseStyle, select_response_style


FOLLOW_UPS: dict[Intent, list[str]] = {
    "skills": [
        "What production AI systems has David built?",
        "What tech stack does David use?",
        "What roles is David open to?",
    ],
    "technical_stack": [
        "What has David built with that stack?",
        "What does David do?",
        "What kinds of engagements is David open to?",
    ],
    "projects": [
        "What tech stack does David use?",
        "What is David strongest at technically?",
        "Can David help with a short MVP build?",
    ],
    "projects_overview": [
        "What tech stack does David use?",
        "What experience does David bring to those builds?",
        "What kinds of work is David open to?",
    ],
    "experience": [
        "What has David built?",
        "What is David strongest at technically?",
        "What roles is David best suited for?",
    ],
    "experience_summary": [
        "What has David built recently?",
        "What tech stack does David use?",
        "What roles is David open to?",
    ],
    "strengths": [
        "What production AI systems has David built?",
        "What tech stack does David use?",
        "Can David be hired for a short project?",
    ],
    "role_fit": [
        "What is David strongest at technically?",
        "What has David built?",
        "How do I contact David?",
    ],
    "preferred_roles": [
        "What does David do?",
        "What has David built?",
        "How do I contact David?",
    ],
    "availability": [
        "What roles is David open to?",
        "Can David help with a short project?",
        "How do I contact David?",
    ],
    "achievements": [
        "What has David built?",
        "What tech stack does David use?",
        "What roles is David open to?",
    ],
    "engagement": [
        "What are David's day rates?",
        "What kinds of work is David open to?",
        "How do I contact David?",
    ],
    "contact": [
        "What does David do?",
        "What has David built?",
        "What tech stack does David use?",
    ],
    "faq": [
        "What has David built?",
        "What is David strongest at technically?",
        "How do I contact David?",
    ],
    "profile_overview": [
        "What tech stack does David use?",
        "What has David built?",
        "What roles is David open to?",
    ],
    "capabilities": [
        "What has David built with those capabilities?",
        "What tech stack supports that work?",
        "What engagements is David open to?",
    ],
    "engagement_preferences": [
        "What does David do?",
        "What has David built?",
        "How do I contact David?",
    ],
    "unknown": [],
}


_OUT_OF_SCOPE = (
    "I can only answer questions about David Robertson's professional background, "
    "including his work, projects, technical stack, experience, and engagement preferences."
)

_INSUFFICIENT_EVIDENCE = (
    "I do not have enough published profile data to answer that cleanly, so I would rather stay grounded in what is on record."
)


_CONTEXT_PATTERNS: list[tuple[str, str]] = [
    (r"solutions?\s+architect", "solutions architecture"),
    (r"applied\s+ai", "applied AI"),
    (r"ai\s+engineer", "AI engineering"),
    (r"next\.?js", "Next.js delivery"),
    (r"python", "Python delivery"),
    (r"mvp", "MVP builds"),
    (r"recruit", "recruitment products"),
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


def _stack_groups(stack: dict[str, Any]) -> dict[str, list[str]]:
    languages = stack.get("languages", [])
    frameworks = stack.get("frameworks", [])
    backend = stack.get("backend", [])
    frontend = stack.get("frontend", [])
    ai_tools = stack.get("ai_tools", [])
    infrastructure = stack.get("infrastructure", [])
    other = stack.get("other", [])
    return {
        "Backend": _dedupe(languages[:1] + backend + frameworks),
        "Frontend": _dedupe(frontend + ["TypeScript"]),
        "AI": _dedupe(ai_tools),
        "Infrastructure": _dedupe(infrastructure + other),
    }


def _styled_intro(
    q_intent: QuestionIntent,
    style: ResponseStyle,
    detail: str,
    message: str = "",
) -> str:
    detail_text = detail
    if " is {detail}" in style.opening_pattern and detail_text.startswith("is "):
        detail_text = detail_text[3:]
    if " strongest at {detail}" in style.opening_pattern and detail_text.startswith("is strongest at "):
        detail_text = detail_text[len("is strongest at ") :]
    if " has built {detail}" in style.opening_pattern and detail_text.startswith("has built "):
        detail_text = detail_text[len("has built ") :]
    if " works best {detail}" in style.opening_pattern and detail_text.startswith("works best "):
        detail_text = detail_text[len("works best ") :]
    if " is available {detail}" in style.opening_pattern and detail_text.startswith("is available "):
        detail_text = detail_text[len("is available ") :]
    base = style.opening_pattern.format(subject="David", detail=detail_text).strip()
    if not base.endswith("."):
        base = f"{base}."
    context = _query_context(message)
    if context and context not in base.lower():
        base = base[:-1] + f", particularly for {context}."
    return base


def _answer_profile_overview(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    title = _pipe_title(data.get("title", "AI architect and systems engineer"))
    location = data.get("location", "")
    profile = data.get("profile", "")
    capabilities = data.get("capabilities") or []
    core_skills = data.get("core_skills") or []
    ideal_roles = data.get("ideal_roles") or []
    focus = data.get("focus", "")

    if not title and not profile:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, f"is {_pipe_title(title)}", message)
        if title
        else _styled_intro(q_intent, style, "works across applied AI and product delivery", message)
    ]

    if location:
        lines.append(f"Based in {location}.")
    if profile:
        lines.extend(["", profile])
    if capabilities:
        lines.append(f"Key capabilities: {_comma_list(capabilities, 4)}.")
    if core_skills:
        lines.append(f"Core delivery areas: {_comma_list(core_skills, 4)}.")
    if ideal_roles:
        lines.append(f"Best-fit roles: {_comma_list(ideal_roles, 4)}.")
    if focus:
        lines.extend(["", focus])
    return _join_lines(lines)


def _answer_capabilities(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    capabilities = data.get("capabilities") or []
    core_skills = data.get("core_skills") or []
    key_systems = data.get("key_systems") or []

    if not capabilities and not core_skills:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "works across AI systems, workflow automation, and product delivery", message),
        "",
        *_bullet_block("Core capabilities:", capabilities, 6),
        "",
        *_bullet_block("Execution strengths:", core_skills, 5),
    ]
    if key_systems:
        lines.extend(["", *_bullet_block("Representative systems:", key_systems, 4)])
    lines.extend([
        "",
        "Those capabilities are demonstrated in shipped products — InterviewsAI, the AI Jobs Pipeline, CareersAI, and RecruitersAI — not just described in a CV.",
        "",
        "That combination suits architecture-led AI work, deterministic systems, and rapid product builds where delivery quality matters as much as speed.",
    ])
    return _join_lines(lines)


def _answer_skills(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    technical_skills = data.get("technical_skills") or []
    working_style = data.get("working_style") or []
    if not technical_skills:
        return _INSUFFICIENT_EVIDENCE

    by_category: dict[str, list[str]] = {}
    for skill in technical_skills:
        category = (skill.get("category") or "Other").title()
        by_category.setdefault(category, []).append(skill.get("name", ""))

    lines = [
        _styled_intro(q_intent, style, "works across applied AI, Python backends, and product-facing frontend delivery", message),
        "",
        "Broadly, the skill set breaks down like this:",
    ]
    for category, names in by_category.items():
        grouped = _comma_list(names)
        if grouped:
            lines.append(f"- **{category}:** {grouped}")

    if working_style:
        lines.extend(["", *_bullet_block("How he tends to work:", working_style, 4)])

    lines.extend([
        "",
        "The positioning is consistent: a hands-on senior builder who can move from architecture through to shipped implementation.",
    ])
    return _join_lines(lines)


def _answer_strengths(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    strengths = data.get("core_strengths") or []
    working_style = data.get("working_style") or []
    if not strengths:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "applied AI, backend engineering, and product delivery", message),
        "",
        *_bullet_block("The strongest themes are:", strengths, 6),
    ]
    if working_style:
        lines.extend(["", *_bullet_block("That usually shows up as:", working_style, 3)])
    lines.extend([
        "",
        "That is backed by concrete systems: InterviewsAI (AI-driven evaluation with scoring and adaptive questioning), the AI Jobs Pipeline (automated sourcing and deterministic fit scoring), and CareersAI / RecruitersAI (end-to-end recruitment AI platforms).",
        "",
        "That is why he fits senior IC, architecture, and founding-style product roles particularly well.",
    ])
    return _join_lines(lines)


def _answer_projects(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    projects = data.get("projects") or []
    if not projects:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "has shipped product-led systems rather than isolated prototypes", message),
    ]
    for project in projects[:3]:
        name = project.get("name", "")
        project_type = project.get("type", "")
        summary = project.get("summary", "")
        tech = project.get("tech") or []
        if not name:
            continue
        lines.extend(["", f"**{name}**" + (f" - {project_type}" if project_type else "")])
        if summary:
            lines.append(summary)
        if tech:
            lines.append(f"Stack: {_comma_list(tech)}.")
    lines.extend([
        "",
        "The pattern across those builds is clear: strong product framing, credible technical delivery, and systems designed to be used in production.",
    ])
    return _join_lines(lines)


def _answer_projects_overview(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    projects = data.get("projects") or []
    key_systems = data.get("key_systems") or []
    products = data.get("products") or []
    if not projects and not key_systems:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "has built production AI systems around automation, scoring, and workflow execution", message),
    ]

    for project in projects[:4]:
        name = project.get("name", "")
        description = project.get("description", "")
        features = project.get("features") or []
        if not name:
            continue
        lines.extend(["", f"**{name}**"])
        if description:
            lines.append(description)
        if features:
            lines.append(f"Key detail: {_comma_list(features, 3)}.")

    if key_systems:
        lines.extend(["", *_bullet_block("Other named systems include:", key_systems, 4)])
    if products:
        lines.append(f"Current product portfolio: {_comma_list(products, 4)}.")

    lines.extend([
        "",
        "This is not vague CV language. The work is concrete: matching, scoring, orchestration, ingestion, and AI-assisted product workflows.",
    ])
    return _join_lines(lines)


def _answer_experience(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    experience = data.get("experience") or []
    capabilities = data.get("capabilities") or []
    industries = data.get("industries") or []
    if not experience and not capabilities:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "brings a mix of applied AI, SaaS, and delivery experience", message),
    ]
    if experience:
        lines.extend(["", *_bullet_block("A quick overview:", [
            f"{item.get('title', '')} - {item.get('summary', '')}".strip(" -")
            for item in experience[:3]
        ], 3)])
    if capabilities:
        lines.extend(["", *_bullet_block("Typical responsibilities:", capabilities, 5)])
    if industries:
        lines.append(f"That work spans { _comma_list(industries) }.")
    lines.extend([
        "",
        "The positioning is senior hands-on delivery rather than pure management.",
    ])
    return _join_lines(lines)


def _answer_experience_summary(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    experience = data.get("experience") or []
    capabilities = data.get("capabilities") or []
    if not experience:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "brings recent AI product work on top of earlier founder, web, and operations experience", message),
    ]
    for role in experience[:4]:
        role_name = role.get("role", "")
        company = role.get("company", "")
        dates = role.get("dates", "")
        summary = role.get("summary", "")
        label = " - ".join(part for part in [role_name, company, dates] if part)
        if not label:
            continue
        lines.extend(["", f"**{label}**"])
        if summary:
            lines.append(summary)

    if capabilities:
        lines.extend(["", *_bullet_block("Consistent themes across that work:", capabilities, 5)])

    lines.extend([
        "",
        "That blend gives him both builder speed and commercial judgement, which is useful in senior AI engineering and architecture roles.",
    ])
    return _join_lines(lines)


def _answer_technical_stack(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    stack = data.get("tech_stack") or {}
    core_skills = data.get("core_skills") or []
    if not stack:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "works across Python services, Next.js products, and supporting AI tooling", message),
        "",
        "Grouped simply, the stack looks like this:",
    ]
    for label, items in _stack_groups(stack).items():
        grouped = _comma_list(items)
        if grouped:
            lines.append(f"- **{label}:** {grouped}")

    if core_skills:
        lines.append(f"Core technical emphasis: {_comma_list(core_skills, 4)}.")

    lines.extend([
        "",
        "In practice that means Python APIs and automation on the backend, Next.js and TypeScript on the frontend, major LLM providers for AI features, and lightweight infrastructure that keeps delivery fast without losing production discipline.",
    ])
    return _join_lines(lines)


def _answer_role_fit(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    positioning = data.get("positioning") or []
    preferred_roles = data.get("preferred_roles") or []
    relevant_titles = data.get("relevant_job_titles") or []
    capabilities = data.get("capabilities") or []
    key_systems = data.get("key_systems") or []
    projects = data.get("projects") or []
    engagement_focus = data.get("engagement_focus", "")
    if not positioning and not preferred_roles and not relevant_titles:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "is a strong fit where AI delivery, systems thinking, and product ownership overlap", message),
    ]
    if relevant_titles:
        lines.append(f"Closest title matches: {_comma_list(relevant_titles, 6)}.")
    if preferred_roles:
        lines.append(f"Roles he actively aligns with: {_comma_list(preferred_roles, 5)}.")
    if capabilities:
        lines.extend(["", *_bullet_block("Why the fit is credible:", capabilities, 4)])

    # Evidence-backed project references
    if projects:
        project_names = [p.get("name", "") for p in projects[:3] if p.get("name")]
        if project_names:
            lines.extend(["", f"That positioning is backed by shipped systems: {_comma_list(project_names)}."])
    if key_systems:
        lines.extend(["", *_bullet_block("Representative systems he has built:", key_systems, 3)])

    if positioning:
        lines.append(f"Overall positioning: {_comma_list(positioning, 4)}.")
    if engagement_focus:
        lines.extend(["", engagement_focus])
    return _join_lines(lines)


def _answer_preferred_roles(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    preferred_roles = data.get("preferred_roles") or []
    relevant_titles = data.get("relevant_job_titles") or []
    availability_summary = data.get("availability_summary", "")
    if not preferred_roles and not relevant_titles:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "is targeting senior AI and product-facing engineering roles", message),
    ]
    if preferred_roles:
        lines.append(f"Preferred role shapes: {_comma_list(preferred_roles)}.")
    if relevant_titles:
        lines.append(f"Concrete title matches: {_comma_list(relevant_titles, 6)}.")
    if availability_summary:
        lines.extend(["", availability_summary])
    return _join_lines(lines)


def _answer_availability(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    summary = data.get("availability_summary", "")
    cta = data.get("contact_cta", "")
    if not summary and not cta:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "is available for senior roles and focused delivery work", message),
    ]
    if summary:
        lines.extend(["", summary])
    if cta:
        lines.extend(["", cta])
    return _join_lines(lines)


def _answer_achievements(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    achievements = data.get("achievements") or []
    if not achievements:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "has a record of recognised startup and product work", message),
    ]
    for achievement in achievements[:5]:
        title = achievement.get("title", "")
        organisation = achievement.get("organisation", "")
        description = achievement.get("description", "")
        year = achievement.get("date") or achievement.get("year")
        label = " - ".join(str(part) for part in [title, organisation, year] if part)
        if not label:
            continue
        lines.extend(["", f"**{label}**"])
        if description:
            lines.append(description)
    return _join_lines(lines)


def _answer_engagement(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    custom_services = data.get("custom_services") or []
    engagement_options = data.get("engagement_options") or []
    pricing_notes = data.get("pricing_notes", "")
    stack_highlight = data.get("stack_highlight", "")
    availability_summary = data.get("availability_summary", "")
    source = custom_services or engagement_options
    if not source:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "takes on focused builds, AI system design, and senior advisory work", message),
    ]
    if stack_highlight:
        lines.append(f"Delivery bias: {stack_highlight}.")
    lines.extend(["", "The main engagement shapes are:"])
    for item in source[:4]:
        name = item.get("name") or item.get("type", "")
        description = item.get("description", "")
        pricing = item.get("pricing", "")
        if not name:
            continue
        line = f"- **{name}** - {description}"
        if pricing:
            line += f" ({pricing})"
        lines.append(line)
    if pricing_notes:
        lines.extend(["", pricing_notes])
    if availability_summary:
        lines.extend(["", availability_summary])
    return _join_lines(lines)


def _answer_contact(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    availability = data.get("availability", "")
    focus = data.get("focus", "")

    lines = [
        "The best way to get in touch is through David's contact page.",
        "Share a short note on the role or project and he can follow up directly.",
    ]
    if availability:
        lines.append(availability)
    elif focus:
        lines.append(focus)
    return _join_lines(lines)


def _answer_faq(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    faqs = data.get("faqs") or []
    if not faqs:
        return _INSUFFICIENT_EVIDENCE

    lines: list[str] = []
    for faq in faqs[:3]:
        question = faq.get("question", "")
        answer = faq.get("answer", "")
        if not question or not answer:
            continue
        lines.extend([f"**{question}**", answer, ""])
    return _join_lines(lines)


def _answer_engagement_preferences(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent,
    style: ResponseStyle,
) -> str:
    work_type = data.get("work_type") or []
    location = data.get("location") or []
    rates = data.get("rates") or {}
    full_time_preferences = data.get("full_time_preferences") or {}
    focus = data.get("focus", "")
    availability_summary = data.get("availability_summary", "")

    if not work_type and not rates and not full_time_preferences:
        return _INSUFFICIENT_EVIDENCE

    lines = [
        _styled_intro(q_intent, style, "is open to both permanent roles and focused delivery engagements", message),
    ]
    if work_type:
        lines.append(f"Work types: {_comma_list(work_type)}.")
    if location:
        lines.append(f"Location preference: {_comma_list(location)}.")
    if rates:
        rate_bits = []
        if rates.get("day_rate"):
            rate_bits.append(f"day rate {rates['day_rate']}")
        if rates.get("mvp_projects"):
            rate_bits.append(f"MVP projects {rates['mvp_projects']}")
        if rates.get("full_time_salary"):
            rate_bits.append(f"full-time salary from {rates['full_time_salary']}")
        if rate_bits:
            lines.append(f"Commercial guide: {', '.join(rate_bits)}.")
    if full_time_preferences.get("ideal_roles"):
        lines.append(
            f"Ideal full-time roles: {_comma_list(full_time_preferences.get('ideal_roles', []), 4)}."
        )
    if full_time_preferences.get("flexibility"):
        lines.append(full_time_preferences["flexibility"])
    if focus:
        lines.extend(["", focus])
    if availability_summary:
        lines.append(availability_summary)
    return _join_lines(lines)


_HANDLERS = {
    "profile_overview": _answer_profile_overview,
    "capabilities": _answer_capabilities,
    "skills": _answer_skills,
    "strengths": _answer_strengths,
    "projects": _answer_projects,
    "projects_overview": _answer_projects_overview,
    "experience": _answer_experience,
    "experience_summary": _answer_experience_summary,
    "technical_stack": _answer_technical_stack,
    "role_fit": _answer_role_fit,
    "preferred_roles": _answer_preferred_roles,
    "availability": _answer_availability,
    "achievements": _answer_achievements,
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

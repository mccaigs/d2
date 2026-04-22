"""Deterministic answer builder.

Every answer follows a recruiter-facing shape:
    1. Direct, context-aware opening (matched to question shape)
    2. Supporting proof (including named project evidence where relevant)
    3. Closing positioning line

No LLM. All copy is templated from structured data loaded by the retriever.
The opening line is selected centrally via QuestionIntent + ResponseStyle,
not hardcoded per handler.
"""

import re
from typing import Any

from app.services.classifier import Intent
from app.services.question_intent import QuestionIntent
from app.services.response_style import ResponseStyle, select_response_style


FOLLOW_UPS: dict[Intent, list[str]] = {
    "skills": [
        "What production AI systems has David built?",
        "What kinds of AI roles is David best suited for?",
        "How does David combine Python and Next.js in production?",
    ],
    "technical_stack": [
        "What projects has David built with this stack?",
        "What kinds of AI roles is David best suited for?",
        "Can David be hired for a short project?",
    ],
    "projects": [
        "What technical stack does David use?",
        "What is David strongest at technically?",
        "Can David be hired for a short MVP build?",
    ],
    "experience": [
        "What projects has David built?",
        "What is David strongest at technically?",
        "What kinds of AI roles is David best suited for?",
    ],
    "strengths": [
        "What production AI systems has David built?",
        "What kinds of AI roles is David best suited for?",
        "Can David be hired for a short project?",
    ],
    "role_fit": [
        "What is David strongest at technically?",
        "What production AI systems has David built?",
        "Is David available for short projects or contract work?",
    ],
    "preferred_roles": [
        "What is David strongest at technically?",
        "What production AI systems has David built?",
        "Is David available for new roles?",
    ],
    "availability": [
        "Can David be hired for a short project?",
        "What kinds of AI roles is David best suited for?",
        "What is David strongest at technically?",
    ],
    "achievements": [
        "What production AI systems has David built?",
        "What is David strongest at technically?",
        "What kinds of AI roles is David best suited for?",
    ],
    "engagement": [
        "What are David's day rates?",
        "How do I contact David?",
        "What production AI systems has David built?",
    ],
    "contact": [
        "What production AI systems has David built?",
        "What is David's technical stack?",
        "Can David help us build an MVP?",
    ],
    "faq": [
        "What production AI systems has David built?",
        "What is David strongest at technically?",
        "Can David be hired for a short project?",
    ],
    "unknown": [],
}


# ---------------------------------------------------------------------------
# Refusal messages
# ---------------------------------------------------------------------------

_OUT_OF_SCOPE = (
    "I can only answer questions about David Robertson's professional background — "
    "his skills, projects, experience, achievements, engagement options, and role "
    "suitability.\n\n"
    "Try asking something like *\"What production AI systems has David built?\"*, "
    "*\"Would David suit a solutions architect role?\"*, or "
    "*\"Can David be hired for a short project?\"*."
)

_INSUFFICIENT_EVIDENCE = (
    "I don't have enough published profile data to answer that confidently. "
    "Rather than speculate, I'd rather stay grounded in what's on record.\n\n"
    "You can ask about David's skills, projects, experience, achievements, "
    "technical stack, engagement options, or role suitability — those areas "
    "are fully covered."
)


# ---------------------------------------------------------------------------
# Query context extraction — lightweight, deterministic
# ---------------------------------------------------------------------------

_CONTEXT_PATTERNS: list[tuple[str, str]] = [
    # (regex, phrase to surface in the opening clause)
    (r"\bsolutions?\s+architect\b", "solutions architecture"),
    (r"\bapplied\s+ai\b", "applied AI work"),
    (r"\bai\s+engineer(?:ing)?\b", "AI engineering"),
    (r"\bai\s+product\b", "AI product work"),
    (r"\bfounding\s+engineer\b", "founding engineer seats"),
    (r"\brecruit(?:er|ment|ing)\s+tool", "recruiter-facing tools"),
    (r"\brecruit(?:er|ment|ing)\b", "recruitment-domain work"),
    (r"\bfull[-\s]?stack\b", "full-stack delivery"),
    (r"\bpython\b.*\bnext\.?js\b|\bnext\.?js\b.*\bpython\b", "Python and Next.js builds"),
    (r"\bpython\b", "Python backend work"),
    (r"\bnext\.?js\b", "Next.js product builds"),
    (r"\bfastapi\b", "FastAPI backends"),
    (r"\bmvp\b", "MVP builds"),
    (r"\bshort\s+project|short[-\s]term|freelance|contract|consulting", "short-term engagements"),
    (r"\barchitecture|architect\b", "architecture work"),
    (r"\bllm|agentic|agent\b", "LLM and agentic systems"),
]


def _query_context(message: str) -> str | None:
    """Return a short noun phrase describing the query context, if we can
    detect one. Used to personalise the opening sentence."""
    if not message:
        return None
    lowered = message.lower()
    for pattern, phrase in _CONTEXT_PATTERNS:
        if re.search(pattern, lowered):
            return phrase
    return None


# ---------------------------------------------------------------------------
# Project evidence — deterministic, name-checked.
# Used to force 1–2 named project references into relevant intents.
# ---------------------------------------------------------------------------

_PROJECT_EVIDENCE: dict[str, str] = {
    "CareersAI": "scoring and matching systems",
    "RecruitersAI": "recruiter-facing intelligence",
    "InterviewsAI": "Python evaluation pipelines on FastAPI + Next.js",
    "UK AI Jobs Pipeline": "AI-assisted automation and scoring",
    "AI IDE Initiative": "AI developer tooling architecture",
}

# Per-keyword hints about which projects to surface first. Falls back to the
# ordered list if no match is found.
_PROJECT_HINTS: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (("recruit", "hiring", "candidate", "talent", "recruiter tool"),
     ("CareersAI", "RecruitersAI")),
    (("interview", "assessment", "evaluation"),
     ("InterviewsAI", "CareersAI")),
    (("python", "fastapi", "backend"),
     ("InterviewsAI", "UK AI Jobs Pipeline")),
    (("next.js", "nextjs", "frontend", "typescript"),
     ("CareersAI", "InterviewsAI")),
    (("automation", "pipeline", "workflow", "scoring"),
     ("UK AI Jobs Pipeline", "InterviewsAI")),
    (("developer", "ide", "tooling", "devtools", "mcp"),
     ("AI IDE Initiative", "InterviewsAI")),
    (("ai product", "applied ai", "llm", "agent", "agentic"),
     ("InterviewsAI", "CareersAI")),
]

_DEFAULT_PROJECT_ORDER: tuple[str, ...] = (
    "InterviewsAI", "CareersAI", "RecruitersAI",
    "UK AI Jobs Pipeline", "AI IDE Initiative",
)


def _pick_projects(message: str, available: list[dict] | None = None) -> list[str]:
    """Return up to two project names most relevant to the query, intersected
    with any retrieved project list so we never reference a project that isn't
    in the data."""
    available_names: set[str] | None = None
    if available:
        available_names = {p.get("name", "") for p in available if p.get("name")}

    lowered = (message or "").lower()
    ordered: list[str] = []
    for keywords, names in _PROJECT_HINTS:
        if any(kw in lowered for kw in keywords):
            for n in names:
                if n not in ordered:
                    ordered.append(n)
    for n in _DEFAULT_PROJECT_ORDER:
        if n not in ordered:
            ordered.append(n)

    if available_names is not None:
        ordered = [n for n in ordered if n in available_names]

    return ordered[:2]


def _project_evidence_line(message: str, available: list[dict] | None = None) -> str | None:
    names = _pick_projects(message, available)
    if not names:
        return None
    if len(names) == 1:
        n = names[0]
        return f"The clearest example is **{n}** ({_PROJECT_EVIDENCE[n]})."
    a, b = names[0], names[1]
    return (
        f"The clearest examples are **{a}** ({_PROJECT_EVIDENCE[a]}) and "
        f"**{b}** ({_PROJECT_EVIDENCE[b]})."
    )


# ---------------------------------------------------------------------------
# Opening helpers
# ---------------------------------------------------------------------------

def _opening(base: str, ctx: str | None, tail: str | None = None) -> str:
    """Glue a context clause into the opener if one is available."""
    if ctx:
        return f"{base}, particularly for {ctx}." if not tail else f"{base}, particularly for {ctx}. {tail}"
    return f"{base}. {tail}" if tail else f"{base}."


# --------------------------------------------------------------------- #
# Centralised opening-line composition
# --------------------------------------------------------------------- #

# Per-QuestionIntent, the detail clause that fills the {detail} slot in
# the ResponseStyle.opening_pattern. Each maps to a short, natural
# continuation that reads well after the pattern prefix.
_OPENING_DETAILS: dict[QuestionIntent, str] = {
    QuestionIntent.CAPABILITY: (
        "works across applied AI, Python backend systems, and "
        "Next.js product builds"
    ),
    QuestionIntent.FIT_YES_NO: (
        "is a strong fit here"
    ),
    QuestionIntent.STRENGTHS: (
        "applied AI, Python backend engineering, and Next.js product delivery "
        "— the areas where those intersect"
    ),
    QuestionIntent.EXPERIENCE: (
        "a run of applied AI and SaaS products, from end to end"
    ),
    QuestionIntent.IDENTITY_SUMMARY: (
        "a senior AI engineer and systems builder who works across applied AI, "
        "Python backends, and Next.js product delivery"
    ),
    QuestionIntent.WORKING_STYLE: (
        "with clear ownership, architectural input, and a bias toward shipping"
    ),
    QuestionIntent.AVAILABILITY_COMMERCIAL: (
        "for both senior roles and short, focused engagements"
    ),
    QuestionIntent.GENERAL_PROFILE: (
        "works at the intersection of applied AI, architecture, and "
        "Python + Next.js product engineering"
    ),
}


def _compose_opening(
    q_intent: QuestionIntent,
    style: ResponseStyle,
    ctx: str | None = None,
) -> str:
    """Build the first sentence of the answer from the classified question
    shape and the selected response style.

    This is the single place that decides how an answer begins.
    """
    detail = _OPENING_DETAILS.get(q_intent, _OPENING_DETAILS[QuestionIntent.GENERAL_PROFILE])
    base = style.opening_pattern.format(subject="David", detail=detail)

    if ctx:
        # Weave the topic-context phrase in naturally.
        if base.endswith("."):
            base = base[:-1]
        return f"{base}, particularly for {ctx}."
    if not base.endswith("."):
        return f"{base}."
    return base


def _join_lines(parts: list[str]) -> str:
    return "\n".join(p for p in parts if p is not None).strip()


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def _answer_skills(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    skills = data.get("technical_skills") or []
    working_style = data.get("working_style") or []
    if not skills:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    by_category: dict[str, list[str]] = {}
    for s in skills:
        cat = (s.get("category") or "other").title()
        by_category.setdefault(cat, []).append(s.get("name", ""))

    rs = style or select_response_style(q_intent)
    lines: list[str] = [_compose_opening(q_intent, rs, ctx), ""]
    lines.append("Across the stack, that breaks down roughly like this:")
    for cat, names in by_category.items():
        cleaned = ", ".join(n for n in names if n)
        if cleaned:
            lines.append(f"— **{cat}:** {cleaned}")

    if working_style:
        lines.append("")
        lines.append("In practice he tends to:")
        for item in working_style[:4]:
            lines.append(f"— {item}")

    evidence = _project_evidence_line(message)
    if evidence:
        lines.append("")
        lines.append(evidence)

    lines.append("")
    lines.append(
        "That combination — Python + FastAPI on the backend, Next.js + "
        "TypeScript on the frontend — is the stack he delivers with in "
        "production, and it's what makes him effective in senior AI "
        "engineering and architecture roles."
    )
    return _join_lines(lines)


def _answer_strengths(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    strengths = data.get("core_strengths") or []
    working_style = data.get("working_style") or []
    if not strengths:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    rs = style or select_response_style(q_intent)
    lines = [_compose_opening(q_intent, rs, ctx), "", "The strengths that come up again and again:"]
    for s in strengths[:6]:
        lines.append(f"— {s}")

    if working_style:
        lines.append("")
        lines.append("How that tends to show up day to day:")
        for item in working_style[:3]:
            lines.append(f"— {item}")

    evidence = _project_evidence_line(message)
    if evidence:
        lines.append("")
        lines.append(evidence)

    lines.append("")
    lines.append(
        "Net-net: these strengths map directly onto senior AI engineer, "
        "solutions architect, and applied AI roles — and onto short MVP "
        "builds where Python + Next.js delivery speed matters."
    )
    return _join_lines(lines)


def _answer_projects(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    projects = data.get("projects") or []
    if not projects:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    primary = projects[0]
    supporting = projects[1:3]

    # Name-driven opener so the first sentence has concrete evidence.
    picked = _pick_projects(message, projects)
    lead_names = ", ".join(f"**{n}**" for n in picked) if picked else f"**{primary.get('name', '')}**"
    rs = style or select_response_style(q_intent)
    opener = _compose_opening(q_intent, rs, ctx)
    # Append concrete project names as a tail clause.
    tail = f"The clearest example{'s' if len(picked) > 1 else ''} here: {lead_names}."
    if opener.endswith("."):
        opener = f"{opener} {tail}"
    else:
        opener = f"{opener}. {tail}"

    lines = [opener, ""]

    lines.append(f"**{primary.get('name', '')}** — {primary.get('type', '')}")
    lines.append(primary.get("summary", ""))
    if primary.get("highlights"):
        lines.append(f"— {primary['highlights'][0]}")
    tech = ", ".join(primary.get("tech", []))
    if tech:
        lines.append(f"*Stack: {tech}*")

    if supporting:
        lines.append("")
        lines.append("Alongside that, a couple more worth knowing about:")
        for p in supporting:
            name = p.get("name", "")
            summary = p.get("summary", "")
            lines.append(f"— **{name}** — {summary}")

    lines.append("")
    lines.append(
        "For hiring: the pattern is consistent — Python + Next.js delivery, "
        "architecture-led thinking, and systems that actually ship. That is "
        "the same delivery posture he brings to short builds and MVP work."
    )
    return _join_lines(lines)


def _answer_experience(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    roles = data.get("experience") or []
    caps = data.get("capabilities") or []
    industries = data.get("industries") or []

    if not roles and not caps:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    rs = style or select_response_style(q_intent)
    lines = [_compose_opening(q_intent, rs, ctx), ""]

    if roles:
        lines.append("A quick sketch of where he sits today:")
        for r in roles[:3]:
            title = r.get("title", "")
            summary = r.get("summary", "")
            lines.append(f"— **{title}** — {summary}")

    if caps:
        lines.append("")
        lines.append("Day to day, the work looks like:")
        for c in caps[:5]:
            lines.append(f"— {c}")

    if industries:
        lines.append("")
        lines.append(f"He has done this across {', '.join(industries)}.")

    lines.append("")
    lines.append(
        "In practice: this background suits senior IC, architect, and "
        "founding-engineer roles — and short, focused engagements where "
        "technical ownership and shipping speed matter."
    )
    return _join_lines(lines)


def _answer_technical_stack(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    skills = data.get("technical_skills") or []
    if not skills:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    by_category: dict[str, list[str]] = {}
    for s in skills:
        cat = (s.get("category") or "other").title()
        by_category.setdefault(cat, []).append(s.get("name", ""))

    rs = style or select_response_style(q_intent)
    lines = [_compose_opening(q_intent, rs, ctx), "", "Breaking that down by area:"]
    for cat, names in by_category.items():
        cleaned = ", ".join(n for n in names if n)
        if cleaned:
            lines.append(f"— **{cat}:** {cleaned}")

    lines.append("")
    lines.append(
        "How it fits together in practice: typed FastAPI services handle the "
        "deterministic backend work, Next.js App Router drives streaming UX "
        "and product surfaces, and Convex, Clerk, and Stripe slot in for "
        "realtime data, auth, and billing when a product needs them."
    )

    evidence = _project_evidence_line(message)
    if evidence:
        lines.append("")
        lines.append(evidence)

    lines.append("")
    lines.append(
        "It is a production-ready stack chosen for speed of delivery and "
        "maintainability — the same stack he uses for short MVP builds and "
        "applied AI work."
    )
    return _join_lines(lines)


def _answer_role_fit(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    positioning = data.get("positioning") or []
    preferred = data.get("preferred_roles") or []
    titles = data.get("relevant_job_titles") or []
    caps = data.get("capabilities") or []

    if not positioning and not preferred and not titles:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message) or "applied AI and full-stack delivery"
    rs = style or select_response_style(q_intent)
    opener = _compose_opening(q_intent, rs, ctx)

    lines = [opener, ""]

    if titles:
        lines.append("Titles that map to him directly:")
        for t in titles[:6]:
            lines.append(f"— {t}")

    if preferred:
        lines.append("")
        lines.append("The role shapes he actively goes after:")
        for r in preferred[:5]:
            lines.append(f"— {r}")

    if caps:
        lines.append("")
        lines.append("Why he fits:")
        for c in caps[:4]:
            lines.append(f"— {c}")

    evidence = _project_evidence_line(message)
    if evidence:
        lines.append("")
        lines.append(evidence)

    lines.append("")
    lines.append(
        "For hiring: he works best with clear ownership, architectural "
        "input, and a bias toward shipping — senior IC, founding engineer, "
        "or architect seats rather than pure management tracks."
    )
    return _join_lines(lines)


def _answer_preferred_roles(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    preferred = data.get("preferred_roles") or []
    titles = data.get("relevant_job_titles") or []
    availability = data.get("availability_summary") or ""

    if not preferred and not titles:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    rs = style or select_response_style(q_intent)
    lines = [_compose_opening(q_intent, rs, ctx), ""]
    if preferred:
        lines.append("The role shapes he's actively after:")
        for r in preferred:
            lines.append(f"— {r}")
    if titles:
        lines.append("")
        lines.append(f"Titles that fit cleanly: {', '.join(titles[:6])}.")
    if availability:
        lines.append("")
        lines.append(availability)
    lines.append("")
    lines.append(
        "Worth noting: he is also open to short projects and MVP builds "
        "alongside full-time conversations."
    )
    return _join_lines(lines)


def _answer_availability(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    summary = data.get("availability_summary") or ""
    cta = data.get("contact_cta") or ""
    if not summary and not cta:
        return _INSUFFICIENT_EVIDENCE

    rs = style or select_response_style(q_intent)
    opener = _compose_opening(q_intent, rs)
    lines = [opener + "\n"]
    if summary:
        lines.append(summary)
    lines.append("")
    lines.append(
        "On the short-project side, that usually means 1–5 day builds, MVP "
        "delivery on Python + Next.js, or applied AI system design."
    )
    if cta:
        lines.append("")
        lines.append(cta)
    return _join_lines(lines)


def _answer_achievements(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    achievements = data.get("achievements") or []
    if not achievements:
        return _INSUFFICIENT_EVIDENCE

    ctx = _query_context(message)
    rs = style or select_response_style(q_intent)
    lines = [_compose_opening(q_intent, rs, ctx), ""]
    for a in achievements:
        title = a.get("title", "")
        desc = a.get("description", "")
        if not title:
            continue
        lines.append(f"**{title}**")
        if desc:
            lines.append(desc)
        lines.append("")

    lines.append(
        "The signal: someone who turns concepts into credible working systems "
        "quickly — the same profile that suits both senior roles and short "
        "high-leverage projects."
    )
    return _join_lines(lines)


def _answer_engagement(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    options = data.get("engagement_options") or []
    services = data.get("custom_services") or []
    pricing_notes = data.get("pricing_notes") or ""
    stack = data.get("stack_highlight") or ""
    availability = data.get("availability_summary") or ""
    cta = data.get("contact_cta") or ""

    if not options and not services:
        return _INSUFFICIENT_EVIDENCE

    rs = style or select_response_style(q_intent)
    opener = _compose_opening(q_intent, rs)
    lines = [opener + "\n"]

    if stack:
        lines.append(f"He delivers on {stack}.")
        lines.append("")

    source = services if services else options
    lines.append("The engagements that fit him best:")
    for opt in source:
        name = opt.get("name") or opt.get("type", "")
        desc = opt.get("description", "")
        if name:
            lines.append(f"— **{name}** — {desc}")

    evidence = _project_evidence_line(message)
    if evidence:
        lines.append("")
        lines.append(evidence)

    if pricing_notes:
        lines.append("")
        lines.append(pricing_notes)

    if availability:
        lines.append("")
        lines.append(availability)
    if cta:
        lines.append("")
        lines.append(cta)
    return _join_lines(lines)


# Subtype detection for the `contact` intent. Ordered by priority:
# rates > contact_details > project_enquiry.
_RATES_PATTERNS = (
    "day rate", "day-rate", "day rates", "rates", "rate?",
    "pricing", "price", "quote", "cost", "budget",
)
_CONTACT_DETAILS_PATTERNS = (
    "contact david", "contact details", "how do i contact",
    "how can i contact", "how to contact", "how do i reach",
    "how can i reach", "reach david", "get in touch",
    "in touch with david", "email david", "david's email",
    "davids email", "email address", "phone number", "mobile number",
)
_PROJECT_ENQUIRY_PATTERNS = (
    "help us build", "build this for us", "can david help us",
    "hire david", "work with david", "working with david",
    "start a project", "discuss a project", "discuss the project",
    "can we work together", "build an mvp", "build us", "build for us",
)


def _contact_subtype(message: str) -> str:
    text = (message or "").lower()
    if any(p in text for p in _RATES_PATTERNS):
        return "rates"
    if any(p in text for p in _CONTACT_DETAILS_PATTERNS):
        return "contact_details"
    if any(p in text for p in _PROJECT_ENQUIRY_PATTERNS):
        return "project_enquiry"
    return "project_enquiry"


def _pricing_block(services: list[dict]) -> list[str]:
    lines = [
        f"— **{svc.get('name', '')}:** {svc.get('pricing', '')}"
        for svc in services
        if svc.get("pricing")
    ]
    if not lines:
        return []
    return ["As an indicative view of pricing:", *lines]


def _engagements_block(services: list[dict]) -> list[str]:
    lines = []
    for svc in services:
        name = svc.get("name", "")
        desc = svc.get("description", "")
        if name:
            lines.append(f"— **{name}** — {desc}")
    if not lines:
        return []
    return ["The engagements that fit him best:", *lines]


def _answer_contact(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    services = data.get("custom_services") or []
    pricing_notes = data.get("pricing_notes") or ""
    cta = data.get("contact_cta") or ""
    available_projects = data.get("projects") or []

    if not services and not cta:
        return _INSUFFICIENT_EVIDENCE

    subtype = _contact_subtype(message)
    evidence = _project_evidence_line(message, available_projects)
    sections: list[list[str]] = []

    if subtype == "rates":
        sections.append([
            "David's rates depend on the shape of the engagement, but here "
            "is a useful indicative view."
        ])
        if services:
            sections.append(_pricing_block(services))
            sections.append(_engagements_block(services))
        if evidence:
            sections.append([evidence])
        if pricing_notes:
            sections.append([pricing_notes])
        if cta:
            sections.append([cta])

    elif subtype == "contact_details":
        sections.append([
            "The cleanest way to reach David is through the project contact "
            "form on the site. A short outline of the scope, timeline, and "
            "goals is the most useful starting point — he reads every "
            "enquiry personally."
        ])
        if services:
            short = [
                f"— **{svc.get('name', '')}** — {svc.get('description', '')}"
                for svc in services[:3]
                if svc.get("name")
            ]
            if short:
                sections.append(["For a rough sense of the engagement shapes he takes on:", *short])
        sections.append([
            "Indicative rates and delivery specifics are easiest to "
            "discuss once the scope is clear."
        ])
        if evidence:
            sections.append([evidence])
        if cta:
            sections.append([cta])

    else:  # project_enquiry
        sections.append([
            "Yes — this is the kind of work David is a strong fit for, "
            "particularly MVP builds and applied AI project delivery where "
            "speed, technical clarity, and architecture-led execution "
            "matter."
        ])
        if services:
            sections.append(_engagements_block(services))
        if evidence:
            sections.append([evidence])
        if services:
            sections.append(_pricing_block(services))
        if pricing_notes:
            sections.append([pricing_notes])
        if cta:
            sections.append([cta])

    # Join sections with blank-line separators.
    out: list[str] = []
    for i, section in enumerate(sections):
        if not section:
            continue
        if out:
            out.append("")
        out.extend(section)
    return _join_lines(out)


def _answer_faq(
    data: dict[str, Any], message: str,
    q_intent: QuestionIntent = QuestionIntent.GENERAL_PROFILE,
    style: ResponseStyle | None = None,
) -> str:
    faqs = data.get("faqs") or []
    if not faqs:
        return _INSUFFICIENT_EVIDENCE

    lines: list[str] = []
    for f in faqs[:3]:
        q = f.get("question", "")
        a = f.get("answer", "")
        if not q or not a:
            continue
        lines.append(f"**{q}**")
        lines.append(a)
        lines.append("")

    evidence = _project_evidence_line(message)
    if evidence:
        lines.append(evidence)
        lines.append("")

    lines.append(
        "Python backend + Next.js frontend delivery is his default posture, "
        "whether for senior roles or short builds."
    )
    return _join_lines(lines) or _INSUFFICIENT_EVIDENCE


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_HANDLERS = {
    "skills": _answer_skills,
    "strengths": _answer_strengths,
    "projects": _answer_projects,
    "experience": _answer_experience,
    "technical_stack": _answer_technical_stack,
    "role_fit": _answer_role_fit,
    "preferred_roles": _answer_preferred_roles,
    "availability": _answer_availability,
    "achievements": _answer_achievements,
    "engagement": _answer_engagement,
    "contact": _answer_contact,
    "faq": _answer_faq,
}


def build_answer(
    intent: Intent,
    data: dict[str, Any],
    message: str = "",
    question_intent: QuestionIntent | None = None,
) -> str:
    """Return a recruiter-grade answer for the given intent and retrieved data.

    `message` is the original user query — used for lightweight context-aware
    openings and project-evidence selection. Safe to omit in tests; answers
    degrade gracefully to the generic opener.

    `question_intent` drives the opening-line style. If not provided the
    handlers fall back to their default openers.
    """
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

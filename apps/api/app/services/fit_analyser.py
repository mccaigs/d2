"""Deterministic job description fit analyser.

Output is shaped for hiring decision support:
    summary, overall_score, fit_label, strengths, gaps, relevant_projects,
    talking_points.

No LLM. All matching is token / phrase based against structured profile data.
"""

import json
import re
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load(filename: str) -> Any:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenise(text: str) -> set[str]:
    norm = _normalise(text)
    norm = re.sub(r"[^\w\s\-\.]", " ", norm)
    return {t for t in norm.split() if len(t) > 1}


def _any_hit(jd_norm: str, jd_tokens: set[str], terms: list[str]) -> bool:
    for term in terms:
        if " " in term or "-" in term or "." in term:
            if term in jd_norm:
                return True
        elif term in jd_tokens:
            return True
    return False


def _count_hits(jd_norm: str, jd_tokens: set[str], terms: list[str]) -> int:
    hits = 0
    for term in terms:
        if " " in term or "-" in term or "." in term:
            if term in jd_norm:
                hits += 1
        elif term in jd_tokens:
            hits += 1
    return hits


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

_TECHNICAL = {
    "target": 6,
    "terms": [
        "python", "fastapi", "next.js", "nextjs", "react", "typescript",
        "tailwind", "convex", "api", "backend", "frontend", "full stack",
        "full-stack", "fullstack", "rest", "graphql", "sql", "database",
        "docker", "testing", "engineer", "engineering", "developer",
        "deployment", "infrastructure",
    ],
}

_AI = {
    "target": 5,
    "terms": [
        "ai", "artificial intelligence", "machine learning", "ml", "llm",
        "gpt", "openai", "anthropic", "agentic", "agent", "agents",
        "rag", "retrieval", "embedding", "vector", "prompt",
        "applied ai", "generative", "nlp", "language model", "chatbot",
        "automation", "workflow", "pipeline", "mcp",
    ],
}

_PRODUCT_ARCH = {
    "target": 4,
    "terms": [
        "architecture", "architect", "platform", "system", "systems",
        "design", "product", "saas", "mvp", "roadmap",
        "technical lead", "tech lead", "principal", "staff",
        "ownership", "scalable", "scalability",
        "solution", "solutions", "delivery", "end-to-end",
    ],
}

_DOMAIN = {
    "target": 3,
    "terms": [
        "recruitment", "recruiter", "talent", "hiring", "candidate",
        "interview", "assessment", "hr", "hrtech", "edtech",
        "saas", "b2b", "marketplace", "startup", "scale-up", "scaleup",
        "developer tools", "devtools", "tooling",
    ],
}

_SENIORITY = {
    "target": 3,
    "terms": [
        "senior", "lead", "principal", "staff", "architect", "head",
        "founding", "hands-on", "autonomous", "independent",
        "ownership", "strategic", "mentor",
    ],
}


def _dim_score(jd_norm: str, jd_tokens: set[str], dim: dict) -> float:
    hits = _count_hits(jd_norm, jd_tokens, dim["terms"])
    return min(hits / max(dim["target"], 1), 1.0)


# ---------------------------------------------------------------------------
# Strengths
# ---------------------------------------------------------------------------

_STRENGTHS: list[dict] = [
    {
        "keywords": ["python", "fastapi", "backend", "api", "server", "service"],
        "text": "Production Python and FastAPI backends with typed APIs and a "
                "clear service layer — matches the engineering bar implied by this role.",
    },
    {
        "keywords": ["next.js", "nextjs", "react", "typescript", "frontend", "ui", "tailwind"],
        "text": "Next.js + TypeScript frontends with App Router and streaming UX — "
                "directly relevant to the product surfaces described in the JD.",
    },
    {
        "keywords": ["ai", "llm", "agentic", "agent", "applied ai", "ml", "rag",
                     "generative", "prompt", "mcp"],
        "text": "Applied AI systems design — deterministic pipelines paired with "
                "LLM and agentic components, not prompt-only wrappers.",
    },
    {
        "keywords": ["full stack", "full-stack", "fullstack", "saas", "product",
                     "end-to-end", "mvp"],
        "text": "End-to-end SaaS delivery on Python + Next.js: backend, frontend, "
                "data, auth, billing — shipped as working products, not prototypes.",
    },
    {
        "keywords": ["architecture", "architect", "system", "systems", "platform",
                     "solutions", "solution"],
        "text": "Architecture-led delivery — service separation, knowledge layers, "
                "and long-term maintainability built in from day one.",
    },
    {
        "keywords": ["automation", "pipeline", "workflow", "scoring", "matching"],
        "text": "Workflow automation and scoring pipelines — repeatable systems "
                "that turn messy inputs into structured, decision-ready outputs.",
    },
    {
        "keywords": ["recruiter", "recruitment", "hiring", "candidate", "talent",
                     "interview", "assessment"],
        "text": "Direct recruitment-domain experience — candidate intelligence, "
                "recruiter-side scoring, and interview evaluation systems already built.",
    },
    {
        "keywords": ["senior", "lead", "principal", "founding", "ownership",
                     "architect", "staff"],
        "text": "Senior IC posture with ownership habits — scopes, decides, and "
                "ships without needing close supervision.",
    },
]


# ---------------------------------------------------------------------------
# Gaps — framed as role expectation vs David's published profile.
# Honest, specific, never softened.
# ---------------------------------------------------------------------------

_GAPS: list[dict] = [
    {
        "keywords": ["manage", "management", "manager", "headcount", "org design",
                     "people manager", "line manage", "direct reports"],
        "area": "People management",
        "note": "This role expects hands-on people management; David operates "
                "primarily as a senior IC / architect and has no published "
                "track record of managing direct reports.",
    },
    {
        "keywords": ["sales", "pre-sales", "presales", "revenue", "quota",
                     "commercial lead", "account management"],
        "area": "Sales / commercial ownership",
        "note": "This role carries a revenue or pre-sales expectation; David's "
                "background is engineering and product delivery, not commercial "
                "ownership.",
    },
    {
        "keywords": ["ios", "android", "mobile", "swift", "kotlin",
                     "react native", "flutter"],
        "area": "Mobile development",
        "note": "This role expects native or cross-platform mobile shipping; "
                "David's public profile shows no mobile delivery experience.",
    },
    {
        "keywords": ["data scientist", "research scientist", "phd",
                     "academic research", "statistics", "scipy", "pandas",
                     "jupyter"],
        "area": "Research / data science",
        "note": "This role leans research-ML or data-science; David focuses on "
                "applied AI systems and delivery, not statistical modelling or "
                "notebook-driven research.",
    },
    {
        "keywords": ["java", "c#", ".net", "c++", "mainframe", "oracle",
                     "sap", "cobol"],
        "area": "Legacy enterprise stacks",
        "note": "This role expects a legacy enterprise stack; David's delivery "
                "stack is modern — Python, TypeScript, and cloud-native tooling.",
    },
    {
        "keywords": ["devops", "sre", "kubernetes", "terraform", "helm",
                     "observability", "prometheus"],
        "area": "Dedicated DevOps / SRE",
        "note": "This role expects a dedicated DevOps or SRE specialist; David "
                "deploys modern cloud-native stacks but has not positioned "
                "himself as an SRE.",
    },
    {
        "keywords": ["fintech", "banking", "trading", "payments platform",
                     "healthcare", "clinical", "gaming"],
        "area": "Domain experience",
        "note": "This role requires domain experience in a regulated or "
                "specialist sector; David has no published record of working "
                "in that specific domain.",
    },
]


# ---------------------------------------------------------------------------
# Projects — with role-aware rationale that references the delivery stack.
# ---------------------------------------------------------------------------

_PROJECTS: list[dict] = [
    {
        "name": "CareersAI",
        "keywords": ["recruitment", "recruiter", "candidate", "hiring", "talent",
                     "scoring", "matching", "saas", "job"],
        "reason": "Closest parallel to the brief — AI job intelligence platform "
                   "with fit scoring and candidate matching, built on Next.js + "
                   "TypeScript with applied-AI scoring logic.",
    },
    {
        "name": "RecruitersAI",
        "keywords": ["recruiter", "recruitment", "hiring", "talent", "candidate",
                     "scoring", "ranking", "saas", "workflow"],
        "reason": "Recruiter-side intelligence platform — structured scoring, "
                   "ranking, and workflow design. Matches the hiring-team surface "
                   "area this JD describes.",
    },
    {
        "name": "InterviewsAI",
        "keywords": ["interview", "assessment", "evaluation", "scoring",
                     "pipeline", "ai", "python", "fastapi", "backend"],
        "reason": "Applied AI evaluation product on Python + FastAPI + Next.js — "
                   "mirrors the production AI system shape in the JD, including "
                   "scoring logic and adaptive flow.",
    },
    {
        "name": "UK AI Jobs Pipeline",
        "keywords": ["automation", "pipeline", "workflow", "scoring", "matching",
                     "ai", "python", "sourcing", "data"],
        "reason": "Repeatable AI-assisted automation pipeline in Python — "
                   "demonstrates the sourcing, filtering, and scoring workflow "
                   "pattern the role expects.",
    },
    {
        "name": "AI IDE Initiative",
        "keywords": ["developer tools", "devtools", "ide", "tooling", "ai",
                     "architecture", "product", "mcp", "agent"],
        "reason": "AI developer tooling concept — model routing, local/cloud "
                   "workflows, and architecture-first thinking about AI-native "
                   "products.",
    },
]


def _select_strengths(jd_norm: str, jd_tokens: set[str]) -> list[str]:
    matched = [s["text"] for s in _STRENGTHS
               if _any_hit(jd_norm, jd_tokens, s["keywords"])]
    if not matched:
        matched.append(
            "Applied AI systems design on Python + Next.js — David's default "
            "delivery posture regardless of domain."
        )
    return matched[:6]


def _select_gaps(jd_norm: str, jd_tokens: set[str]) -> list[dict]:
    return [
        {"area": g["area"], "note": g["note"]}
        for g in _GAPS
        if _any_hit(jd_norm, jd_tokens, g["keywords"])
    ]


def _select_projects(jd_norm: str, jd_tokens: set[str]) -> list[dict]:
    scored: list[tuple[int, dict]] = []
    for p in _PROJECTS:
        hits = _count_hits(jd_norm, jd_tokens, p["keywords"])
        if hits > 0:
            scored.append((hits, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # Default generalists: Python + Next.js evidence first.
        scored = [(1, _PROJECTS[2]), (1, _PROJECTS[0])]

    return [{"name": p["name"], "reason": p["reason"]} for _, p in scored[:3]]


def _select_talking_points(jd_norm: str, jd_tokens: set[str]) -> list[str]:
    points: list[str] = []

    if _any_hit(jd_norm, jd_tokens, ["ai", "llm", "agentic", "applied ai", "ml", "rag"]):
        points.append(
            "How David designs deterministic pipelines alongside LLM and "
            "agentic components"
        )
    if _any_hit(jd_norm, jd_tokens, ["python", "fastapi", "backend", "api"]):
        points.append(
            "Python and FastAPI in production — typed services, deterministic "
            "logic, and service-layer architecture"
        )
    if _any_hit(jd_norm, jd_tokens, ["next.js", "nextjs", "react", "typescript",
                                      "frontend", "ui"]):
        points.append(
            "Approach to full-stack AI product development using Next.js, "
            "TypeScript, and streaming UX"
        )
    if _any_hit(jd_norm, jd_tokens, ["architecture", "architect", "system",
                                      "platform", "solutions"]):
        points.append(
            "Architectural decisions on recent builds — service separation, "
            "knowledge layers, and long-term maintainability"
        )
    if _any_hit(jd_norm, jd_tokens, ["recruitment", "recruiter", "talent",
                                      "hiring", "candidate", "interview"]):
        points.append(
            "Recruitment-domain projects (CareersAI, RecruitersAI, "
            "InterviewsAI) and the patterns that transferred between them"
        )
    if _any_hit(jd_norm, jd_tokens, ["saas", "product", "mvp", "startup",
                                      "founding", "founder"]):
        points.append(
            "How David scopes and ships SaaS MVPs end-to-end without losing "
            "production quality"
        )
    if _any_hit(jd_norm, jd_tokens, ["senior", "lead", "principal", "architect",
                                      "ownership", "staff"]):
        points.append(
            "Working as a senior IC with architectural ownership — decision "
            "latitude, trade-off handling, and delivery accountability"
        )

    if not points:
        points.append(
            "David's applied AI portfolio and how his Python + Next.js stack "
            "maps onto production product work"
        )

    return points[:5]


# ---------------------------------------------------------------------------
# Scoring & summary
# ---------------------------------------------------------------------------

_DIMENSION_WEIGHTS = {
    "technical": 0.25,
    "ai": 0.30,
    "product_arch": 0.25,
    "domain": 0.10,
    "seniority": 0.10,
}


def _overall_score(scores: dict[str, float]) -> int:
    weighted = sum(scores[k] * _DIMENSION_WEIGHTS[k] for k in _DIMENSION_WEIGHTS)
    if scores["ai"] < 0.2:
        weighted = min(weighted, 0.55)
    if scores["technical"] < 0.15 and scores["product_arch"] < 0.15:
        weighted = min(weighted, 0.45)
    return round(max(0.0, min(weighted, 1.0)) * 100)


def _breakdown_scores(scores: dict[str, float]) -> dict[str, int]:
    """Convert raw 0‒1 dimension scores to integer sub-scores on a 0‒100 scale.

    Uses a floor + range mapping so that any non-zero signal starts at 50
    rather than near-zero — this better reflects that even a partial hit means
    the JD *does* mention the category.
    """
    out: dict[str, int] = {}
    label_map = {
        "technical": "technical",
        "ai": "applied_ai",
        "product_arch": "product_architecture",
        "domain": "domain",
        "seniority": "seniority",
    }
    for key, label in label_map.items():
        raw = scores[key]
        if raw <= 0.0:
            out[label] = 0
        else:
            # Map (0, 1] → [50, 100]
            out[label] = round(50 + raw * 50)
        out[label] = max(0, min(out[label], 100))
    return out


def _compute_confidence(
    scores: dict[str, float],
    jd_norm: str,
    jd_tokens: set[str],
) -> tuple[str, str]:
    """Deterministic confidence indicator based on signal coverage.

    Returns (level, reason) where level is 'high', 'medium', or 'low'.
    """
    # Count how many dimensions have strong signal (>= 0.5)
    strong_dims = [k for k, v in scores.items() if v >= 0.5]
    moderate_dims = [k for k, v in scores.items() if 0.2 <= v < 0.5]
    weak_dims = [k for k, v in scores.items() if v < 0.2]

    dim_label = {
        "technical": "technical stack",
        "ai": "applied AI",
        "product_arch": "product and architecture",
        "domain": "domain relevance",
        "seniority": "seniority alignment",
    }

    # Token count as a secondary signal — very short JDs get penalised
    token_count = len(jd_tokens)

    if len(strong_dims) >= 3 and token_count >= 30:
        top_labels = " and ".join(dim_label[d] for d in strong_dims[:3])
        return (
            "high",
            f"Based on direct experience signals across {top_labels}",
        )

    if len(strong_dims) >= 2:
        top_labels = " and ".join(dim_label[d] for d in strong_dims[:2])
        return (
            "high",
            f"Based on direct experience signals across {top_labels}",
        )

    if len(strong_dims) >= 1 and len(moderate_dims) >= 1:
        return (
            "medium",
            "Partial alignment — strong signals in some areas, inferred in others",
        )

    if len(strong_dims) >= 1:
        return (
            "medium",
            f"Direct signal on {dim_label[strong_dims[0]]}, but limited coverage elsewhere",
        )

    if len(moderate_dims) >= 2:
        return (
            "medium",
            "Moderate alignment inferred from partial signals across the brief",
        )

    if token_count < 15:
        return (
            "low",
            "Very short job description — insufficient detail for reliable scoring",
        )

    return (
        "low",
        "Weak or sparse signal coverage across the brief",
    )


def _label(score: int) -> str:
    if score >= 80:
        return "Strong fit"
    if score >= 65:
        return "Good fit"
    if score >= 50:
        return "Partial fit"
    return "Weak fit"


_DIM_LABEL = {
    "technical": "technical stack",
    "ai": "applied AI",
    "product_arch": "product and architecture",
    "domain": "domain relevance",
    "seniority": "seniority alignment",
}


def _role_context(jd_norm: str) -> str:
    """Short clause describing the role, for the opening line."""
    if "solutions architect" in jd_norm or "solution architect" in jd_norm:
        return "a solutions architect role"
    if "founding" in jd_norm:
        return "a founding engineer seat"
    if re.search(r"\bai\s+(engineer|engineering)\b", jd_norm):
        return "an AI engineering role"
    if re.search(r"\bapplied\s+ai\b", jd_norm):
        return "applied AI work"
    if re.search(r"\bai\s+product\b", jd_norm):
        return "AI product work"
    if re.search(r"\bfull[-\s]?stack\b", jd_norm):
        return "full-stack delivery"
    if re.search(r"\brecruit", jd_norm):
        return "recruitment-domain work"
    if re.search(r"\bsenior\b", jd_norm):
        return "a senior engineering role"
    return "this role"


def _hire_signal(score: int, strengths: list[str], gaps: list[dict]) -> str:
    """Short closing line: strong interview area, or main evaluation risk."""
    if score >= 80:
        anchor = (
            "applied AI design and Python + Next.js delivery"
            if strengths else "his core delivery stack"
        )
        return f"Strong interview expected on {anchor}."
    if score >= 65:
        risk = gaps[0]["area"].lower() if gaps else "domain depth"
        return (
            f"Strong interview expected on core engineering; main evaluation "
            f"risk would be {risk}."
        )
    if score >= 50:
        risk = gaps[0]["area"].lower() if gaps else "coverage of the full brief"
        return f"Main evaluation risk would be {risk}."
    risk = gaps[0]["area"].lower() if gaps else "core alignment with the brief"
    return f"Main evaluation risk would be {risk} — recommend caution before interview."


def _build_summary(
    score: int,
    label: str,
    scores: dict[str, float],
    jd_norm: str,
    strengths: list[str],
    gaps: list[dict],
) -> str:
    role_ctx = _role_context(jd_norm)

    # Sentence 1 — explicit fit level + context.
    if label == "Strong fit":
        s1 = (
            f"David is a **strong fit** for {role_ctx}. Scored at "
            f"**{score}/100**, the brief maps cleanly onto his core strengths."
        )
    elif label == "Good fit":
        s1 = (
            f"David is a **good fit** for {role_ctx}. At **{score}/100**, the "
            f"core of the brief lines up with his profile, with one or two "
            f"gaps worth probing."
        )
    elif label == "Partial fit":
        s1 = (
            f"David is a **partial fit** for {role_ctx}. At **{score}/100**, "
            f"there is real overlap, but significant parts of the brief sit "
            f"outside his published evidence."
        )
    else:
        s1 = (
            f"David is a **weak fit** for {role_ctx} as written. At "
            f"**{score}/100**, too little of the brief overlaps with his "
            f"documented strengths to recommend him confidently."
        )

    # Sentence 2 — strongest alignment.
    top_dims = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strong = [_DIM_LABEL[k] for k, v in top_dims[:2] if v >= 0.5]
    if strong:
        s2 = "The strongest alignment is on " + " and ".join(strong) + "."
    else:
        s2 = (
            "No single dimension aligns strongly with the profile — this JD "
            "sits partly outside David's core territory."
        )

    # Sentence 3 — main risk/gap framed against the role.
    if gaps:
        g = gaps[0]
        s3 = f"The main risk is **{g['area'].lower()}**: {g['note']}"
    else:
        s3 = (
            "No disqualifying gaps surfaced from the job description, "
            "though seniority and scope should still be confirmed."
        )

    # Sentence 4 — hire signal.
    s4 = _hire_signal(score, strengths, gaps)

    return f"{s1}\n\n{s2} {s3}\n\n{s4}"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyse_fit(job_description: str) -> dict:
    if not job_description or not job_description.strip():
        return {
            "summary": (
                "No job description was provided, so there is nothing to "
                "score against. Paste the full JD and try again."
            ),
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
            "confidence_reason": "No job description provided",
            "strengths": [],
            "gaps": [],
            "relevant_projects": [],
            "talking_points": [],
        }

    jd_norm = _normalise(job_description)
    jd_tokens = _tokenise(job_description)

    scores = {
        "technical": _dim_score(jd_norm, jd_tokens, _TECHNICAL),
        "ai": _dim_score(jd_norm, jd_tokens, _AI),
        "product_arch": _dim_score(jd_norm, jd_tokens, _PRODUCT_ARCH),
        "domain": _dim_score(jd_norm, jd_tokens, _DOMAIN),
        "seniority": _dim_score(jd_norm, jd_tokens, _SENIORITY),
    }

    overall = _overall_score(scores)
    label = _label(overall)
    breakdown = _breakdown_scores(scores)
    confidence, confidence_reason = _compute_confidence(scores, jd_norm, jd_tokens)

    strengths = _select_strengths(jd_norm, jd_tokens)
    gaps = _select_gaps(jd_norm, jd_tokens)
    projects = _select_projects(jd_norm, jd_tokens)
    talking_points = _select_talking_points(jd_norm, jd_tokens)

    summary = _build_summary(overall, label, scores, jd_norm, strengths, gaps)

    return {
        "summary": summary,
        "overall_score": overall,
        "fit_label": label,
        "breakdown": breakdown,
        "confidence": confidence,
        "confidence_reason": confidence_reason,
        "strengths": strengths,
        "gaps": gaps,
        "relevant_projects": projects,
        "talking_points": talking_points,
    }

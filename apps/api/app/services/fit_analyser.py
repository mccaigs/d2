"""Deterministic job description fit analyser — v2.

Evidence-aware scoring model:
  - Role type detection drives adaptive dimension weights.
  - David's published profile capability scores provide evidence floors that
    prevent false-zero penalties when JD vocabulary differs from his stack.
  - Evidence is tiered: direct (JD matches David's words), inferred (adjacent
    capability), and true gap (no evidence + genuinely missing).
  - Missing keywords never equal missing capability.
  - Historical leadership (Sodexo Prestige, operations at scale) is counted.

Output shaped for hiring decision support:
    summary, overall_score, fit_label, strengths, gaps, relevant_projects,
    talking_points.

No LLM. All matching is token / phrase-based against structured profile data.
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
# David's published profile capability scores (evidence-based constants).
#
# These represent the evidence floor for each scoring dimension, derived from
# David's CV and project record. They prevent false-zero penalties when the
# JD uses vocabulary that differs from David's stated stack.
#
# Scale: 0.0 (no evidence) → 1.0 (definitive, extensive published evidence).
# Tune these as the profile evolves.
# ---------------------------------------------------------------------------

_DAVID_CAPABILITY = {
    # Strong: Python, TypeScript, Docker, REST APIs, cloud deployment, Linux VPS
    "technical":    0.85,
    # Core identity: AI architect, deterministic scoring engines, LLM
    # orchestration, agent pipelines, multiple AI-first SaaS products shipped
    "ai":           1.00,
    # Core identity: architecture-led SaaS, service separation, end-to-end
    # delivery from concept through production
    "product_arch": 0.90,
    # Moderate: recruitment/EdTech domain is strong; other sectors are
    # transferable via operational delivery and stakeholder management
    "domain":       0.35,
    # Strong: 20+ years total, senior IC posture, Sodexo Prestige operational
    # leadership at large scale, multiple founder roles
    "seniority":    0.85,
}

# Role-specific domain capability overrides.
# Recruitment/EdTech sit above the general floor; SA/enterprise draws on
# David's operational delivery and stakeholder management history.
_DAVID_DOMAIN_CAPABILITY_BY_ROLE = {
    "recruitment":       0.90,
    "edtech":            0.75,
    "ai_engineering":    0.80,  # AI product domain — David's core ground
    "solution_architect": 0.55, # Operational delivery, stakeholder mgmt, complex envs
    "fullstack":         0.50,
    "general_tech":      0.40,
}

# Role-specific technical capability overrides.
#
# David's overall technical depth is high (0.85), but the FORM it takes
# differs by role archetype:
#
#   solution_architect — His stack is modern cloud-native (Docker / Linux VPS /
#       REST APIs / CI-CD). He can reason about Azure IaaS/PaaS architecturally
#       but has no published Azure-specific delivery or certification.  The
#       expanded SA technical terms saturate JD signal quickly; without a lower
#       cap the score would overstate direct Azure experience.
#
#   ai_engineering / fullstack — Python + FastAPI + Next.js is David's exact
#       primary stack, so full capability credit is warranted.
#
# Tune this as David's profile adds explicit cloud/enterprise SA evidence.
_DAVID_TECH_CAPABILITY_BY_ROLE: dict[str, float] = {
    "solution_architect": 0.68,   # Modern cloud-native, not Azure-certified SA
    "ai_engineering":     0.90,   # Python / FastAPI is home ground
    "fullstack":          0.90,   # React / Next.js / TypeScript is primary stack
    "general_tech":       0.85,   # Default — strong modern developer
}

# People management evidence flag.
# David managed large-scale operations teams at Sodexo Prestige (5 000+ staff).
# Used to downgrade the people-management gap from "hard gap" to "discussion risk".
_DAVID_HAS_PEOPLE_MANAGEMENT = True


# ---------------------------------------------------------------------------
# Dimensions — JD-side term matching
# ---------------------------------------------------------------------------

_TECHNICAL = {
    # Target hits before the dimension is considered fully covered.
    # Keep this calibrated: too high → hard to score 1.0; too low → saturates.
    "target": 6,
    "terms": [
        # Modern developer stack
        "python", "fastapi", "next.js", "nextjs", "react", "typescript",
        "tailwind", "convex", "api", "apis", "backend", "frontend",
        "full stack", "full-stack", "fullstack", "rest", "graphql",
        "sql", "database", "docker", "testing", "engineer", "engineering",
        "developer", "deployment", "infrastructure",
        # Enterprise / solution-architect stack
        "azure", "aws", "gcp", "cloud", "on-premises", "on-prem",
        "iaas", "paas", "hybrid", "integration", "service design",
        "hld", "high level design", "high-level design",
        "lld", "low level design",
        "microservices", "messaging", "esb", "event-driven",
        "devops", "ci/cd", "cicd", "agile", "itil", "togaf",
        "networking", "security", "compliance", "monitoring",
        "service management", "cloud-native",
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
        # Solution-architect-specific
        "service design", "solution design", "enterprise architecture",
        "high level design", "hld", "technical architecture",
    ],
}

_DOMAIN = {
    "target": 3,
    "terms": [
        # Recruitment / HR domain
        "recruitment", "recruiter", "talent", "hiring", "candidate",
        "interview", "assessment", "hr", "hrtech", "edtech",
        # General product / startup domain signals
        "saas", "b2b", "marketplace", "startup", "scale-up", "scaleup",
        "developer tools", "devtools", "tooling",
        # Public sector / regulated / operational domain signals
        "public sector", "government", "utilities", "transport",
        "regulated", "mission-critical", "mission critical",
        "operational", "stakeholder", "service management",
        "client-facing", "customer-facing", "end user", "end-user",
        "complex environment", "enterprise", "large organisation",
    ],
}

_SENIORITY = {
    "target": 3,
    "terms": [
        "senior", "lead", "principal", "staff", "architect", "head",
        "founding", "hands-on", "autonomous", "independent",
        "ownership", "strategic", "mentor",
        # Operational / enterprise seniority signals
        "director", "manager", "management", "leadership",
        "stakeholder management", "executive",
    ],
}


# ---------------------------------------------------------------------------
# Role type detection
# ---------------------------------------------------------------------------

# SA signals — explicit role title or structural SA artefacts in the JD
_SA_ROLE_SIGNALS = [
    "solution architect", "solutions architect", "solution designer",
    "enterprise architect", "technical architect", "infrastructure architect",
    "cloud architect", "it architect", "service design",
    "hld", "high level design", "high-level design",
]

_AI_ROLE_SIGNALS = [
    "ai engineer", "ai engineering", "machine learning engineer",
    "ml engineer", "applied ai", "llm engineer", "ai product",
    "ai platform", "data scientist", "ai architect",
]

_FULLSTACK_ROLE_SIGNALS = [
    "full stack", "full-stack", "fullstack",
    "frontend engineer", "backend engineer",
    "software engineer", "web developer",
]


def _detect_role_type(jd_norm: str, jd_tokens: set[str]) -> str:
    """Classify the JD into a role archetype.

    Used to select appropriate dimension weights and domain capability scores.
    Precedence: solution_architect > ai_engineering > fullstack > general_tech.
    """
    if _any_hit(jd_norm, jd_tokens, _SA_ROLE_SIGNALS):
        return "solution_architect"
    if _any_hit(jd_norm, jd_tokens, _AI_ROLE_SIGNALS):
        return "ai_engineering"
    if _any_hit(jd_norm, jd_tokens, _FULLSTACK_ROLE_SIGNALS):
        return "fullstack"
    return "general_tech"


# ---------------------------------------------------------------------------
# Dimension weights by role type.
#
# AI weight is intentionally suppressed for non-AI roles.  David's AI
# capability should not count against him when a role doesn't require AI —
# it simply isn't relevant, so it should neither boost nor penalise.
#
# product_arch gets the largest share for SA roles because architectural
# design and delivery quality are what the hiring manager cares about most.
# ---------------------------------------------------------------------------

_WEIGHTS_BY_ROLE_TYPE: dict[str, dict[str, float]] = {
    # Solution architect: architecture quality dominates; AI not a core ask
    "solution_architect": {
        "technical":    0.25,
        "ai":           0.05,
        "product_arch": 0.40,
        "domain":       0.15,
        "seniority":    0.15,
    },
    # AI engineering: AI is the primary signal; tech and arch also matter
    "ai_engineering": {
        "technical":    0.20,
        "ai":           0.35,
        "product_arch": 0.25,
        "domain":       0.10,
        "seniority":    0.10,
    },
    # Full-stack product engineering
    "fullstack": {
        "technical":    0.35,
        "ai":           0.15,
        "product_arch": 0.25,
        "domain":       0.15,
        "seniority":    0.10,
    },
    # General tech (default)
    "general_tech": {
        "technical":    0.25,
        "ai":           0.25,
        "product_arch": 0.25,
        "domain":       0.15,
        "seniority":    0.10,
    },
}

# Backward-compatible default (general tech)
_DIMENSION_WEIGHTS = _WEIGHTS_BY_ROLE_TYPE["general_tech"]


# ---------------------------------------------------------------------------
# Evidence-aware dimension scoring
# ---------------------------------------------------------------------------

def _dim_score(jd_norm: str, jd_tokens: set[str], dim: dict) -> float:
    """Raw JD-signal score: fraction of dimension terms found in the JD.

    Returns 0.0–1.0.  A score of 0.0 means the JD doesn't mention this
    dimension at all — not that David lacks the capability.
    """
    hits = _count_hits(jd_norm, jd_tokens, dim["terms"])
    return min(hits / max(dim["target"], 1), 1.0)


def _dim_score_evidence_aware(
    jd_norm: str,
    jd_tokens: set[str],
    dim: dict,
    david_cap: float,
) -> float:
    """Evidence-aware score: blends JD signal with David's known capability.

    Three regimes:
    - JD doesn't mention the dimension (signal = 0.0):
        → 0.5  (neutral — neither boost nor penalty).
          The role doesn't ask for it; David's possession of it is irrelevant.
    - JD weakly mentions the dimension (0 < signal < threshold):
        → interpolation between capability floor and full capability.
    - JD strongly mentions the dimension (signal ≥ threshold):
        → David's capability score dominates (he can cover what's asked).

    This prevents the false-zero penalty that fires when the JD uses different
    vocabulary for capabilities David clearly possesses (e.g., "Azure IaaS
    deployment" vs "Docker / Linux VPS deployment").

    Args:
        dim:       Dimension config dict with 'terms' and 'target' keys.
        david_cap: David's inherent capability for this dimension (0.0–1.0).

    Returns:
        Blended score 0.0–1.0.
    """
    jd_signal = _dim_score(jd_norm, jd_tokens, dim)

    if jd_signal == 0.0:
        # Role doesn't signal this dimension — neutral contribution.
        return 0.5

    # JD does require this dimension.  At full signal (1.0) David's capability
    # is the determining factor.  At minimal signal the score gravitates toward
    # a "capability floor" (david_cap * 0.6) to reflect partial evidence.
    capability_floor = david_cap * 0.6
    return jd_signal * david_cap + (1.0 - jd_signal) * capability_floor


# ---------------------------------------------------------------------------
# Strengths — recruiter-facing, specific, role-aware
# ---------------------------------------------------------------------------

_STRENGTHS: list[dict] = [
    {
        "keywords": ["python", "fastapi", "backend", "api", "apis", "server", "service"],
        "text": (
            "Production Python and FastAPI backends with typed APIs and a clear "
            "service layer — matches the engineering bar implied by this role."
        ),
    },
    {
        "keywords": ["next.js", "nextjs", "react", "typescript", "frontend", "ui", "tailwind"],
        "text": (
            "Next.js + TypeScript frontends with App Router and streaming UX — "
            "directly relevant to the product surfaces described in the JD."
        ),
    },
    {
        "keywords": ["ai", "llm", "agentic", "agent", "applied ai", "ml", "rag",
                     "generative", "prompt", "mcp"],
        "text": (
            "Applied AI systems design — deterministic pipelines paired with "
            "LLM and agentic components, not prompt-only wrappers."
        ),
    },
    {
        "keywords": ["full stack", "full-stack", "fullstack", "saas", "product",
                     "end-to-end", "mvp"],
        "text": (
            "End-to-end SaaS delivery on Python + Next.js: backend, frontend, "
            "data, auth, billing — shipped as working products, not prototypes."
        ),
    },
    {
        "keywords": ["architecture", "architect", "system", "systems", "platform",
                     "solutions", "solution", "solution design", "enterprise architecture",
                     "hld", "high level design"],
        "text": (
            "Architecture-led delivery — service separation, well-defined "
            "boundaries, and long-term maintainability built in from day one. "
            "Produces artefacts that explain, not just code that works."
        ),
    },
    {
        "keywords": ["automation", "pipeline", "workflow", "scoring", "matching"],
        "text": (
            "Workflow automation and scoring pipelines — repeatable systems "
            "that turn messy inputs into structured, decision-ready outputs."
        ),
    },
    {
        "keywords": ["recruiter", "recruitment", "hiring", "candidate", "talent",
                     "interview", "assessment"],
        "text": (
            "Direct recruitment-domain experience — candidate intelligence, "
            "recruiter-side scoring, and interview evaluation systems already built."
        ),
    },
    {
        "keywords": ["senior", "lead", "principal", "founding", "ownership",
                     "architect", "staff"],
        "text": (
            "Senior IC posture with ownership habits — scopes, decides, and "
            "ships without needing close supervision."
        ),
    },
    {
        "keywords": ["stakeholder", "stakeholder management", "client-facing",
                     "customer-facing", "communication", "operational"],
        "text": (
            "Stakeholder-facing delivery experience — operated in high-pressure "
            "commercial environments (Sodexo Prestige) with accountability to "
            "senior audiences. Bridges technical and non-technical stakeholders."
        ),
    },
    {
        "keywords": ["azure", "cloud", "iaas", "paas", "on-premises", "on-prem",
                     "infrastructure", "hybrid", "integration", "service design",
                     "hld", "devops", "ci/cd"],
        "text": (
            "Infrastructure and integration delivery — cloud deployment, service "
            "separation, and API-driven architecture translate directly to "
            "IaaS/PaaS solution design patterns."
        ),
    },
    {
        "keywords": ["agile", "delivery", "itil", "service management", "regulated",
                     "mission-critical"],
        "text": (
            "Delivery discipline in time-constrained, high-visibility environments "
            "— operational leadership at Sodexo and founder-paced product delivery "
            "both demand the same rigour this role requires."
        ),
    },
    {
        "keywords": ["manage", "management", "manager", "leadership", "team",
                     "people manager", "line manage", "direct reports"],
        "text": (
            "Operational leadership at scale — managed large-scale operations "
            "teams at Sodexo Prestige, including direct and indirect reports, "
            "in high-profile commercial environments."
        ),
    },
]


# ---------------------------------------------------------------------------
# Gaps — tiered: hard / soft / risk
#
# Tiers:
#   hard  — True disqualifying gap.  No evidence on the profile, the role
#           explicitly requires it, and it cannot be bridged by transfer.
#   soft  — Partial evidence exists or the gap is bridgeable with context.
#           Interview should probe, but not a blocker.
#   risk  — Discussion risk only.  David has adjacent/historical evidence;
#           the hiring team should confirm scope, not assume a gap.
#
# People management keywords are NARROWED to explicit direct-reports language.
# "stakeholder management" and "service management" should NOT fire this gap.
# ---------------------------------------------------------------------------

_GAPS: list[dict] = [
    {
        # Only fire when the JD explicitly requires managing direct reports
        "keywords": [
            "line manage", "direct reports", "people manager",
            "headcount", "org design", "manage a team", "managing a team",
            "leading a team", "people management", "staff management",
            "team manager", "line manager",
        ],
        "area": "People management (current role)",
        "tier": "risk",
        "note": (
            "This role expects hands-on management of direct reports. David's "
            "recent work is senior IC / architect. However, he managed "
            "large-scale operations teams at Sodexo Prestige — historical "
            "leadership evidence exists and should be explored at interview "
            "rather than treated as a hard gap."
        ),
    },
    {
        "keywords": [
            "sales", "pre-sales", "presales", "revenue", "quota",
            "commercial lead", "account management",
        ],
        "area": "Sales / commercial ownership",
        "tier": "hard",
        "note": (
            "This role carries a revenue or pre-sales expectation; David's "
            "background is engineering and product delivery, not commercial "
            "ownership."
        ),
    },
    {
        "keywords": [
            "ios", "android", "mobile", "swift", "kotlin",
            "react native", "flutter",
        ],
        "area": "Mobile development",
        "tier": "hard",
        "note": (
            "This role expects native or cross-platform mobile shipping; "
            "David's public profile shows no mobile delivery experience."
        ),
    },
    {
        "keywords": [
            "data scientist", "research scientist", "phd",
            "academic research", "statistics", "scipy", "pandas",
            "jupyter",
        ],
        "area": "Research / data science",
        "tier": "hard",
        "note": (
            "This role leans research-ML or data-science; David focuses on "
            "applied AI systems and delivery, not statistical modelling or "
            "notebook-driven research."
        ),
    },
    {
        "keywords": [
            "java", "c#", ".net", "c++", "mainframe", "oracle",
            "sap", "cobol",
        ],
        "area": "Legacy enterprise stacks",
        "tier": "soft",
        "note": (
            "This role expects a legacy enterprise stack; David's delivery "
            "stack is modern — Python, TypeScript, and cloud-native tooling. "
            "Bridging is possible but the team should confirm stack expectations."
        ),
    },
    {
        "keywords": [
            "devops engineer", "sre", "kubernetes", "terraform", "helm",
            "observability", "prometheus",
        ],
        "area": "Dedicated DevOps / SRE",
        "tier": "soft",
        "note": (
            "This role expects a dedicated DevOps or SRE specialist. David "
            "deploys cloud-native stacks and uses CI/CD, but has not "
            "positioned himself as a platform engineer or SRE."
        ),
    },
    {
        "keywords": [
            "fintech", "banking", "trading", "payments platform",
            "healthcare", "clinical", "gaming",
        ],
        "area": "Specialist domain experience",
        "tier": "soft",
        "note": (
            "This role requires domain experience in a regulated or specialist "
            "sector David has not explicitly worked in. Transferable delivery "
            "and stakeholder skills should be weighed against domain depth."
        ),
    },
]


# ---------------------------------------------------------------------------
# Projects — with role-aware rationale
# ---------------------------------------------------------------------------

_PROJECTS: list[dict] = [
    {
        "name": "CareersAI",
        "keywords": ["recruitment", "recruiter", "candidate", "hiring", "talent",
                     "scoring", "matching", "saas", "job"],
        "reason": (
            "Closest parallel to the brief — AI job intelligence platform "
            "with fit scoring and candidate matching, built on Next.js + "
            "TypeScript with applied-AI scoring logic."
        ),
    },
    {
        "name": "RecruitersAI",
        "keywords": ["recruiter", "recruitment", "hiring", "talent", "candidate",
                     "scoring", "ranking", "saas", "workflow"],
        "reason": (
            "Recruiter-side intelligence platform — structured scoring, "
            "ranking, and workflow design. Matches the hiring-team surface "
            "area this JD describes."
        ),
    },
    {
        "name": "InterviewsAI",
        "keywords": ["interview", "assessment", "evaluation", "scoring",
                     "pipeline", "ai", "python", "fastapi", "backend"],
        "reason": (
            "Applied AI evaluation product on Python + FastAPI + Next.js — "
            "mirrors the production AI system shape in the JD, including "
            "scoring logic and adaptive flow."
        ),
    },
    {
        "name": "UK AI Jobs Pipeline",
        "keywords": ["automation", "pipeline", "workflow", "scoring", "matching",
                     "ai", "python", "sourcing", "data"],
        "reason": (
            "Repeatable AI-assisted automation pipeline in Python — "
            "demonstrates the sourcing, filtering, and scoring workflow "
            "pattern the role expects."
        ),
    },
    {
        "name": "AI IDE Initiative",
        "keywords": ["developer tools", "devtools", "ide", "tooling", "ai",
                     "architecture", "product", "mcp", "agent"],
        "reason": (
            "AI developer tooling concept — model routing, local/cloud "
            "workflows, and architecture-first thinking about AI-native "
            "products."
        ),
    },
    {
        "name": "DavidRobertson.pro",
        "keywords": ["solution", "solutions", "architect", "architecture",
                     "system", "systems", "platform", "service design",
                     "azure", "cloud", "infrastructure", "integration",
                     "stakeholder", "delivery", "hld"],
        "reason": (
            "Production SaaS system with full service separation — FastAPI "
            "backend, Next.js frontend, auth, streaming, and data layers. "
            "Demonstrates the end-to-end architecture ownership expected in "
            "a Solution Architect role."
        ),
    },
]


# ---------------------------------------------------------------------------
# Gap selection
# ---------------------------------------------------------------------------

def _select_gaps(jd_norm: str, jd_tokens: set[str]) -> list[dict]:
    """Return gaps triggered by the JD, as structured dicts with tier."""
    return [
        {"area": g["area"], "tier": g["tier"], "note": g["note"]}
        for g in _GAPS
        if _any_hit(jd_norm, jd_tokens, g["keywords"])
    ]


# ---------------------------------------------------------------------------
# Strengths selection
# ---------------------------------------------------------------------------

def _select_strengths(jd_norm: str, jd_tokens: set[str]) -> list[str]:
    matched = [
        s["text"]
        for s in _STRENGTHS
        if _any_hit(jd_norm, jd_tokens, s["keywords"])
    ]
    if not matched:
        matched.append(
            "Applied AI systems design on Python + Next.js — David's default "
            "delivery posture regardless of domain."
        )
    return matched[:6]


# ---------------------------------------------------------------------------
# Projects selection
# ---------------------------------------------------------------------------

def _select_projects(jd_norm: str, jd_tokens: set[str]) -> list[dict]:
    scored: list[tuple[int, dict]] = []
    for p in _PROJECTS:
        hits = _count_hits(jd_norm, jd_tokens, p["keywords"])
        if hits > 0:
            scored.append((hits, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # Default: architecture + AI products as representative work
        scored = [(1, _PROJECTS[5]), (1, _PROJECTS[2]), (1, _PROJECTS[0])]

    return [{"name": p["name"], "reason": p["reason"]} for _, p in scored[:3]]


# ---------------------------------------------------------------------------
# Talking points
# ---------------------------------------------------------------------------

def _select_talking_points(jd_norm: str, jd_tokens: set[str]) -> list[str]:
    points: list[str] = []

    if _any_hit(jd_norm, jd_tokens, ["ai", "llm", "agentic", "applied ai", "ml", "rag"]):
        points.append(
            "How David designs deterministic pipelines alongside LLM and "
            "agentic components"
        )
    if _any_hit(jd_norm, jd_tokens, ["python", "fastapi", "backend", "api", "apis"]):
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
                                      "platform", "solutions", "hld",
                                      "solution design", "service design"]):
        points.append(
            "Architectural decisions on recent builds — service separation, "
            "knowledge layers, documentation artefacts, and long-term "
            "maintainability"
        )
    if _any_hit(jd_norm, jd_tokens, ["azure", "cloud", "iaas", "paas",
                                      "infrastructure", "on-prem", "hybrid",
                                      "integration", "devops", "ci/cd"]):
        points.append(
            "Cloud and infrastructure delivery — how David's production "
            "deployments (VPS, Docker, CI/CD, REST APIs) map onto the "
            "Azure / IaaS / PaaS patterns this role requires"
        )
    if _any_hit(jd_norm, jd_tokens, ["stakeholder", "stakeholder management",
                                      "client-facing", "communication",
                                      "operational", "regulated"]):
        points.append(
            "Stakeholder and operational delivery experience — Sodexo Prestige "
            "background and founder-stage accountability across technical and "
            "non-technical audiences"
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

def _overall_score(scores: dict[str, float], weights: dict[str, float]) -> int:
    """Compute overall score using role-adaptive weights.

    No blanket AI hard-cap.  If the JD doesn't ask for AI, the AI dimension
    returns 0.5 (neutral) and with a low weight it contributes negligibly.
    A soft penalty is only applied when the JD is explicitly an AI engineering
    role and David's AI signal is weak — which should never occur given his
    profile, but is preserved as a safety rail.

    Args:
        scores:  Evidence-aware dimension scores (0.0–1.0).
        weights: Role-type-specific dimension weights (must sum to ~1.0).
    """
    weighted = sum(scores[k] * weights[k] for k in weights)

    # Safety rail: only suppress score for genuine AI-role mismatches.
    # (David's AI capability is 1.0 so this should never trigger.)
    if weights.get("ai", 0) >= 0.30 and scores["ai"] < 0.2:
        weighted = min(weighted, 0.55)

    # Safety rail: both technical AND architecture near-zero = true mismatch
    if scores["technical"] < 0.15 and scores["product_arch"] < 0.15:
        weighted = min(weighted, 0.45)

    return round(max(0.0, min(weighted, 1.0)) * 100)


def _breakdown_scores(scores: dict[str, float]) -> dict[str, int]:
    """Convert evidence-aware 0–1 dimension scores to display integers 0–100.

    Uses a direct linear mapping (raw × 100) so scores communicate honestly:

        0.0  →   0  (true gap — should not occur under evidence-aware model)
        0.5  →  50  (neutral — JD doesn't ask for this dimension; amber in UI)
        0.7  →  70  (partial/inferred alignment)
        0.85 →  85  (strong direct alignment)
        1.0  → 100  (full evidence match)

    The previous mapping (50 + raw × 50) compressed scores into the 75–100
    range, making a neutral 0.5 display as 75 in green — overstating evidence
    for dimensions the JD doesn't actually require.
    """
    out: dict[str, int] = {}
    label_map = {
        "technical":    "technical",
        "ai":           "applied_ai",
        "product_arch": "product_architecture",
        "domain":       "domain",
        "seniority":    "seniority",
    }
    for key, label in label_map.items():
        raw = scores[key]
        out[label] = max(0, min(round(raw * 100), 100))
    return out


def _evidence_labels(scores: dict[str, float]) -> dict[str, str]:
    """Derive per-dimension evidence quality labels from raw 0–1 scores.

    Classification thresholds:
    - Exact 0.5:  JD didn't signal this dimension → "not_central"
    - ≥ 0.75:     Strong JD signal + high capability → "direct"
    - ≥ 0.60:     Good signal with some inference → "strong_adjacent"
    - > 0.5:      Weak JD signal → "partial_inference"
    - < 0.5:      Below neutral (rare under this model) → "partial_inference"
    """
    label_map = {
        "technical":    "technical",
        "ai":           "applied_ai",
        "product_arch": "product_architecture",
        "domain":       "domain",
        "seniority":    "seniority",
    }
    out: dict[str, str] = {}
    for key, field in label_map.items():
        raw = scores[key]
        if raw == 0.5:
            out[field] = "not_central"
        elif raw >= 0.75:
            out[field] = "direct"
        elif raw >= 0.60:
            out[field] = "strong_adjacent"
        else:
            out[field] = "partial_inference"
    return out


def _compute_confidence(
    scores: dict[str, float],
    jd_norm: str,
    jd_tokens: set[str],
    role_type: str = "general_tech",
) -> tuple[str, str]:
    """Deterministic confidence indicator based on signal coverage.

    Returns (level, reason) where level is 'high', 'medium', or 'low'.

    Neutral (0.5) scores are excluded from the "strong" count so confidence
    reflects genuine JD signal, not David's omnipresent capability floors.

    For Solution Architect roles a qualifier is appended when the technical
    dimension is below the "strong" threshold — signalling to the reader that
    cloud/infrastructure alignment is partially inferred rather than direct.
    """
    # Only count dimensions where the JD actually signalled something
    # (i.e., raw score != the neutralised 0.5 default)
    active = {k: v for k, v in scores.items() if v != 0.5}

    strong_dims = [k for k, v in active.items() if v >= 0.7]
    moderate_dims = [k for k, v in active.items() if 0.4 <= v < 0.7]

    dim_label = {
        "technical":    "technical stack",
        "ai":           "applied AI",
        "product_arch": "product and architecture",
        "domain":       "domain relevance",
        "seniority":    "seniority alignment",
    }

    # SA-specific qualifier: when tech is active but not strong, note the inference.
    # Applied only where this is genuinely the right context — don't fire on AI or
    # fullstack roles where David's tech capability IS direct evidence.
    sa_inferred_qualifier = ""
    if (
        role_type == "solution_architect"
        and "technical" in active
        and active["technical"] < 0.70
    ):
        sa_inferred_qualifier = (
            "; cloud/infrastructure experience partially inferred from "
            "adjacent delivery evidence"
        )

    token_count = len(jd_tokens)

    if len(strong_dims) >= 3 and token_count >= 30:
        top_labels = " and ".join(dim_label[d] for d in strong_dims[:3])
        return ("high", f"Based on direct evidence across {top_labels}{sa_inferred_qualifier}")

    if len(strong_dims) >= 2:
        top_labels = " and ".join(dim_label[d] for d in strong_dims[:2])
        return ("high", f"Based on direct evidence across {top_labels}{sa_inferred_qualifier}")

    if len(strong_dims) >= 1 and len(moderate_dims) >= 1:
        return (
            "medium",
            "Strong signal on core dimensions; partial or inferred alignment elsewhere",
        )

    if len(strong_dims) >= 1:
        return (
            "medium",
            f"Direct evidence on {dim_label[strong_dims[0]]}; limited coverage elsewhere",
        )

    if len(moderate_dims) >= 2:
        return ("medium", "Partial alignment across the brief — some dimensions inferred")

    if token_count < 15:
        return ("low", "Very short job description — insufficient detail for reliable scoring")

    return ("low", "Sparse signal across the brief — scoring is indicative only")


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
    """Short clause describing the role, for the opening sentence."""
    if "solutions architect" in jd_norm or "solution architect" in jd_norm:
        return "a Solution Architect role"
    if "enterprise architect" in jd_norm:
        return "an Enterprise Architect role"
    if "technical architect" in jd_norm:
        return "a Technical Architect role"
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


def _hire_signal(
    score: int,
    strengths: list[str],
    gaps: list[dict],
    role_type: str,
) -> str:
    """Closing recommendation line for the summary.

    Ordered by severity: hard gaps surface first, then soft, then risk.
    Language is recruiter-facing — avoids engineering diagnostic phrasing.
    """
    hard_gaps = [g for g in gaps if g.get("tier") == "hard"]
    soft_gaps  = [g for g in gaps if g.get("tier") == "soft"]
    risk_gaps  = [g for g in gaps if g.get("tier") == "risk"]
    first_hard = hard_gaps[0] if hard_gaps else None
    first_any  = first_hard or (soft_gaps[0] if soft_gaps else (risk_gaps[0] if risk_gaps else None))

    if score >= 80:
        if role_type == "solution_architect":
            return (
                "Strong interview candidate. Prioritise: architectural "
                "decision-making on recent builds, stakeholder communication "
                "approach, and cloud/infrastructure delivery experience."
            )
        anchor = "applied AI design and Python + Next.js delivery" if strengths else "his core delivery stack"
        return f"Strong interview candidate — lead with {anchor}."

    if score >= 65:
        if role_type == "solution_architect":
            confirm = (
                first_hard["area"].lower()
                if first_hard
                else "cloud/infrastructure delivery depth and any platform-specific requirements"
            )
            return (
                f"Good interview candidate. Focus the conversation on "
                f"architectural delivery examples and stakeholder experience. "
                f"Main area to confirm: {confirm}."
            )
        risk_desc = first_any["area"].lower() if first_any else "domain depth"
        return (
            f"Good interview candidate on core engineering. "
            f"Main area to probe: {risk_desc}."
        )

    if score >= 50:
        risk_desc = first_any["area"].lower() if first_any else "coverage of the full brief"
        return f"Partial match. Assess carefully — the primary risk is {risk_desc}."

    risk_desc = first_any["area"].lower() if first_any else "core alignment with this brief"
    return f"Weak alignment overall. The primary gap is {risk_desc} — proceed with caution."


def _build_summary(
    score: int,
    label: str,
    scores: dict[str, float],
    jd_norm: str,
    strengths: list[str],
    gaps: list[dict],
    role_type: str,
) -> str:
    role_ctx = _role_context(jd_norm)

    # --- Sentence 1: fit level + context ---
    if label == "Strong fit":
        s1 = (
            f"David is a **strong fit** for {role_ctx}. Scored at "
            f"**{score}/100**, the brief maps cleanly onto his core strengths."
        )
    elif label == "Good fit":
        s1 = (
            f"David is a **good fit** for {role_ctx}. At **{score}/100**, the "
            f"core of the brief lines up with his profile — there are one or "
            f"two areas worth probing at interview."
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

    # --- Sentence 2: strongest alignment ---
    # Exclude neutral (0.5) scores from the "strongest" display —
    # only show dimensions where the JD actually signalled something.
    active_scores = {k: v for k, v in scores.items() if v != 0.5}
    top_dims = sorted(active_scores.items(), key=lambda x: x[1], reverse=True)
    strong = [_DIM_LABEL[k] for k, v in top_dims[:2] if v >= 0.6]
    if strong:
        s2 = "The strongest alignment is on " + " and ".join(strong) + "."
    else:
        s2 = (
            "No single dimension aligns strongly with the profile — this JD "
            "sits partly outside David's core territory."
        )

    # --- Sentence 3: gaps, tiered ---
    hard_gaps = [g for g in gaps if g.get("tier") == "hard"]
    risk_gaps = [g for g in gaps if g.get("tier") in ("risk", "soft")]

    if hard_gaps:
        g = hard_gaps[0]
        s3 = f"The main concern is **{g['area']}**: {g['note']}"
    elif risk_gaps:
        g = risk_gaps[0]
        s3 = (
            f"One area worth exploring at interview is **{g['area']}**: {g['note']}"
        )
    elif role_type == "solution_architect":
        # SA roles with no hard/soft gaps still warrant a specific confirm note
        s3 = (
            "No hard gaps identified. Worth confirming at interview: "
            "hands-on cloud and infrastructure delivery experience, "
            "the expected HLD documentation standard, and any "
            "certification requirements (e.g. TOGAF, ITIL)."
        )
    else:
        s3 = (
            "No hard gaps identified from the job description. "
            "Exact tooling and team structure are worth confirming at interview."
        )

    # --- Sentence 4: hire signal ---
    s4 = _hire_signal(score, strengths, gaps, role_type)

    return f"{s1}\n\n{s2} {s3}\n\n{s4}"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

_EMPTY_EVIDENCE = {
    "technical": "not_central",
    "applied_ai": "not_central",
    "product_architecture": "not_central",
    "domain": "not_central",
    "seniority": "not_central",
}

_EMPTY_WEIGHTS = {
    "technical": 0.25,
    "applied_ai": 0.25,
    "product_architecture": 0.25,
    "domain": 0.15,
    "seniority": 0.10,
}


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
            "role_type": "general_tech",
            "dimension_weights": _EMPTY_WEIGHTS,
            "dimension_evidence": _EMPTY_EVIDENCE,
        }

    jd_norm = _normalise(job_description)
    jd_tokens = _tokenise(job_description)

    # Detect role archetype to select appropriate weights and capability scores
    role_type = _detect_role_type(jd_norm, jd_tokens)
    weights = _WEIGHTS_BY_ROLE_TYPE[role_type]
    david_tech_cap = _DAVID_TECH_CAPABILITY_BY_ROLE.get(role_type, _DAVID_CAPABILITY["technical"])
    david_domain_cap = _DAVID_DOMAIN_CAPABILITY_BY_ROLE.get(role_type, _DAVID_CAPABILITY["domain"])

    # Evidence-aware dimension scores
    scores = {
        "technical":    _dim_score_evidence_aware(jd_norm, jd_tokens, _TECHNICAL, david_tech_cap),
        "ai":           _dim_score_evidence_aware(jd_norm, jd_tokens, _AI, _DAVID_CAPABILITY["ai"]),
        "product_arch": _dim_score_evidence_aware(jd_norm, jd_tokens, _PRODUCT_ARCH, _DAVID_CAPABILITY["product_arch"]),
        "domain":       _dim_score_evidence_aware(jd_norm, jd_tokens, _DOMAIN, david_domain_cap),
        "seniority":    _dim_score_evidence_aware(jd_norm, jd_tokens, _SENIORITY, _DAVID_CAPABILITY["seniority"]),
    }

    overall = _overall_score(scores, weights)
    label = _label(overall)
    breakdown = _breakdown_scores(scores)
    evidence = _evidence_labels(scores)
    confidence, confidence_reason = _compute_confidence(scores, jd_norm, jd_tokens, role_type)

    strengths = _select_strengths(jd_norm, jd_tokens)
    gaps = _select_gaps(jd_norm, jd_tokens)
    projects = _select_projects(jd_norm, jd_tokens)
    talking_points = _select_talking_points(jd_norm, jd_tokens)

    summary = _build_summary(overall, label, scores, jd_norm, strengths, gaps, role_type)

    # Build frontend-facing dimension weights (using public-facing key names)
    dimension_weights = {
        "technical":            weights["technical"],
        "applied_ai":           weights["ai"],
        "product_architecture": weights["product_arch"],
        "domain":               weights["domain"],
        "seniority":            weights["seniority"],
    }

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
        "role_type": role_type,
        "dimension_weights": dimension_weights,
        "dimension_evidence": evidence,
    }

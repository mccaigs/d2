import re
from typing import Literal

Intent = Literal[
    "skills",
    "projects",
    "projects_overview",
    "experience",
    "experience_summary",
    "technical_stack",
    "role_fit",
    "strengths",
    "availability",
    "preferred_roles",
    "achievements",
    "engagement",
    "contact",
    "faq",
    "profile_overview",
    "capabilities",
    "engagement_preferences",
    "unknown",
]


def _normalise(message: str) -> str:
    text = re.sub(r"[^\w\s'.+-]", " ", (message or "").lower())
    return re.sub(r"\s+", " ", text).strip()


CONTACT_PHRASES: list[str] = [
    "how do i contact david",
    "how can i contact david",
    "how do i reach david",
    "how can i reach david",
    "how to contact david",
    "contact david",
    "get in touch with david",
    "get in touch",
    "reach david",
    "email david",
    "david's email",
    "davids email",
    "email address",
    "phone number",
    "mobile number",
]

PROFILE_PHRASES: list[str] = [
    "who is david",
    "tell me about david",
    "about david robertson",
    "what does david do",
    "what does he do",
    "introduce david",
    "describe david",
    "summarise david",
    "summarize david",
    "give me an overview of david",
    "overview of david",
]

STACK_PHRASES: list[str] = [
    "what stack does david use",
    "what stack does he use",
    "what tech stack does david use",
    "what tech stack does he use",
    "what is david's technical stack",
    "what is his technical stack",
    "what tools does david use",
    "what technologies does david use",
]

PROJECT_OVERVIEW_PHRASES: list[str] = [
    "what has david built",
    "what has he built",
    "what has david made",
    "what has he made",
    "what has david created",
    "what has he created",
    "what has david shipped",
    "what projects has david built",
    "what projects has he built",
    "what has david actually built",
    "what has he actually built",
]

EXPERIENCE_SUMMARY_PHRASES: list[str] = [
    "summarise his experience",
    "summarize his experience",
    "summarise david's experience",
    "summarize david's experience",
    "experience summary",
    "career summary",
    "walk me through david's background",
]

CAPABILITY_PHRASES: list[str] = [
    "what can david do",
    "what can he do",
    "what is david capable of",
    "what is he capable of",
    "what can david help with",
    "what capabilities does david have",
    "what capabilities does he have",
]

ENGAGEMENT_PREFERENCE_PHRASES: list[str] = [
    "what roles is he open to",
    "what roles is david open to",
    "what role is he open to",
    "what kind of work is he open to",
    "what types of work is he open to",
    "what types of work does david take on",
    "what is david open to",
    "what are david's day rates",
    "what is david's day rate",
    "what's david's day rate",
    "what's david's pricing",
    "what is david's pricing",
    "what are his rates",
]

GOOD_FIT_PHRASES: list[str] = [
    "what would make this a good project for david",
    "what kinds of work is david best suited to",
    "what kind of work is david best suited to",
    "is this the sort of project david would be good for",
    "what makes a good project for david",
    "what sort of role suits david",
    "what type of project suits david",
    "would david be a good fit",
    "is david right for this",
    "what is david best at",
    "where does david add the most value",
    "what work suits david best",
]

HIGH_INTENT_PHRASES: list[str] = [
    "hire david",
    "work with david",
    "working with david",
    "discuss a project",
    "start a project",
    "help us build",
    "build this for us",
    "can david help us",
    "get david involved",
    "speak to david",
    "talk to david",
    "engage david",
    "bring david in",
    "get in touch",
    "contact david",
]

# Tokens that signal genuine commercial / hire intent.
# Deliberately excludes broad terms like "project" or "budget" that
# appear in exploratory questions without real hiring signal.
HIGH_INTENT_TOKENS: list[str] = [
    "hire",
    "pricing",
    "rates",
    "quote",
    "contact",
    "engage",
]

PHRASE_OVERRIDES: list[tuple[str, list[str]]] = [
    ("contact", CONTACT_PHRASES),
    ("experience_summary", EXPERIENCE_SUMMARY_PHRASES),
    ("profile_overview", PROFILE_PHRASES),
    ("technical_stack", STACK_PHRASES),
    ("projects_overview", PROJECT_OVERVIEW_PHRASES),
    ("capabilities", CAPABILITY_PHRASES),
    ("engagement_preferences", ENGAGEMENT_PREFERENCE_PHRASES),
    ("role_fit", GOOD_FIT_PHRASES),
]

KEYWORD_MAP: dict[Intent, list[str]] = {
    "skills": [
        "skill",
        "skills",
        "know",
        "language",
        "framework",
        "technology",
        "technologies",
        "proficient",
        "familiar",
        "expertise",
        "python",
        "typescript",
        "fastapi",
        "next.js",
        "nextjs",
        "react",
    ],
    "technical_stack": [
        "stack",
        "tech stack",
        "technical stack",
        "tooling",
        "backend",
        "frontend",
        "infrastructure",
        "architecture stack",
        "built with",
        "build with",
        "technology",
        "technologies",
    ],
    "projects_overview": [
        "built",
        "shipped",
        "created",
        "developed",
        "made",
        "projects",
        "systems",
        "products",
    ],
    "projects": [
        "careersai",
        "recruitersai",
        "interviewsai",
        "studentlyai",
        "jobs pipeline",
        "project",
        "platform",
        "app",
        "application",
    ],
    "experience_summary": [
        "background",
        "career",
        "history",
        "experience",
        "summary",
        "worked",
        "professional",
        "roles",
    ],
    "experience": [
        "industry",
        "domain",
        "sector",
        "years",
        "employed",
        "career history",
    ],
    "strengths": [
        "strong",
        "strength",
        "strongest",
        "best at",
        "good at",
        "excel",
        "excellent",
        "specialise",
        "specialize",
        "expert",
    ],
    "role_fit": [
        "fit",
        "suit",
        "suited",
        "suitable",
        "match",
        "good fit",
        "right for",
        "candidate",
        "job description",
        "jd",
    ],
    "preferred_roles": [
        "preferred role",
        "preferred roles",
        "ideal role",
        "ideal roles",
        "target role",
        "target roles",
    ],
    "availability": [
        "available",
        "availability",
        "start",
        "starting",
        "notice",
    ],
    "achievements": [
        "achievement",
        "achievements",
        "accomplished",
        "award",
        "won",
        "milestone",
    ],
    "engagement": [
        "freelance",
        "contract",
        "contracting",
        "consulting",
        "consultancy",
        "mvp",
        "mvp build",
        "short project",
        "short-term",
        "advisory",
        "engagement",
    ],
    "faq": [
        "different",
        "unique",
        "why david",
        "why hire",
        "what makes",
        "full stack",
        "full-stack",
        "production",
    ],
    "profile_overview": [
        "overview",
        "profile",
        "who",
        "about",
        "summary",
        "introduce",
        "describe",
    ],
    "capabilities": [
        "capable",
        "capability",
        "capabilities",
        "competencies",
        "offer",
        "services",
        "deliver",
        "help with",
    ],
    "engagement_preferences": [
        "open to",
        "types of work",
        "kind of work",
        "day rate",
        "day rates",
        "rates",
        "pricing",
        "salary",
        "full-time",
        "full time",
        "permanent",
        "remote",
        "hybrid",
        "budget",
    ],
}


def classify(message: str) -> Intent:
    text = _normalise(message)
    if not text:
        return "unknown"

    for intent, phrases in PHRASE_OVERRIDES:
        if any(phrase in text for phrase in phrases):
            return intent  # type: ignore[return-value]

    scores: dict[Intent, int] = {intent: 0 for intent in KEYWORD_MAP}
    for intent, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in text:
                scores[intent] += 1

    best_intent = max(scores, key=lambda item: scores[item])
    if scores[best_intent] == 0:
        return "unknown"

    return best_intent


def has_high_intent(message: str) -> bool:
    text = _normalise(message)
    if any(phrase in text for phrase in HIGH_INTENT_PHRASES):
        return True
    return any(token in text for token in HIGH_INTENT_TOKENS)

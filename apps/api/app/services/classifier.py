import re
from typing import Literal

Intent = Literal[
    "capabilities",
    "technical_stack",
    "workflows",
    "workflows_overview",
    "procurement_examples",
    "procurement_summary",
    "strengths",
    "role_fit",
    "preferred_roles",
    "availability",
    "proof_points",
    "engagement",
    "contact",
    "faq",
    "profile_overview",
    "engagement_preferences",
    "unknown",
]


def _normalise(message: str) -> str:
    text = re.sub(r"[^\w\s'.+-]", " ", (message or "").lower())
    return re.sub(r"\s+", " ", text).strip()


CONTACT_PHRASES: list[str] = [
    "how do i contact bidworx",
    "contact bidworx",
    "get in touch",
    "book a demo",
    "speak to the team",
]

PROFILE_PHRASES: list[str] = [
    "what is bidworx",
    "tell me about bidworx",
    "what does bidworx do",
    "summarise bidworx",
    "summarize bidworx",
    "give me an overview",
]

STACK_PHRASES: list[str] = [
    "how is bidworx built",
    "what architecture does bidworx use",
    "what is the technical stack",
    "what stack does bidworx use",
]

WORKFLOW_OVERVIEW_PHRASES: list[str] = [
    "what does bidworx analyse",
    "what can bidworx analyse",
    "what workflows does bidworx support",
    "tender intelligence workflow",
]

PROCUREMENT_SUMMARY_PHRASES: list[str] = [
    "summarise the buyer requirements",
    "summarize the buyer requirements",
    "summarise this tender",
    "summarize this tender",
    "what does the buyer need",
    "buyer requirements",
]

CAPABILITY_PHRASES: list[str] = [
    "what can bidworx do",
    "what capabilities does bidworx have",
    "what evidence do we need",
    "what evidence supports this claim",
    "what proof do we need",
]

COMPLIANCE_PHRASES: list[str] = [
    "what are the compliance risks",
    "likely compliance risks",
    "submission requirements",
    "missing submission requirements",
    "mandatory requirements",
    "pass fail",
    "pass/fail",
]

SCORING_PHRASES: list[str] = [
    "score this opportunity",
    "score this tender",
    "bid readiness",
    "go no go",
    "go/no-go",
    "is this opportunity worth pursuing",
    "analyse this tender opportunity",
    "analyze this tender opportunity",
]

HIGH_INTENT_PHRASES: list[str] = [
    "analyse this tender",
    "analyze this tender",
    "score this opportunity",
    "check this submission",
    "review this tender",
    "book a demo",
]

HIGH_INTENT_TOKENS: list[str] = [
    "analyse",
    "analyze",
    "score",
    "review",
    "demo",
    "contact",
]

PHRASE_OVERRIDES: list[tuple[str, list[str]]] = [
    ("contact", CONTACT_PHRASES),
    ("profile_overview", PROFILE_PHRASES),
    ("technical_stack", STACK_PHRASES),
    ("workflows_overview", WORKFLOW_OVERVIEW_PHRASES),
    ("procurement_summary", PROCUREMENT_SUMMARY_PHRASES),
    ("capabilities", CAPABILITY_PHRASES),
    ("procurement_examples", COMPLIANCE_PHRASES),
    ("role_fit", SCORING_PHRASES),
]

KEYWORD_MAP: dict[Intent, list[str]] = {
    "capabilities": [
        "capability",
        "capabilities",
        "evidence",
        "proof",
        "claim",
        "claims",
        "source",
        "support",
    ],
    "technical_stack": [
        "stack",
        "architecture",
        "fastapi",
        "pydantic",
        "next.js",
        "structured json",
        "streaming",
        "deterministic",
    ],
    "workflows_overview": [
        "analyse",
        "analyze",
        "workflow",
        "workflows",
        "tender",
        "rfp",
        "bid",
        "framework",
    ],
    "workflows": [
        "triage",
        "coverage",
        "submission",
        "review",
        "evidence map",
        "compliance check",
    ],
    "procurement_summary": [
        "buyer",
        "requirements",
        "summarise",
        "summarize",
        "needs",
        "instructions",
    ],
    "procurement_examples": [
        "compliance",
        "risk",
        "risks",
        "mandatory",
        "missing",
        "attachment",
        "declaration",
        "policy",
    ],
    "strengths": [
        "strong",
        "strength",
        "best",
        "different",
        "trust",
        "reliable",
    ],
    "role_fit": [
        "score",
        "scoring",
        "readiness",
        "opportunity",
        "go/no-go",
        "fit",
        "worth",
    ],
    "preferred_roles": [
        "buyer role",
        "buyer roles",
        "procurement role",
        "evaluator",
        "category manager",
    ],
    "availability": [
        "available",
        "start",
        "use",
        "when should",
    ],
    "proof_points": [
        "proof point",
        "proof points",
        "source chip",
        "evidence backed",
        "supported claim",
    ],
    "engagement": [
        "demo",
        "pilot",
        "implementation",
        "setup",
        "pricing",
        "package",
    ],
    "faq": [
        "why",
        "how",
        "unsupported",
        "hallucinate",
        "llm",
    ],
    "profile_overview": [
        "overview",
        "about",
        "bidworx",
        "product",
        "platform",
    ],
    "engagement_preferences": [
        "use case",
        "team",
        "teams",
        "proposal",
        "bid team",
        "capture",
    ],
    "contact": [
        "contact",
        "demo",
        "speak",
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

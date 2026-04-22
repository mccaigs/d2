from typing import Literal

Intent = Literal[
    "skills",
    "projects",
    "experience",
    "technical_stack",
    "role_fit",
    "strengths",
    "availability",
    "preferred_roles",
    "achievements",
    "engagement",
    "contact",
    "faq",
    "unknown",
]

# Phrase-level matches for high-intent contact / hiring-conversion signals.
# If any of these appear in the query, we return `contact` immediately so
# generic keyword scoring cannot out-vote a clear lead-capture signal.
CONTACT_PHRASES: list[str] = [
    # direct contact capture
    "contact david", "contact details", "how do i contact",
    "how can i contact", "how to contact", "how do i reach",
    "how can i reach", "reach david", "get in touch", "in touch with david",
    "email david", "david's email", "davids email", "email address",
    "phone number", "mobile number",
    # hiring / engagement conversion
    "hire david", "work with david", "working with david",
    "start a project", "discuss a project", "discuss the project",
    "can we work together", "help us build", "build this for us",
    "can david help us", "david help us build",
    # rates / pricing / commercial
    "david's rates", "davids rates", "his rates", "day rate", "day rates",
    "day-rate", "what are the rates", "pricing", "price list", "quote",
    "budget for", "availability for project",
]

# Single-token high-intent signals used both to disambiguate engagement
# queries and to decide whether to show the contact-form CTA.
HIGH_INTENT_TOKENS: list[str] = [
    "hire", "rates", "pricing", "quote", "budget",
    "contact", "discuss",
]

KEYWORD_MAP: dict[Intent, list[str]] = {
    "skills": [
        "skill", "skills", "know", "language", "framework", "technology",
        "technologies", "proficient", "familiar", "expertise", "capable",
        "python", "typescript", "next.js", "nextjs", "fastapi", "tailwind",
        "convex", "clerk", "stripe", "react",
    ],
    "technical_stack": [
        "stack", "tech stack", "tooling", "backend", "frontend",
        "database", "infrastructure", "architecture stack",
        "built with", "build with", "technologies", "technology",
        "uses for", "use for",
    ],
    "projects": [
        "project", "projects", "built", "build", "created",
        "developed", "careersai", "recruitersai", "interviewsai", "uk jobs",
        "ai jobs", "ai ide", "product", "platform", "system", "app",
        "application",
    ],
    "experience": [
        "experience", "background", "career", "history", "worked",
        "work", "professional", "industry", "domain", "sector", "years",
        "role", "position", "job", "employed",
    ],
    "strengths": [
        "strong", "strength", "strongest", "best at", "good at",
        "excel", "excellent", "specialise", "specialize", "expert",
        "leading", "notable",
    ],
    "role_fit": [
        "fit", "suit", "suited", "suitable", "match", "good fit", "right for",
        "would david", "can david", "right candidate",
        "job description", "jd",
    ],
    "preferred_roles": [
        "preferred role", "preferred roles", "looking for", "wants",
        "open to", "interest", "interested in", "target role", "ideal role",
        "seeking", "available for",
    ],
    "availability": [
        "available", "availability", "start", "starting", "when",
        "notice", "permanent", "remote", "hybrid", "onsite", "relocate",
    ],
    "achievements": [
        "achievement", "achievements", "accomplished", "award", "won",
        "delivered", "proud", "notable", "highlight", "milestone",
    ],
    "engagement": [
        "hire", "hired", "hire him",
        "short project", "short projects", "small project",
        "freelance", "contract", "contracting", "consulting", "consultancy",
        "mvp build", "mvp", "short-term", "short term",
        "ad hoc", "ad-hoc", "engagement", "engage david",
        "advisory", "one-off", "one off",
    ],
    "faq": [
        "different", "unique", "why david", "why hire", "what makes",
        "full stack", "fullstack", "full-stack", "production",
    ],
}


def classify(message: str) -> Intent:
    text = message.lower()

    # High-priority phrase override: strong commercial / contact signals
    # should always route to the contact intent regardless of noise elsewhere.
    for phrase in CONTACT_PHRASES:
        if phrase in text:
            return "contact"

    scores: dict[Intent, int] = {intent: 0 for intent in KEYWORD_MAP}

    for intent, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in text:
                scores[intent] += 1

    best_intent = max(scores, key=lambda i: scores[i])
    if scores[best_intent] == 0:
        return "unknown"

    return best_intent


def has_high_intent(message: str) -> bool:
    """True when the query contains clear commercial / conversion signals.

    Used by the chat route to decide whether to surface the contact-form CTA
    for `engagement` intents that sit adjacent to a direct contact request.
    """
    text = message.lower()
    if any(phrase in text for phrase in CONTACT_PHRASES):
        return True
    return any(tok in text for tok in HIGH_INTENT_TOKENS)

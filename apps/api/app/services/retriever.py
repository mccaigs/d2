import json
import re
from pathlib import Path
from typing import Any

from app.models.chat import SourceChip
from app.services.classifier import Intent

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load(filename: str) -> Any:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


_product_cache: dict[str, Any] | None = None


def _load_product() -> dict[str, Any]:
    global _product_cache
    if _product_cache is None:
        _product_cache = _load("product.json")
    return _product_cache


def get_profile_summary() -> dict[str, Any]:
    product = _load_product()
    return {
        "name": product.get("name", ""),
        "title": product.get("headline", ""),
        "location": product.get("location", ""),
        "profile": product.get("summary", ""),
        "capabilities": product.get("core_strengths", []),
    }


def get_capabilities() -> dict[str, Any]:
    product = _load_product()
    caps = _load("capabilities.json")
    return {
        "capabilities": [item.get("name", "") for item in caps.get("capabilities", [])],
        "core_skills": product.get("core_strengths", []),
        "key_systems": [item.get("name", "") for item in _load("workflows.json").get("workflows", [])],
    }


def get_core_skills() -> list[str]:
    return _load_product().get("core_strengths", [])


def get_tech_stack() -> dict[str, Any]:
    return {
        "backend": ["FastAPI", "Pydantic models", "deterministic services"],
        "frontend": ["Next.js", "TypeScript", "streaming response UX"],
        "data": ["structured JSON knowledge", "evidence categories", "scoring rules"],
        "trust": ["scoped refusals", "source chips", "approved evidence only"],
    }


def get_experience() -> list[dict[str, Any]]:
    return _load("procurement_examples.json").get("examples", [])


def get_projects() -> list[dict[str, Any]]:
    return _load("workflows.json").get("workflows", [])


def get_engagement_preferences() -> dict[str, Any]:
    product = _load_product()
    return {
        "work_type": [item.get("type", "") for item in product.get("engagement_options", [])],
        "location": ["Procurement teams", "Bid teams", "Framework and tender workflows"],
        "rates": {},
        "full_time_preferences": {"ideal_roles": product.get("preferred_roles", [])},
        "focus": product.get("availability_summary", ""),
    }


_SYNONYM_GROUPS: list[list[str]] = [
    ["tender", "rfp", "bid", "opportunity", "call-off", "framework"],
    ["buyer", "authority", "client", "evaluator", "procurement"],
    ["evidence", "proof", "source", "support", "claim"],
    ["compliance", "mandatory", "pass/fail", "submission", "attachment"],
    ["score", "scoring", "readiness", "fit", "go/no-go"],
    ["risk", "gap", "missing", "unsupported"],
    ["workflow", "process", "analysis", "review"],
]

_SYNONYM_MAP: dict[str, set[str]] = {}
for group in _SYNONYM_GROUPS:
    expanded = set(group)
    for term in group:
        _SYNONYM_MAP[term] = expanded

_BOOST_PHRASES: list[tuple[str, float]] = [
    ("buyer requirements", 4.0),
    ("compliance risks", 4.0),
    ("submission requirements", 4.0),
    ("evidence backed", 3.5),
    ("unsupported claims", 3.5),
    ("bid readiness", 3.5),
    ("score this opportunity", 3.0),
    ("analyse this tender", 3.0),
    ("analyze this tender", 3.0),
]

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "has", "have", "had", "will", "would", "can", "could",
    "should", "may", "might", "of", "in", "on", "at", "to", "for", "with",
    "and", "or", "but", "if", "as", "by", "from", "that", "this", "these",
    "those", "it", "its", "they", "them", "their", "what", "when", "where",
    "which", "who", "why", "how", "about", "some", "any", "all", "me", "you",
    "your", "i", "we", "our", "bidworx",
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenise(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s\-\/\.]", " ", text)
    return [t for t in text.split() if len(t) > 1]


def _content_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in _STOPWORDS]


def _expand_tokens(tokens: list[str]) -> set[str]:
    expanded: set[str] = set(tokens)
    for token in tokens:
        if token in _SYNONYM_MAP:
            expanded |= _SYNONYM_MAP[token]
    return expanded


def _active_phrases(query_norm: str) -> list[tuple[str, float]]:
    return [(p, w) for p, w in _BOOST_PHRASES if p in query_norm]


def _score_text(
    query_tokens: set[str],
    text: str,
    phrases: list[tuple[str, float]] | None = None,
) -> float:
    if not text:
        return 0.0
    norm = _normalise(text)
    score = 0.0
    if query_tokens:
        text_tokens = set(_tokenise(norm))
        hits = query_tokens & text_tokens
        if hits:
            score += len(hits) / max(len(query_tokens), 1)
    if phrases:
        for phrase, weight in phrases:
            if phrase in norm:
                score += weight
    return score


def _score_record(query_tokens: set[str], phrases: list[tuple[str, float]], item: dict) -> float:
    score = 0.0
    for key, weight in [
        ("name", 3.5),
        ("title", 3.0),
        ("type", 1.5),
        ("category", 1.5),
        ("summary", 2.0),
        ("description", 2.0),
        ("notes", 1.5),
    ]:
        score += _score_text(query_tokens, str(item.get(key, "")), phrases) * weight
    for list_key in ["themes", "tech", "highlights"]:
        for value in item.get(list_key, []):
            score += _score_text(query_tokens, value, phrases) * 1.5
    return score


def _rank(items: list[dict], scorer, n: int | None = None) -> list[dict]:
    scored = [(scorer(item), item) for item in items]
    positive = [item for s, item in sorted(scored, key=lambda x: x[0], reverse=True) if s > 0]
    if positive:
        return positive[:n] if n else positive
    return items[:n] if n else items


def _prepare_query(message: str) -> tuple[set[str], list[tuple[str, float]]]:
    norm = _normalise(message)
    tokens = _tokenise(norm)
    content = _content_tokens(tokens)
    expanded = _expand_tokens(content) if content else set()
    phrases = _active_phrases(norm)
    return expanded, phrases


def retrieve(intent: Intent, message: str) -> tuple[dict[str, Any], list[SourceChip]]:
    sources: list[SourceChip] = []
    data: dict[str, Any] = {}

    query_tokens, phrases = _prepare_query(message)
    has_query = bool(query_tokens or phrases)

    if intent == "capabilities":
        raw = _load("capabilities.json")
        caps = raw.get("capabilities", [])
        data["capabilities"] = _rank(caps, lambda s: _score_record(query_tokens, phrases, s)) if has_query else caps
        data["working_style"] = raw.get("working_style", [])
        sources.append(SourceChip(label="Capabilities", category="capabilities"))

    elif intent == "technical_stack":
        data["tech_stack"] = get_tech_stack()
        data["core_skills"] = get_core_skills()
        sources.append(SourceChip(label="Architecture", category="architecture"))

    elif intent == "workflows":
        raw = _load("workflows.json")
        workflows = raw.get("workflows", [])
        data["workflows"] = _rank(workflows, lambda p: _score_record(query_tokens, phrases, p), n=5)
        sources.append(SourceChip(label="Workflows", category="workflows"))

    elif intent == "workflows_overview":
        data["workflows"] = get_projects()
        data["scoring_rules"] = _load("scoring_rules.json").get("dimensions", [])
        data["evidence_categories"] = _load("evidence_categories.json").get("categories", [])
        sources.append(SourceChip(label="Tender Intelligence Workflow", category="workflows"))

    elif intent == "procurement_examples":
        raw = _load("procurement_examples.json")
        data["experience"] = raw.get("examples", [])
        data["capabilities"] = raw.get("capabilities", [])
        data["industries"] = raw.get("industries_or_domains", [])
        data["compliance_rules"] = _load("compliance_rules.json").get("rules", [])
        sources.append(SourceChip(label="Compliance Rules", category="compliance"))

    elif intent == "procurement_summary":
        data["experience"] = get_experience()
        data["capabilities"] = _load("procurement_examples.json").get("capabilities", [])
        data["workflows"] = get_projects()
        sources.append(SourceChip(label="Buyer Requirements", category="procurement"))

    elif intent == "strengths":
        product = _load_product()
        caps = _load("capabilities.json")
        data["core_strengths"] = product.get("core_strengths", [])
        data["working_style"] = caps.get("working_style", [])
        sources.append(SourceChip(label="Product Principles", category="product"))

    elif intent == "role_fit":
        product = _load_product()
        data["positioning"] = product.get("positioning", [])
        data["preferred_roles"] = product.get("preferred_roles", [])
        data["relevant_job_titles"] = _load("buyer_roles.json").get("buyer_roles", [])
        data["capabilities"] = _load("procurement_examples.json").get("capabilities", [])
        data["key_systems"] = [w.get("name", "") for w in get_projects()]
        data["projects"] = get_projects()
        data["engagement_focus"] = product.get("availability_summary", "")
        data["scoring_rules"] = _load("scoring_rules.json").get("dimensions", [])
        sources.append(SourceChip(label="Scoring Rules", category="scoring"))
        sources.append(SourceChip(label="Buyer Roles", category="procurement"))

    elif intent == "preferred_roles":
        product = _load_product()
        data["preferred_roles"] = product.get("preferred_roles", [])
        data["relevant_job_titles"] = _load("buyer_roles.json").get("buyer_roles", [])
        data["availability_summary"] = product.get("availability_summary", "")
        sources.append(SourceChip(label="Buyer Roles", category="procurement"))

    elif intent == "availability":
        product = _load_product()
        data["availability_summary"] = product.get("availability_summary", "")
        data["contact_cta"] = product.get("contact_cta", "")
        sources.append(SourceChip(label="Use Cases", category="product"))

    elif intent == "engagement":
        product = _load_product()
        data["engagement_options"] = product.get("engagement_options", [])
        data["custom_services"] = product.get("custom_services", [])
        data["pricing_notes"] = product.get("pricing_notes", "")
        data["stack_highlight"] = product.get("stack_highlight", "")
        data["availability_summary"] = product.get("availability_summary", "")
        data["contact_cta"] = product.get("contact_cta", "")
        sources.append(SourceChip(label="Operational Use Cases", category="product"))

    elif intent == "proof_points":
        raw = _load("proof_points.json")
        data["achievements"] = raw.get("proof_points", [])
        sources.append(SourceChip(label="Proof Points", category="proof"))

    elif intent == "faq":
        raw = _load("faqs.json")
        faqs = raw.get("faqs", [])
        data["faqs"] = _rank(faqs, lambda f: _score_record(query_tokens, phrases, f), n=3)
        sources.append(SourceChip(label="FAQ", category="faq"))

    elif intent == "profile_overview":
        profile_data = get_profile_summary()
        prefs = get_engagement_preferences()
        data["name"] = profile_data["name"]
        data["title"] = profile_data["title"]
        data["location"] = profile_data["location"]
        data["profile"] = profile_data["profile"]
        data["capabilities"] = profile_data["capabilities"]
        data["core_skills"] = get_core_skills()
        data["ideal_roles"] = prefs.get("full_time_preferences", {}).get("ideal_roles", [])
        data["focus"] = prefs.get("focus", "")
        sources.append(SourceChip(label="Product Overview", category="product"))

    elif intent == "engagement_preferences":
        prefs = get_engagement_preferences()
        data["work_type"] = prefs.get("work_type", [])
        data["location"] = prefs.get("location", [])
        data["rates"] = prefs.get("rates", {})
        data["full_time_preferences"] = prefs.get("full_time_preferences", {})
        data["focus"] = prefs.get("focus", "")
        data["availability_summary"] = _load_product().get("contact_cta", "")
        sources.append(SourceChip(label="Bid Team Use Cases", category="product"))

    elif intent == "contact":
        product = _load_product()
        data["availability"] = product.get("contact_cta", "")
        data["focus"] = product.get("availability_summary", "")
        sources.append(SourceChip(label="Next Step", category="product"))

    return data, sources

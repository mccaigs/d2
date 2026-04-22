import json
import re
from pathlib import Path
from typing import Any

from app.models.chat import SourceChip
from app.services.classifier import Intent

_DATA_DIR = Path(__file__).parent.parent / "data"

# ---------------------------------------------------------------------------
# Synonym groups — any token in a group is treated as equivalent to all others
# ---------------------------------------------------------------------------
_SYNONYM_GROUPS: list[list[str]] = [
    ["recruiter", "recruiters", "hiring", "recruitment", "talent"],
    ["ai", "llm", "agentic", "agent", "gpt", "ml"],
    ["frontend", "nextjs", "react", "ui"],
    ["backend", "python", "fastapi", "server", "api"],
    ["architecture", "systems", "platform", "infrastructure"],
    ["saas", "product", "startup"],
    ["automation", "pipeline", "workflow", "workflows"],
    ["fullstack", "end-to-end"],
    ["built", "build", "builds", "building", "created", "made", "developed", "ship", "shipped"],
    ["role", "roles", "position", "job"],
    ["suit", "suited", "suitable", "fit", "match"],
]

_SYNONYM_MAP: dict[str, set[str]] = {}
for group in _SYNONYM_GROUPS:
    expanded = set(group)
    for term in group:
        _SYNONYM_MAP[term] = expanded

# ---------------------------------------------------------------------------
# Multi-word phrases that should get strong boosts when present in the query
# ---------------------------------------------------------------------------
_BOOST_PHRASES: list[tuple[str, float]] = [
    ("solutions architect", 4.0),
    ("solution architect", 4.0),
    ("applied ai", 3.5),
    ("full stack", 3.0),
    ("full-stack", 3.0),
    ("fullstack", 3.0),
    ("next.js", 3.0),
    ("nextjs", 3.0),
    ("fastapi", 3.0),
    ("job fit", 3.0),
    ("recruiter tools", 4.0),
    ("recruitment tools", 4.0),
    ("ai product", 2.5),
    ("ai products", 2.5),
    ("ai systems", 2.5),
    ("ai engineer", 2.5),
    ("systems architect", 3.0),
    ("product engineer", 2.5),
    ("workflow automation", 2.5),
    ("typescript", 2.0),
    ("python", 2.0),
    ("react", 1.5),
]

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "has", "have", "had", "will", "would", "can", "could",
    "should", "may", "might", "of", "in", "on", "at", "to", "for", "with",
    "and", "or", "but", "if", "as", "by", "from", "that", "this", "these",
    "those", "it", "its", "he", "she", "they", "them", "his", "her", "their",
    "what", "when", "where", "which", "who", "why", "how",
    "about", "some", "any", "all", "me", "you", "your", "i", "we", "our",
    "david", "robertson",
}


def _load(filename: str) -> Any:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenise(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into tokens."""
    text = text.lower()
    text = re.sub(r"[^\w\s\-\.]", " ", text)
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
    """Return boost phrases that appear in the query, plus their weight."""
    return [(p, w) for p, w in _BOOST_PHRASES if p in query_norm]


def _score_text(
    query_tokens: set[str],
    text: str,
    phrases: list[tuple[str, float]] | None = None,
) -> float:
    """Token overlap + phrase substring boosts.

    Token score: overlap / total-query-tokens (so specific queries are harder
    to max out and prioritise breadth of match).
    Phrase score: additive per matching multi-word phrase.
    """
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


def _score_project(
    query_tokens: set[str],
    phrases: list[tuple[str, float]],
    project: dict,
) -> float:
    score = 0.0
    score += _score_text(query_tokens, project.get("name", ""), phrases) * 3.5
    score += _score_text(query_tokens, project.get("type", ""), phrases) * 1.5
    score += _score_text(query_tokens, project.get("summary", ""), phrases) * 2.0
    for theme in project.get("themes", []):
        score += _score_text(query_tokens, theme, phrases) * 2.0
    for tech in project.get("tech", []):
        score += _score_text(query_tokens, tech, phrases) * 2.0
    for highlight in project.get("highlights", []):
        score += _score_text(query_tokens, highlight, phrases) * 1.2
    return score


def _score_skill(
    query_tokens: set[str],
    phrases: list[tuple[str, float]],
    skill: dict,
) -> float:
    score = 0.0
    score += _score_text(query_tokens, skill.get("name", ""), phrases) * 3.5
    score += _score_text(query_tokens, skill.get("category", ""), phrases) * 1.5
    score += _score_text(query_tokens, skill.get("notes", ""), phrases) * 1.0
    return score


def _score_faq(
    query_tokens: set[str],
    phrases: list[tuple[str, float]],
    faq: dict,
) -> float:
    score = 0.0
    score += _score_text(query_tokens, faq.get("question", ""), phrases) * 3.5
    score += _score_text(query_tokens, faq.get("answer", ""), phrases) * 2.0
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
    """Return structured data records and source chips for a given intent."""

    sources: list[SourceChip] = []
    data: dict[str, Any] = {}

    query_tokens, phrases = _prepare_query(message)
    has_query = bool(query_tokens or phrases)

    if intent == "skills":
        raw = _load("skills.json")
        skills = raw.get("technical_skills", [])
        style = raw.get("working_style", [])
        if has_query:
            data["technical_skills"] = _rank(skills, lambda s: _score_skill(query_tokens, phrases, s))
        else:
            data["technical_skills"] = skills
        data["working_style"] = style
        sources.append(SourceChip(label="Skills", category="skills"))

    elif intent == "technical_stack":
        raw = _load("skills.json")
        data["technical_skills"] = raw.get("technical_skills", [])
        sources.append(SourceChip(label="Technical Stack", category="skills"))

    elif intent == "projects":
        raw = _load("projects.json")
        projects = raw.get("projects", [])
        data["projects"] = _rank(
            projects,
            lambda p: _score_project(query_tokens, phrases, p),
            n=5,
        )
        sources.append(SourceChip(label="Projects", category="projects"))

    elif intent == "experience":
        raw = _load("experience.json")
        data["experience"] = raw.get("experience", [])
        data["capabilities"] = raw.get("capabilities", [])
        data["industries"] = raw.get("industries_or_domains", [])
        sources.append(SourceChip(label="Experience", category="experience"))

    elif intent == "strengths":
        profile = _load("profile.json")
        skills = _load("skills.json")
        data["core_strengths"] = profile.get("core_strengths", [])
        data["working_style"] = skills.get("working_style", [])
        sources.append(SourceChip(label="Strengths", category="profile"))

    elif intent == "role_fit":
        profile = _load("profile.json")
        job_titles = _load("job_titles.json")
        experience = _load("experience.json")
        data["positioning"] = profile.get("positioning", [])
        data["preferred_roles"] = profile.get("preferred_roles", [])
        titles = job_titles.get("relevant_job_titles", [])
        # If the query mentions a specific role, surface most relevant titles first
        if has_query:
            titles = sorted(
                titles,
                key=lambda t: _score_text(query_tokens, t, phrases),
                reverse=True,
            )
        data["relevant_job_titles"] = titles
        data["capabilities"] = experience.get("capabilities", [])
        sources.append(SourceChip(label="Role Fit", category="profile"))
        sources.append(SourceChip(label="Preferred Roles", category="profile"))

    elif intent == "preferred_roles":
        profile = _load("profile.json")
        job_titles = _load("job_titles.json")
        data["preferred_roles"] = profile.get("preferred_roles", [])
        data["relevant_job_titles"] = job_titles.get("relevant_job_titles", [])
        data["availability_summary"] = profile.get("availability_summary", "")
        sources.append(SourceChip(label="Preferred Roles", category="profile"))

    elif intent == "availability":
        profile = _load("profile.json")
        data["availability_summary"] = profile.get("availability_summary", "")
        data["contact_cta"] = profile.get("contact_cta", "")
        sources.append(SourceChip(label="Availability", category="profile"))

    elif intent == "engagement":
        profile = _load("profile.json")
        data["engagement_options"] = profile.get("engagement_options", [])
        data["custom_services"] = profile.get("custom_services", [])
        data["pricing_notes"] = profile.get("pricing_notes", "")
        data["stack_highlight"] = profile.get("stack_highlight", "")
        data["availability_summary"] = profile.get("availability_summary", "")
        data["contact_cta"] = profile.get("contact_cta", "")
        sources.append(SourceChip(label="Engagement Options", category="profile"))

    elif intent == "contact":
        profile = _load("profile.json")
        projects_raw = _load("projects.json").get("projects", [])
        data["custom_services"] = profile.get("custom_services", [])
        data["engagement_options"] = profile.get("engagement_options", [])
        data["pricing_notes"] = profile.get("pricing_notes", "")
        data["stack_highlight"] = profile.get("stack_highlight", "")
        data["contact_cta"] = profile.get("contact_cta", "")
        data["availability_summary"] = profile.get("availability_summary", "")
        # Surface the strongest named proof for the conversion answer. Rank
        # by query relevance so a query like "help us build recruiter tools"
        # still surfaces the most relevant projects first.
        if has_query:
            data["projects"] = _rank(
                projects_raw,
                lambda p: _score_project(query_tokens, phrases, p),
                n=3,
            )
        else:
            data["projects"] = projects_raw[:3]
        sources.append(SourceChip(label="Engagement & Pricing", category="profile"))
        sources.append(SourceChip(label="Projects", category="projects"))

    elif intent == "achievements":
        raw = _load("achievements.json")
        data["achievements"] = raw.get("achievements", [])
        sources.append(SourceChip(label="Achievements", category="achievements"))

    elif intent == "faq":
        raw = _load("faqs.json")
        faqs = raw.get("faqs", [])
        data["faqs"] = _rank(
            faqs,
            lambda f: _score_faq(query_tokens, phrases, f),
            n=3,
        )
        sources.append(SourceChip(label="Profile FAQ", category="faq"))

    else:
        data = {}

    return data, sources

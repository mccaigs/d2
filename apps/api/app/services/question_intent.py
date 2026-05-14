"""Deterministic question-shape classifier.

Detects how the user phrased their question so the answer builder can select a
natural opening style. Topic classification remains in classifier.py.
"""

import re
from enum import Enum


class QuestionIntent(str, Enum):
    CAPABILITY = "capability"
    FIT_YES_NO = "fit_yes_no"
    STRENGTHS = "strengths"
    EXPERIENCE = "experience"
    IDENTITY_SUMMARY = "identity_summary"
    WORKING_STYLE = "working_style"
    AVAILABILITY_COMMERCIAL = "availability_commercial"
    GENERAL_PROFILE = "general_profile"


_PATTERNS: list[tuple[re.Pattern[str], QuestionIntent]] = [
    (
        re.compile(
            r"\b(?:what\s+(?:is|are)\s+bidworx\s+(?:strongest|best)\s+at"
            r"|what\s+(?:are|is)\s+(?:the\s+)?(?:key\s+)?strengths?"
            r"|what\s+makes\s+bidworx\s+(?:different|reliable|useful))"
        ),
        QuestionIntent.STRENGTHS,
    ),
    (
        re.compile(
            r"\b(?:how\s+does\s+bidworx\s+(?:work|analyse|analyze|score|check)"
            r"|what\s+is\s+(?:the\s+)?(?:workflow|approach|process)"
            r"|how\s+does\s+(?:the\s+)?platform\s+operate)"
        ),
        QuestionIntent.WORKING_STYLE,
    ),
    (
        re.compile(
            r"\b(?:what\s+is\s+bidworx"
            r"|tell\s+me\s+about\s+bidworx"
            r"|summari[sz]e\s+bidworx"
            r"|give\s+(?:me\s+)?(?:an?\s+)?(?:overview|summary)"
            r"|describe\s+bidworx)"
        ),
        QuestionIntent.IDENTITY_SUMMARY,
    ),
    (
        re.compile(
            r"\b(?:can\s+(?:we|i)\s+(?:use|try|pilot|deploy)\s+bidworx"
            r"|is\s+bidworx\s+(?:available|ready|suitable)"
            r"|book\s+a\s+demo)"
        ),
        QuestionIntent.AVAILABILITY_COMMERCIAL,
    ),
    (
        re.compile(
            r"\b(?:is\s+this\s+(?:a\s+)?(?:good\s+)?(?:opportunity|tender|bid)"
            r"|should\s+we\s+bid"
            r"|is\s+this\s+worth\s+pursuing"
            r"|score\s+this\s+(?:opportunity|tender|bid))"
        ),
        QuestionIntent.FIT_YES_NO,
    ),
    (
        re.compile(
            r"\b(?:what\s+(?:does|can)\s+bidworx\s+(?:analyse|analyze|check|extract|review)"
            r"|what\s+(?:workflow|workflows)\s+does\s+bidworx\s+support"
            r"|what\s+has\s+the\s+platform\s+been\s+set\s+up\s+to\s+do)"
        ),
        QuestionIntent.EXPERIENCE,
    ),
    (
        re.compile(
            r"\b(?:what\s+(?:can|does|could)\s+bidworx\s+(?:do|help|offer|provide)"
            r"|what\s+evidence\s+do\s+we\s+need"
            r"|what\s+capabilities\s+does\s+bidworx\s+have)"
        ),
        QuestionIntent.CAPABILITY,
    ),
]


def classify_question_intent(question: str) -> QuestionIntent:
    text = re.sub(r"[^\w\s'?/-]", " ", (question or "").lower())
    text = re.sub(r"\s+", " ", text).strip()

    for pattern, intent in _PATTERNS:
        if pattern.search(text):
            return intent

    return QuestionIntent.GENERAL_PROFILE

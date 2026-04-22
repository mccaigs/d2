"""Deterministic question-shape classifier.

Detects how the user phrased their question (not *what* they asked about —
that is the topic classifier's job) so the answer builder can select a
natural opening style.

Rule-based, ordered pattern matching. No LLM.
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


# Each entry: (compiled regex, QuestionIntent).
# Order matters — first match wins. More specific patterns come first.
_PATTERNS: list[tuple[re.Pattern[str], QuestionIntent]] = [
    # --- strengths (before generic capability) ---
    (re.compile(
        r"\b(?:what\s+is\s+(?:david|he)\s+(?:strongest|best)\s+at"
        r"|what\s+(?:are|is)\s+(?:david(?:'?s)?|his)\s+(?:strongest|best|key)\s+skill"
        r"|where\s+(?:is|does)\s+(?:david|he)\s+(?:strongest|best|excel)"
        r"|what\s+does\s+(?:david|he)\s+do\s+best"
        r"|what\s+(?:is|are)\s+(?:david|he)\s+(?:strongest|best)\b)"
    ), QuestionIntent.STRENGTHS),

    # --- working style ---
    (re.compile(
        r"\b(?:how\s+does\s+(?:david|he)\s+(?:work|approach|operate|deliver)"
        r"|what\s+is\s+(?:david|he)\s+like\s+to\s+work\s+with"
        r"|what\s+is\s+(?:david(?:'?s)?|his)\s+(?:working\s+style|approach)"
        r"|how\s+does\s+(?:david|he)\s+approach)"
    ), QuestionIntent.WORKING_STYLE),

    # --- identity / summary ---
    (re.compile(
        r"\b(?:who\s+is\s+(?:david|he)"
        r"|tell\s+me\s+about\s+david"
        r"|summari[sz]e\s+david"
        r"|give\s+(?:me\s+)?(?:an?\s+)?(?:overview|summary)\s+(?:of\s+)?david"
        r"|introduce\s+david"
        r"|describe\s+david)"
    ), QuestionIntent.IDENTITY_SUMMARY),

    # --- availability / commercial (yes/no shape) ---
    (re.compile(
        r"\b(?:is\s+(?:david|he)\s+(?:available|open|free|taking)"
        r"|can\s+(?:i|we)\s+(?:hire|engage|book|commission)\s+(?:david|him)"
        r"|does\s+(?:david|he)\s+(?:do|take|accept)\s+(?:advisory|consulting|contract|freelance)"
        r"|is\s+(?:david|he)\s+open\s+to\s+(?:consulting|contract|freelance|short))"
    ), QuestionIntent.AVAILABILITY_COMMERCIAL),

    # --- fit yes/no ---
    (re.compile(
        r"\b(?:is\s+(?:david|he)\s+(?:a\s+)?(?:good\s+)?(?:fit|suited|suitable|right|match)"
        r"|would\s+(?:david|he)\s+(?:suit|fit|be\s+(?:a\s+)?(?:good\s+)?(?:fit|match|suited|suitable))"
        r"|can\s+(?:david|he)\s+(?:do|handle|fill|take\s+on)\s+this\s+(?:role|position|job)"
        r"|(?:david|he)\s+(?:a\s+)?good\s+(?:fit|match|candidate))"
    ), QuestionIntent.FIT_YES_NO),

    # --- experience / what has he built ---
    (re.compile(
        r"\b(?:what\s+has\s+(?:david|he)\s+(?:built|made|created|developed|shipped|delivered|worked\s+on)"
        r"|what\s+(?:\w+\s+){0,3}(?:systems?|products?|projects?)\s+has\s+(?:david|he)\s+(?:built|made|created|shipped|delivered)"
        r"|what\s+projects?\s+has\s+(?:david|he)"
        r"|what\s+has\s+(?:david|he)\s+actually\s+(?:built|made|done)"
        r"|what\s+did\s+(?:david|he)\s+build)"
    ), QuestionIntent.EXPERIENCE),

    # --- capability (what can / what does) ---
    (re.compile(
        r"\b(?:what\s+(?:can|does|could)\s+(?:david|he)\s+(?:do|help|offer|deliver|build|provide)"
        r"|what\s+(?:kind|type|sort)\s+of\s+(?:work|things?|projects?)\s+(?:does|can|could)\s+(?:david|he)"
        r"|what\s+is\s+(?:david|he)\s+(?:able|capable)\s+(?:of|to)"
        r"|what\s+(?:services?|work)\s+does\s+(?:david|he))"
    ), QuestionIntent.CAPABILITY),
]


def classify_question_intent(question: str) -> QuestionIntent:
    """Classify the rhetorical shape of a user question.

    Returns a QuestionIntent that describes *how* the question was framed
    (yes/no, what-can, who-is, etc.) — independent of the topic classifier.
    """
    text = re.sub(r"[^\w\s'?]", " ", (question or "").lower())
    text = re.sub(r"\s+", " ", text).strip()

    for pattern, intent in _PATTERNS:
        if pattern.search(text):
            return intent

    return QuestionIntent.GENERAL_PROFILE

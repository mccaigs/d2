"""Centralised response-style selection.

Maps a QuestionIntent to a ResponseStyle that controls how the answer
builder composes the opening line and overall framing.

Deterministic. No LLM.
"""

from dataclasses import dataclass

from app.services.question_intent import QuestionIntent


@dataclass(frozen=True, slots=True)
class ResponseStyle:
    """Controls answer composition for a given question shape."""

    # Opening pattern template.  Use ``{subject}`` as placeholder for
    # "David" or a pronoun, and ``{detail}`` for the context-aware clause
    # that the answer builder fills in.
    opening_pattern: str

    # Whether the opening may begin with "Yes — " / "No — ".
    allow_yes_no_prefix: bool = False

    # Whether evaluative / judgement language is appropriate.
    allow_evaluative: bool = False

    # Whether the answer should lean on list-heavy structure.
    prefer_lists: bool = False


# --------------------------------------------------------------------- #
# Style table
# --------------------------------------------------------------------- #

_STYLES: dict[QuestionIntent, ResponseStyle] = {
    QuestionIntent.CAPABILITY: ResponseStyle(
        opening_pattern="David {detail}",
        allow_yes_no_prefix=False,
        allow_evaluative=False,
        prefer_lists=True,
    ),
    QuestionIntent.FIT_YES_NO: ResponseStyle(
        opening_pattern="Yes — David {detail}",
        allow_yes_no_prefix=True,
        allow_evaluative=True,
        prefer_lists=False,
    ),
    QuestionIntent.STRENGTHS: ResponseStyle(
        opening_pattern="David is strongest at {detail}",
        allow_yes_no_prefix=False,
        allow_evaluative=True,
        prefer_lists=True,
    ),
    QuestionIntent.EXPERIENCE: ResponseStyle(
        opening_pattern="David has built {detail}",
        allow_yes_no_prefix=False,
        allow_evaluative=False,
        prefer_lists=True,
    ),
    QuestionIntent.IDENTITY_SUMMARY: ResponseStyle(
        opening_pattern="David is {detail}",
        allow_yes_no_prefix=False,
        allow_evaluative=False,
        prefer_lists=False,
    ),
    QuestionIntent.WORKING_STYLE: ResponseStyle(
        opening_pattern="David works best {detail}",
        allow_yes_no_prefix=False,
        allow_evaluative=False,
        prefer_lists=False,
    ),
    QuestionIntent.AVAILABILITY_COMMERCIAL: ResponseStyle(
        opening_pattern="Yes — David is available {detail}",
        allow_yes_no_prefix=True,
        allow_evaluative=False,
        prefer_lists=True,
    ),
    QuestionIntent.GENERAL_PROFILE: ResponseStyle(
        opening_pattern="David {detail}",
        allow_yes_no_prefix=False,
        allow_evaluative=False,
        prefer_lists=False,
    ),
}


def select_response_style(intent: QuestionIntent) -> ResponseStyle:
    """Return the ResponseStyle for a classified question shape."""
    return _STYLES.get(intent, _STYLES[QuestionIntent.GENERAL_PROFILE])

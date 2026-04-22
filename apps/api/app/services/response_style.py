"""Centralised response-style selection.

This keeps opening-line composition deterministic and consistent across the
answer builder. The builder still decides the content; this module decides the
shape of the opening sentence.
"""

from dataclasses import dataclass

from app.services.question_intent import QuestionIntent


@dataclass(frozen=True, slots=True)
class ResponseStyle:
    opening_pattern: str
    allow_yes_no_prefix: bool = False
    allow_evaluative: bool = False
    prefer_lists: bool = False


_STYLES: dict[QuestionIntent, ResponseStyle] = {
    QuestionIntent.CAPABILITY: ResponseStyle(
        opening_pattern="David {detail}",
        prefer_lists=True,
    ),
    QuestionIntent.FIT_YES_NO: ResponseStyle(
        opening_pattern="Yes, David {detail}",
        allow_yes_no_prefix=True,
        allow_evaluative=True,
    ),
    QuestionIntent.STRENGTHS: ResponseStyle(
        opening_pattern="David is strongest at {detail}",
        allow_evaluative=True,
        prefer_lists=True,
    ),
    QuestionIntent.EXPERIENCE: ResponseStyle(
        opening_pattern="David has built {detail}",
        prefer_lists=True,
    ),
    QuestionIntent.IDENTITY_SUMMARY: ResponseStyle(
        opening_pattern="David is {detail}",
    ),
    QuestionIntent.WORKING_STYLE: ResponseStyle(
        opening_pattern="David works best {detail}",
    ),
    QuestionIntent.AVAILABILITY_COMMERCIAL: ResponseStyle(
        opening_pattern="Yes, David is available {detail}",
        allow_yes_no_prefix=True,
        prefer_lists=True,
    ),
    QuestionIntent.GENERAL_PROFILE: ResponseStyle(
        opening_pattern="David {detail}",
    ),
}


def select_response_style(intent: QuestionIntent) -> ResponseStyle:
    return _STYLES.get(intent, _STYLES[QuestionIntent.GENERAL_PROFILE])

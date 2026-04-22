from fastapi import APIRouter

from app.models.suggestion import SuggestionResponse

router = APIRouter()

SUGGESTED_PROMPTS = [
    "What kinds of AI roles is David best suited for?",
    "What production AI systems has David built?",
    "What is David strongest at technically?",
    "Has David led full-stack AI product builds?",
    "What experience does David have with Python and Next.js?",
    "What makes David different from a typical engineer?",
]


@router.get("/suggestions")
async def get_suggestions() -> SuggestionResponse:
    return SuggestionResponse(
        prompts=SUGGESTED_PROMPTS,
        category="general",
    )

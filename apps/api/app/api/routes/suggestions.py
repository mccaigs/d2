from fastapi import APIRouter

from app.models.suggestion import SuggestionResponse

router = APIRouter()

SUGGESTED_PROMPTS = [
    "Analyse this tender opportunity",
    "What are the likely compliance risks?",
    "What evidence do we need to support this claim?",
    "Summarise the buyer requirements",
    "Score this opportunity",
    "Identify missing submission requirements",
]


@router.get("/suggestions")
async def get_suggestions() -> SuggestionResponse:
    return SuggestionResponse(
        prompts=SUGGESTED_PROMPTS,
        category="general",
    )

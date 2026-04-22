from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest, ChatMetadata
from app.services.classifier import classify, has_high_intent
from app.services.question_intent import QuestionIntent, classify_question_intent
from app.services.retriever import retrieve
from app.services.answer_builder import build_answer, get_follow_ups
from app.services.stream_writer import stream_response

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    message = request.message.strip()

    intent = classify(message)
    question_intent = classify_question_intent(message)

    # When the topic classifier draws a blank but the question-shape
    # classifier recognises a meaningful profile question, re-route to
    # the experience topic so we give a real answer instead of refusing.
    _RESCUABLE_INTENTS = {
        QuestionIntent.IDENTITY_SUMMARY,
        QuestionIntent.GENERAL_PROFILE,
        QuestionIntent.CAPABILITY,
        QuestionIntent.WORKING_STYLE,
        QuestionIntent.STRENGTHS,
    }
    if intent == "unknown" and question_intent in _RESCUABLE_INTENTS:
        intent = "experience"

    data, sources = retrieve(intent, message)
    answer = build_answer(intent, data, message, question_intent=question_intent)
    follow_ups = get_follow_ups(intent)

    # Show the contact-form CTA only on clear conversion signals: a direct
    # `contact` intent, or an `engagement` query layered with hire / rates /
    # budget / contact / discuss wording. Role-fit, project, and skills
    # questions never surface the form by default.
    show_contact_form = False
    contact_reason: str | None = None
    if intent == "contact":
        show_contact_form = True
        contact_reason = "high_intent"
    elif intent == "engagement" and has_high_intent(message):
        show_contact_form = True
        contact_reason = "engagement_high_intent"

    metadata = ChatMetadata(
        sources=sources,
        follow_ups=follow_ups,
        intent=intent,
        show_contact_form=show_contact_form,
        contact_reason=contact_reason,
    )

    return StreamingResponse(
        stream_response(answer, metadata),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

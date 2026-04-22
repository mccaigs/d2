from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatCta, ChatRequest, ChatMetadata
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

    rescue_map = {
        QuestionIntent.IDENTITY_SUMMARY: "profile_overview",
        QuestionIntent.GENERAL_PROFILE: "profile_overview",
        QuestionIntent.CAPABILITY: "capabilities",
        QuestionIntent.WORKING_STYLE: "experience_summary",
        QuestionIntent.STRENGTHS: "strengths",
        QuestionIntent.EXPERIENCE: "projects_overview",
        QuestionIntent.AVAILABILITY_COMMERCIAL: "engagement_preferences",
    }
    if intent == "unknown":
        intent = rescue_map.get(question_intent, "unknown")

    data, sources = retrieve(intent, message)
    answer = build_answer(intent, data, message, question_intent=question_intent)
    follow_ups = get_follow_ups(intent)

    cta: ChatCta | None = None
    show_contact_form = False
    contact_reason: str | None = None

    # --- CTA rules ---
    # Always: explicit contact intent
    if intent == "contact":
        cta = ChatCta(type="link", label="Open contact form", href="/contact?intent=general")
        show_contact_form = True
        contact_reason = "contact_intent"
    # High-signal: explicit hire / engage / speak-to-David intent on commercial topics
    elif intent in {"engagement", "engagement_preferences"} and has_high_intent(message):
        cta = ChatCta(type="link", label="Open contact form", href="/contact?intent=hire")
        show_contact_form = True
        contact_reason = "commercial_intent"
    # High-signal: role fit questions with genuine hiring intent
    elif intent == "role_fit" and has_high_intent(message):
        cta = ChatCta(type="link", label="Discuss this with David", href="/contact?intent=hire")
        show_contact_form = True
        contact_reason = "fit_intent"
    # Do NOT attach CTA for:
    # - General capability / skill / project questions
    # - Mentions of rates or preferences without explicit hire signal
    # - Informational role_fit questions (browsing, not buying)

    metadata = ChatMetadata(
        sources=sources,
        follow_ups=follow_ups,
        intent=intent,
        cta=cta,
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

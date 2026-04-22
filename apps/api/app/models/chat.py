from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    message: str


class SourceChip(BaseModel):
    label: str
    category: str


class ChatCta(BaseModel):
    type: Literal["link"]
    label: str
    href: str


class ChatMetadata(BaseModel):
    sources: list[SourceChip]
    follow_ups: list[str]
    intent: str
    cta: ChatCta | None = None
    show_contact_form: bool = False
    contact_reason: str | None = None

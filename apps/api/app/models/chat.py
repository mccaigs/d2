from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    message: str


class SourceChip(BaseModel):
    label: str
    category: str


class ChatMetadata(BaseModel):
    sources: list[SourceChip]
    follow_ups: list[str]
    intent: str
    show_contact_form: bool = False
    contact_reason: str | None = None

from pydantic import BaseModel


class SuggestionResponse(BaseModel):
    prompts: list[str]
    category: str

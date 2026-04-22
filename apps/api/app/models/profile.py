from pydantic import BaseModel


class ProfileSummary(BaseModel):
    name: str
    headline: str
    location: str
    website: str
    summary: str
    positioning: list[str]
    core_strengths: list[str]
    preferred_roles: list[str]
    availability_summary: str
    contact_cta: str

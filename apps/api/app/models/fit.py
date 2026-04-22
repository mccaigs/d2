from typing import Literal

from pydantic import BaseModel


class FitRequest(BaseModel):
    job_description: str


class FitGap(BaseModel):
    area: str
    note: str


class ProjectMatch(BaseModel):
    name: str
    reason: str


class ScoreBreakdown(BaseModel):
    technical: int
    applied_ai: int
    product_architecture: int
    domain: int
    seniority: int


class FitResponse(BaseModel):
    summary: str
    overall_score: int
    fit_label: str
    breakdown: ScoreBreakdown
    confidence: Literal["high", "medium", "low"]
    confidence_reason: str
    strengths: list[str]
    gaps: list[FitGap]
    relevant_projects: list[ProjectMatch]
    talking_points: list[str]

from typing import Literal, Optional

from pydantic import BaseModel


class FitRequest(BaseModel):
    job_description: str


class FitGap(BaseModel):
    area: str
    note: str
    # Tier classifies the severity of the gap so the UI can render it appropriately.
    # hard  = disqualifying; soft = bridgeable; risk = discussion point only.
    tier: Optional[Literal["hard", "soft", "risk"]] = None


class ProjectMatch(BaseModel):
    name: str
    reason: str


class ScoreBreakdown(BaseModel):
    technical: int
    applied_ai: int
    product_architecture: int
    domain: int
    seniority: int


class DimensionEvidence(BaseModel):
    """Per-dimension evidence quality, derived from the evidence-aware scoring model."""

    technical: str
    applied_ai: str
    product_architecture: str
    domain: str
    seniority: str


class DimensionWeights(BaseModel):
    """Role-adaptive dimension weights used to compute the overall score."""

    technical: float
    applied_ai: float
    product_architecture: float
    domain: float
    seniority: float


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
    # Role-awareness fields — Optional for backward compatibility
    role_type: Optional[str] = None
    dimension_weights: Optional[DimensionWeights] = None
    dimension_evidence: Optional[DimensionEvidence] = None

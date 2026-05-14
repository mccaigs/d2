from pydantic import BaseModel, Field


class ExtractedRequirement(BaseModel):
    id: str
    text: str
    requirement_type: str
    confidence: str


class ComplianceRisk(BaseModel):
    area: str
    note: str
    severity: str
    evidence_needed: list[str] = Field(default_factory=list)


class EvidenceNeed(BaseModel):
    label: str
    category: str
    reason: str


class ReadinessScore(BaseModel):
    score: int
    label: str
    dimensions: dict[str, int]


class TenderAnalysis(BaseModel):
    buyer: str | None = None
    opportunity_type: str | None = None
    opportunity_summary: str
    buyer_requirements: list[ExtractedRequirement]
    submission_requirements: list[ExtractedRequirement]
    compliance_risks: list[ComplianceRisk]
    evidence_needed: list[EvidenceNeed]
    readiness: ReadinessScore

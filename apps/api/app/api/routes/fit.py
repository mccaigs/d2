from fastapi import APIRouter

from app.models.fit import (
    FitRequest,
    FitResponse,
    FitGap,
    ProjectMatch,
    ScoreBreakdown,
    DimensionEvidence,
    DimensionWeights,
)
from app.services.fit_analyser import analyse_fit

router = APIRouter()


@router.post("/fit/analyse", response_model=FitResponse)
async def fit_analyse(request: FitRequest) -> FitResponse:
    result = analyse_fit(request.job_description)

    dimension_evidence = (
        DimensionEvidence(**result["dimension_evidence"])
        if result.get("dimension_evidence")
        else None
    )
    dimension_weights = (
        DimensionWeights(**result["dimension_weights"])
        if result.get("dimension_weights")
        else None
    )

    return FitResponse(
        summary=result["summary"],
        overall_score=result["overall_score"],
        fit_label=result["fit_label"],
        breakdown=ScoreBreakdown(**result["breakdown"]),
        confidence=result["confidence"],
        confidence_reason=result["confidence_reason"],
        strengths=result["strengths"],
        gaps=[FitGap(**g) for g in result["gaps"]],
        relevant_projects=[ProjectMatch(**p) for p in result["relevant_projects"]],
        talking_points=result["talking_points"],
        role_type=result.get("role_type"),
        dimension_weights=dimension_weights,
        dimension_evidence=dimension_evidence,
    )

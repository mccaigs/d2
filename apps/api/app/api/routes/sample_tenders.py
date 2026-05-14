from fastapi import APIRouter

from app.models.tender import SampleTender
from app.services.sample_tenders import list_sample_tenders

router = APIRouter()


@router.get("/sample-tenders", response_model=list[SampleTender])
def sample_tenders() -> list[SampleTender]:
    return list_sample_tenders()

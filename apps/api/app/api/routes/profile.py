import json
from pathlib import Path
from fastapi import APIRouter

from app.models.profile import ProfileSummary

router = APIRouter()

_DATA_DIR = Path(__file__).parent.parent.parent / "data"


@router.get("/profile")
async def get_profile() -> ProfileSummary:
    with open(_DATA_DIR / "profile.json", encoding="utf-8") as f:
        data = json.load(f)
    return ProfileSummary(**data)

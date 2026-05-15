from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.startup import validate_required_data_files
from app.api.routes import chat, fit, health, profile, sample_tenders, suggestions


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_required_data_files()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Evidence-backed bid intelligence API for procurement teams.",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")
app.include_router(fit.router, prefix="/api")
app.include_router(sample_tenders.router, prefix="/api")

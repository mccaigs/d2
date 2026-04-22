from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, chat, profile, suggestions, fit

app = FastAPI(
    title=settings.app_name,
    description="Recruiter-facing profile assistant API for David Robertson.",
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")
app.include_router(fit.router, prefix="/api")

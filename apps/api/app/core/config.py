from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Bidworx API"
    app_version: str = "1.0.0"
    debug: bool = False
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3100",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3100",
            "https://bidworx.example",
            "https://www.bidworx.example",
        ],
        alias="CORS_ORIGINS",
    )
    cors_origin_regex: str | None = Field(
        default=r"^https://.*\.vercel\.app$",
        alias="CORS_ORIGIN_REGEX",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("cors_origin_regex", mode="before")
    @classmethod
    def parse_cors_origin_regex(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip():
            return None
        return v


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "davidrobertson.pro API"
    app_version: str = "1.0.0"
    debug: bool = False
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://davidrobertson.pro",
    ]

    class Config:
        env_file = ".env"


settings = Settings()

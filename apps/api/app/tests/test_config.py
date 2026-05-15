from app.core.config import settings


def test_cors_defaults_cover_local_preview_and_placeholder_domains() -> None:
    assert "http://localhost:3000" in settings.cors_origins
    assert "http://127.0.0.1:3100" in settings.cors_origins
    assert "https://bidworx.example" in settings.cors_origins
    assert settings.cors_origin_regex == r"^https://.*\.vercel\.app$"

from app.services.classifier import classify


def test_classify_profile_overview() -> None:
    assert classify("Who is David?") == "profile_overview"
    assert classify("What does David do?") == "profile_overview"


def test_classify_technical_stack() -> None:
    assert classify("What tech stack does he use?") == "technical_stack"


def test_classify_projects_overview() -> None:
    assert classify("What has David built?") == "projects_overview"


def test_classify_experience_summary() -> None:
    assert classify("Summarise David's experience") == "experience_summary"


def test_classify_capabilities() -> None:
    assert classify("What can David do?") == "capabilities"


def test_classify_engagement_preferences() -> None:
    assert classify("What roles is he open to?") == "engagement_preferences"
    assert classify("What are David's day rates?") == "engagement_preferences"


def test_classify_contact() -> None:
    assert classify("How do I contact David?") == "contact"
    assert classify("What is David's email address?") == "contact"


def test_classify_role_fit_unaffected() -> None:
    assert classify("Would David suit a solutions architect role?") == "role_fit"


def test_classify_unknown() -> None:
    assert classify("What is the weather today?") == "unknown"

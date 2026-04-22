from app.services.retriever import retrieve


def test_retrieve_profile_overview_from_cv() -> None:
    data, sources = retrieve("profile_overview", "What does David do?")
    assert data["title"]
    assert data["profile"]
    assert data["capabilities"]
    assert data["core_skills"]
    assert sources[0].category == "cv"


def test_retrieve_technical_stack_from_cv() -> None:
    data, sources = retrieve("technical_stack", "What tech stack does he use?")
    assert data["tech_stack"]["languages"]
    assert data["core_skills"]
    assert sources[0].label == "CV Stack"


def test_retrieve_projects_overview_from_cv() -> None:
    data, sources = retrieve("projects_overview", "What has David built?")
    assert data["projects"]
    assert data["key_systems"]
    assert sources[0].category == "cv"


def test_retrieve_engagement_preferences_from_cv() -> None:
    data, sources = retrieve("engagement_preferences", "What roles is he open to?")
    assert data["work_type"]
    assert data["rates"]["day_rate"]
    assert data["full_time_preferences"]["ideal_roles"]
    assert sources[0].category == "cv"


def test_retrieve_contact_is_gated() -> None:
    data, sources = retrieve("contact", "How do I contact David?")
    assert "availability" in data
    assert "focus" in data
    assert "phone" not in data
    assert "email" not in data
    assert sources[0].category == "cv"


def test_retrieve_unknown() -> None:
    data, sources = retrieve("unknown", "Random question")
    assert data == {}
    assert sources == []

import pytest
from app.services.retriever import retrieve


def test_retrieve_skills():
    data, sources = retrieve("skills", "What skills does David have?")
    assert "technical_skills" in data
    assert len(sources) > 0
    assert sources[0].category == "skills"


def test_retrieve_projects():
    data, sources = retrieve("projects", "What projects has David built?")
    assert "projects" in data
    assert len(data["projects"]) > 0
    assert len(sources) > 0


def test_retrieve_unknown():
    data, sources = retrieve("unknown", "Random question")
    assert data == {}
    assert sources == []


def test_retrieve_contact_surfaces_services_and_projects():
    data, sources = retrieve("contact", "What are David's day rates?")
    assert data["custom_services"]
    assert data["pricing_notes"]
    assert data["contact_cta"]
    assert data["projects"]
    assert any(s.category == "projects" for s in sources)

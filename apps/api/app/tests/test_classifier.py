import pytest
from app.services.classifier import classify


def test_classify_skills():
    result = classify("What skills does David have?")
    assert result == "skills"


def test_classify_projects():
    result = classify("What projects has David built?")
    assert result == "projects"


def test_classify_experience():
    result = classify("What is David's background?")
    assert result == "experience"


def test_classify_strengths():
    result = classify("What is David strongest at?")
    assert result == "strengths"


def test_classify_role_fit():
    result = classify("Is David a good fit for this role?")
    assert result == "role_fit"


def test_classify_unknown():
    result = classify("What is the weather today?")
    assert result == "unknown"


def test_classify_contact_direct():
    assert classify("How do I contact David?") == "contact"
    assert classify("What is David's email?") == "contact"
    assert classify("Can I get in touch with David?") == "contact"


def test_classify_contact_rates():
    assert classify("What are David's day rates?") == "contact"
    assert classify("What's David's pricing?") == "contact"


def test_classify_contact_hiring_conversion():
    assert classify("Can David help us build this?") == "contact"
    assert classify("We'd like to start a project with David.") == "contact"


def test_classify_engagement_still_routes_for_service_queries():
    # No direct-contact phrase — should stay on engagement
    assert classify("Does David do freelance MVP builds?") == "engagement"
    assert classify("Does he take consulting or advisory engagements?") == "engagement"


def test_classify_projects_not_hijacked_by_contact():
    # "built" / "recruiter tools" should not trip the contact override
    assert classify("Has David built recruiter tools?") == "projects"


def test_classify_technical_stack_unaffected():
    assert classify("What is David's technical stack?") == "technical_stack"


def test_classify_role_fit_unaffected():
    assert classify("Would David suit a solutions architect role?") == "role_fit"

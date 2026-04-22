from app.services.answer_builder import build_answer, get_follow_ups


def test_build_answer_profile_overview() -> None:
    answer = build_answer(
        "profile_overview",
        {
            "title": "AI Architect | AI Systems Engineer | AI Product Builder",
            "location": "Edinburgh, United Kingdom",
            "profile": "Builds production AI systems.",
            "capabilities": ["AI systems architecture", "Workflow automation"],
            "core_skills": ["Python backend engineering", "Next.js frontend systems"],
            "ideal_roles": ["Senior AI Engineer"],
            "focus": "Open to high-impact AI work.",
        },
        message="What does David do?",
    )
    assert "AI Architect" in answer
    assert "Workflow automation" in answer
    assert "Senior AI Engineer" in answer


def test_build_answer_technical_stack() -> None:
    answer = build_answer(
        "technical_stack",
        {
            "tech_stack": {
                "languages": ["Python", "TypeScript"],
                "frameworks": ["Next.js", "Node.js"],
                "backend": ["Convex", "REST APIs"],
                "frontend": ["Next.js", "Tailwind CSS"],
                "ai_tools": ["OpenAI", "Anthropic"],
                "infrastructure": ["Linux", "Docker"],
                "other": ["GitHub Actions"],
            },
            "core_skills": ["LLM orchestration", "Structured data pipelines"],
        },
        message="What tech stack does he use?",
    )
    assert "Backend" in answer
    assert "Frontend" in answer
    assert "OpenAI" in answer


def test_build_answer_projects_overview() -> None:
    answer = build_answer(
        "projects_overview",
        {
            "projects": [
                {
                    "name": "AI Jobs Pipeline",
                    "description": "Automated job scanning and deterministic scoring.",
                    "features": ["Multi-source ingestion", "Deterministic scoring engine"],
                },
                {
                    "name": "InterviewsAI",
                    "description": "Interview evaluation with adaptive questioning.",
                    "features": ["Structured scoring outputs"],
                },
            ],
            "key_systems": ["AI interview simulation and evaluation system"],
            "products": ["CareersAI"],
        },
        message="What has David built?",
    )
    assert "AI Jobs Pipeline" in answer
    assert "InterviewsAI" in answer
    assert "CareersAI" in answer


def test_build_answer_contact_is_gated() -> None:
    answer = build_answer(
        "contact",
        {
            "availability": "Available immediately",
            "focus": "Open to high-impact work.",
        },
        message="How do I contact David?",
    )
    assert "contact page" in answer.lower()
    assert "07565" not in answer
    assert "@" not in answer


def test_get_follow_ups() -> None:
    follow_ups = get_follow_ups("profile_overview")
    assert len(follow_ups) > 0
    assert isinstance(follow_ups[0], str)

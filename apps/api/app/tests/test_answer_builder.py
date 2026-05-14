from app.services.answer_builder import build_answer


def test_build_product_overview_answer() -> None:
    answer = build_answer(
        "profile_overview",
        {
            "name": "Bidworx",
            "title": "Evidence-backed bid intelligence",
            "profile": "Bidworx analyses tenders from approved procurement records.",
            "capabilities": ["Maps buyer requirements to evidence"],
            "ideal_roles": ["Bid teams"],
            "focus": "Use before drafting.",
        },
        message="What is Bidworx?",
    )
    assert "Bidworx" in answer
    assert "Evidence-backed" in answer


def test_build_capabilities_answer() -> None:
    answer = build_answer(
        "capabilities",
        {
            "capabilities": [
                {
                    "name": "Evidence mapping",
                    "notes": "Maps bid claims to approved proof points.",
                }
            ],
            "working_style": ["Flags unsupported claims"],
        },
        message="What evidence do we need?",
    )
    assert "Evidence mapping" in answer
    assert "unsupported claims" in answer


def test_unknown_refuses_scope() -> None:
    answer = build_answer("unknown", {}, message="Tell me a joke")
    assert "Bidworx procurement intelligence" in answer

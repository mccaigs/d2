from app.services.retriever import retrieve


def test_retrieve_product_overview() -> None:
    data, sources = retrieve("profile_overview", "What is Bidworx?")
    assert data["name"] == "Bidworx"
    assert data["capabilities"]
    assert sources[0].label == "Product Overview"


def test_retrieve_capabilities() -> None:
    data, sources = retrieve("capabilities", "What evidence supports this claim?")
    assert data["capabilities"]
    assert sources[0].category == "capabilities"


def test_retrieve_workflows() -> None:
    data, sources = retrieve("workflows_overview", "What does Bidworx analyse?")
    assert data["workflows"]
    assert data["scoring_rules"]
    assert sources[0].category == "workflows"

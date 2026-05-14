from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_sample_tenders_route_returns_demo_samples() -> None:
    response = client.get("/api/sample-tenders")

    assert response.status_code == 200
    samples = response.json()
    assert len(samples) == 3
    titles = {sample["title"] for sample in samples}
    assert "Clear strong opportunity" in titles
    assert "Risky missing compliance evidence" in titles
    assert "Poor-fit cautious no-bid" in titles
    assert all(sample["text"] for sample in samples)

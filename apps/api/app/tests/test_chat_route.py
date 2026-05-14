import json

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


TENDER_TEXT = """
Buyer: Northshire Council.
The supplier must provide a secure case management service for adult social care.
The solution shall include implementation methodology, service reporting, and data protection controls.
Responses must include a pricing schedule, signed declaration, insurance certificate,
and risk management plan.
Submission is via the procurement portal by 12 May.
The buyer requires case study evidence, GDPR policy detail, social value evidence, and value for money.
Pass/fail checks apply to mandatory documents and eligibility.
"""


def _collect(message: str) -> str:
    response = client.post("/api/chat/stream", json={"message": message})
    assert response.status_code == 200
    body = response.text
    assert "data:" in body
    return body


def test_chat_stream_product_query() -> None:
    body = _collect("What is Bidworx?")
    assert "Bidworx" in body
    assert "metadata" in body


def test_chat_stream_compliance_query() -> None:
    body = _collect("What are the likely compliance risks?")
    assert "Compliance" in body or "compliance" in body


def test_metadata_is_json() -> None:
    body = _collect("What evidence do we need to support this claim?")
    metadata_lines = [
        line.removeprefix("data: ").strip()
        for line in body.splitlines()
        if line.startswith("data:") and '"type": "metadata"' in line
    ]
    assert metadata_lines
    parsed = json.loads(metadata_lines[-1])
    assert parsed["sources"]


def test_chat_stream_pasted_tender_analysis() -> None:
    body = _collect(TENDER_TEXT)

    assert "Opportunity summary" in body
    assert "Buyer requirements" in body
    assert "Submission requirements" in body
    assert "Compliance risks" in body
    assert "Evidence needed" in body
    assert "Bid/no-bid readiness score" in body

    metadata_lines = [
        line.removeprefix("data: ").strip()
        for line in body.splitlines()
        if line.startswith("data:") and '"type": "metadata"' in line
    ]
    parsed = json.loads(metadata_lines[-1])
    assert parsed["intent"] == "tender_analysis"
    labels = {source["label"] for source in parsed["sources"]}
    assert {"Compliance Rules", "Scoring Rules"}.issubset(labels)

from fastapi.testclient import TestClient

from legal_ease import api
from legal_ease.schemas import DocumentRequest


class FakeGenerator:
    def generate_document(self, request: DocumentRequest) -> str:
        return f"Draft: {request.document_type} for {request.parties}"


def test_health_reports_keyless_service(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")
    client = TestClient(api.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "gemini_configured": False}


def test_generate_returns_draft_and_disclaimer(monkeypatch) -> None:
    monkeypatch.setattr(api, "GeminiDocumentGenerator", FakeGenerator)
    client = TestClient(api.app)
    payload = {
        "document_type": "Freelance Services Agreement",
        "parties": "Riley (Provider); Acme (Client)",
        "terms": "Payment within 30 days; confidentiality",
        "effective_date": "October 10, 2026",
    }

    response = client.post("/generate", json=payload)

    assert response.status_code == 200
    assert response.json()["document"] == "Draft: Freelance Services Agreement for Riley (Provider); Acme (Client)"
    assert "not legal advice" in response.json()["disclaimer"]


def test_generate_rejects_blank_fields() -> None:
    client = TestClient(api.app)
    payload = {
        "document_type": "NDA",
        "parties": "Client and consultant",
        "terms": "Keep information confidential",
        "effective_date": " ",
    }

    response = client.post("/generate", json=payload)

    assert response.status_code == 422


def test_generate_without_key_returns_configuration_error(monkeypatch) -> None:
    from legal_ease.services.gemini import GeminiDocumentGenerator

    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setattr(api, "GeminiDocumentGenerator", GeminiDocumentGenerator)
    client = TestClient(api.app)
    payload = {
        "document_type": "NDA",
        "parties": "Client and consultant",
        "terms": "Keep information confidential",
        "effective_date": "October 10, 2026",
    }

    response = client.post("/generate", json=payload)

    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]

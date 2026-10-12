"""FastAPI endpoints for health checks and document generation."""

from fastapi import FastAPI, HTTPException

from legal_ease.config import get_settings
from legal_ease.schemas import DocumentRequest, DocumentResponse
from legal_ease.services.gemini import (
    GenerationError,
    GeminiDocumentGenerator,
    MissingApiKeyError,
)

app = FastAPI(
    title="LegalEase API",
    description="Draft legal documents from user-provided terms and export them in the UI.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "gemini_configured": bool(get_settings().gemini_api_key),
    }


@app.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest) -> DocumentResponse:
    try:
        document = GeminiDocumentGenerator().generate_document(request)
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return DocumentResponse(document=document)

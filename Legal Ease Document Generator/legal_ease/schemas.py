"""Validated API request and response models."""

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    parties: str = Field(min_length=2, max_length=2000)
    terms: str = Field(min_length=2, max_length=12000)
    effective_date: str = Field(min_length=2, max_length=100)

    @field_validator("document_type", "parties", "terms", "effective_date")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be blank.")
        return cleaned


class DocumentResponse(BaseModel):
    document: str
    disclaimer: str = (
        "Drafting aid only, not legal advice. Have a qualified lawyer review this document "
        "before signing or relying on it."
    )

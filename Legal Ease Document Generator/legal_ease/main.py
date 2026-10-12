"""ASGI entry point: uvicorn legal_ease.main:app --reload"""

from legal_ease.api import app

__all__ = ["app"]

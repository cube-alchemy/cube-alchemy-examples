"""
Uvicorn entrypoint for the FastAPI app.

Run with:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from backend.main import app  # noqa: F401

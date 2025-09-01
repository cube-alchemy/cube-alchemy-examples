import os
from pydantic import BaseModel


class Settings(BaseModel):
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    broker_url: str = os.getenv("BROKER_URL", "redis://localhost:6379/1")
    result_backend: str = os.getenv("RESULT_BACKEND", "redis://localhost:6379/2")
    # security
    allow_origins: list[str] = [
        os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        os.getenv("FRONTEND_ORIGIN_ALT", "http://localhost:3000"),
        os.getenv("FRONTEND_ORIGIN_FASTAPI", "http://localhost:8000"),
    ]


settings = Settings()

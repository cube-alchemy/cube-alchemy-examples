# Simple Web Backend for Cube Alchemy (Example)

This example provides a FastAPI backend with Celery workers and Redis, plus a JS proxy to call cube methods from a browser.

Components:
- FastAPI app at `backend/main.py`

- Celery worker tasks at `backend/tasks/cube_tasks.py`

- Redis-based registry at `backend/registry.py`

- Frontend static files in `frontend/`

## Quickstart

Prereqs: Redis running locally.

1. Install deps in your virtualenv:

```
python -m pip install fastapi uvicorn celery redis pydantic[dotenv]
```

2. Start Redis (if not already running) and a Celery worker:

```
# one terminal
celery -A backend.celery_app.celery_app worker --loglevel=info
```

3. Run the FastAPI app:

```
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

4. Open `frontend/index.html` via a simple HTTP server or your browser and click "New Cube" then "Call cube.plot()".

Env vars (optional):
- `REDIS_URL` (default: redis://localhost:6379/0)

- `BROKER_URL` (default: redis://localhost:6379/1)

- `RESULT_BACKEND` (default: redis://localhost:6379/2)

- `FRONTEND_ORIGIN` for CORS

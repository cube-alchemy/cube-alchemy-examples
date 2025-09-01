from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .schemas import NewCubeResponse, CubeCallRequest, CubeCallResponse
from .tasks.cube_tasks import create_cube_task, call_cube_method_task

app = FastAPI(title="Cube Alchemy Backend", version="0.1")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in settings.allow_origins if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve demo frontend under /
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


@app.post("/cube/new", response_model=NewCubeResponse)
async def new_cube():
    # Create asynchronously but wait for id (short task)
    task = create_cube_task.delay({})
    cube_id = task.get(timeout=30)
    return NewCubeResponse(cube_id=cube_id)


@app.post("/cube/call", response_model=CubeCallResponse)
async def cube_call(payload: CubeCallRequest):
    try:
        task = call_cube_method_task.delay(
            payload.cube_id,
            payload.method,
            payload.args or [],
            payload.kwargs or {},
        )
        result = task.get(timeout=120)
        return CubeCallResponse(status="ok", result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

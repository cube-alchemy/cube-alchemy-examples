from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class NewCubeResponse(BaseModel):
    cube_id: str


class CubeCallRequest(BaseModel):
    cube_id: str
    method: str
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None


class CubeCallResponse(BaseModel):
    status: str
    result: Any | None = None
    error: str | None = None

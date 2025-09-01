from __future__ import annotations
from typing import Any, Dict
import base64
import io
import pickle

from ..celery_app import celery_app
from ..registry import registry

from cube_alchemy import Hypercube


@celery_app.task(name="cube.create")
def create_cube_task(init_payload: Dict[str, Any] | None = None) -> str:
    """Create a new Hypercube instance and persist it in the registry.
    Returns the generated cube_id.
    init_payload could include seed dataframes or a path to load from.
    """
    import uuid

    cube_id = str(uuid.uuid4())
    # Init a fresh cube per session; user can later load data/define metrics.
    tables = init_payload.get("tables") if init_payload else None
    cube = Hypercube(tables or {})

    # Register minimal functions needed later; can be overridden via method calls
    try:
        import numpy as np
        import pandas as pd
        cube.registered_functions = {"np": np, "pd": pd}
    except Exception:
        pass

    registry.save(cube_id, cube)
    return cube_id


def _serialize_return(value: Any) -> Any:
    """Best-effort serialization for returned values, including matplotlib figures."""
    try:
        import matplotlib.figure
        if isinstance(value, matplotlib.figure.Figure):
            buf = io.BytesIO()
            value.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            return {
                "_type": "image/png;base64",
                "data": base64.b64encode(buf.read()).decode("ascii"),
            }
    except Exception:
        pass

    # Fallback: try pandas df to records
    try:
        import pandas as pd
        if isinstance(value, pd.DataFrame):
            return {"_type": "dataframe", "data": value.to_dict(orient="records")}
    except Exception:
        pass

    # Last resort: pickle and base64-encode to make it JSON safe
    try:
        return {
            "_type": "pickle/base64",
            "data": base64.b64encode(pickle.dumps(value)).decode("ascii"),
        }
    except Exception:
        # really last resort: string repr
        return {"_type": "str", "data": repr(value)}


@celery_app.task(name="cube.call")
def call_cube_method_task(cube_id: str, method: str, args: list | None = None, kwargs: dict | None = None):
    cube = registry.get(cube_id)
    if cube is None:
        raise ValueError(f"Cube {cube_id} not found")

    # Security: allow only public methods
    if method.startswith("_"):
        raise ValueError("Attempt to call private/protected method")

    target = getattr(cube, method, None)
    if target is None or not callable(target):
        raise AttributeError(f"Method {method} not found on Hypercube")

    result = target(*(args or []), **(kwargs or {}))

    # Persist cube if mutated (best effort)
    try:
        registry.save(cube_id, cube)
    except Exception:
        pass

    return _serialize_return(result)

import time
from typing import Optional
from dataclasses import dataclass
import redis
import pickle

from .core.config import settings


@dataclass
class CubeRecord:
    cube_id: str
    created_at: float
    last_used: float


class CubeRegistry:
    """Redis-backed registry to store and retrieve pickled Hypercube instances.
    Keys:
      cube:<cube_id> -> pickled cube bytes
      meta:<cube_id> -> pickled CubeRecord
    """

    def __init__(self, redis_url: str | None = None):
        self.r = redis.Redis.from_url(redis_url or settings.redis_url)

    def _key(self, cube_id: str) -> str:
        return f"cube:{cube_id}"

    def _meta(self, cube_id: str) -> str:
        return f"meta:{cube_id}"

    def save(self, cube_id: str, cube_obj) -> None:
        now = time.time()
        # robust pickling: temporarily clear non-picklable fields
        to_restore = None
        try:
            data = pickle.dumps(cube_obj)
        except Exception:
            # common issue: registered_functions holds modules
            if hasattr(cube_obj, "registered_functions"):
                to_restore = getattr(cube_obj, "registered_functions")
                try:
                    cube_obj.registered_functions = {}
                    data = pickle.dumps(cube_obj)
                finally:
                    # restore even if dumping failed; we'll raise downstream
                    cube_obj.registered_functions = to_restore
            else:
                raise

        pipe = self.r.pipeline()
        pipe.set(self._key(cube_id), data)
        pipe.set(self._meta(cube_id), pickle.dumps(CubeRecord(cube_id, now, now)))
        pipe.execute()

    def get(self, cube_id: str):
        data = self.r.get(self._key(cube_id))
        if not data:
            return None
        cube = pickle.loads(data)
        # Re-register safe defaults after unpickling
        try:
            import numpy as np
            import pandas as pd
            setattr(cube, "registered_functions", {"np": np, "pd": pd})
        except Exception:
            pass
        # touch last_used
        self.r.set(self._meta(cube_id), pickle.dumps(CubeRecord(cube_id, time.time(), time.time())))
        return cube

    def delete(self, cube_id: str) -> None:
        self.r.delete(self._key(cube_id))
        self.r.delete(self._meta(cube_id))

    def exists(self, cube_id: str) -> bool:
        return self.r.exists(self._key(cube_id)) == 1


registry = CubeRegistry()

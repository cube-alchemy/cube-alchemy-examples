from __future__ import annotations
from typing import Dict, Any
import pandas as pd
from cube_alchemy import Hypercube


def build_demo_cube() -> Hypercube:
    """Build a minimal demo cube with empty tables so methods can be tested.
    In real usage, users will upload or define tables/metrics via API calls.
    """
    cube = Hypercube({})
    # create an empty PNL plot so frontend demo call works without data
    try:
        cube.define_query(name='PNL', metrics=[], dimensions=[])
        cube.define_plot(query_name='PNL', plot_name='Default', plot_type='bar', dimensions=[], metrics=[])
    except Exception:
        pass
    return cube

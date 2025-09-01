import streamlit as st
import pandas as pd
from typing import Dict, Any, List


def apply_filters(cube, criteria: Dict[str, List[str]]):
    """Mirror the original app behavior: reset and apply exact filter state."""
    cube.reset_filters('all')
    if criteria:
        cube.filter(criteria)


def render_sidebar_filters(cube):
    """Render fixed-dimension sidebar filters and apply them to the cube.

    Changes from previous behavior:
    - Removes any use of st.session_state for caching options.
    - Fetches option lists from the current (already-filtered) cube state.

    Returns (criteria, all_dims) where criteria is the dict used to filter
    and all_dims is the fixed list of dimensions.
    """
    st.sidebar.header('Filters')

    # Fixed list of dimensions for this UI
    all_dims = ['Year','Region', 'Business Type', 'Category','Subcategory']

    def fetch_options(dimension: str) -> List[str]:
        try:
            vals = cube.dimensions(dimensions=[dimension])[dimension]
            return vals.dropna().sort_values().unique().tolist()
        except Exception:
            return []

    # Sync widget state from currently applied cube filters BEFORE rendering widgets
    try:
        applied_now: Dict[str, List[Any]] = cube.get_filters(0)
    except Exception:
        applied_now = {}

    if st.session_state.get('_sync_filters_from_cube', False):
        for dim in all_dims:
            st.session_state[f'flt_{dim}'] = list(applied_now.get(dim, []))
        st.session_state['_sync_filters_from_cube'] = False
    st.session_state.setdefault('filters_dirty', False)

    # Ensure each widget key has an initial value (either existing state or applied filters)
    for dim in all_dims:
        key = f'flt_{dim}'
        if key not in st.session_state:
            st.session_state[key] = list(applied_now.get(dim, []))

    # Render filters inside a form so changes don't trigger reruns
    selections: Dict[str, List[str]] = {}
    with st.sidebar.form('filters_form', clear_on_submit=False):
        for dim in all_dims:
            options = fetch_options(dim)
            st.multiselect(dim, options=options, key=f'flt_{dim}')
            picked = list(st.session_state.get(f'flt_{dim}', []))
            if picked:
                selections[dim] = picked
        submitted = st.form_submit_button('Apply filters', use_container_width=True)

    # Apply on submit
    if submitted:
        try:
            current_filters: Dict[str, List[Any]] = cube.get_filters(0)
        except Exception:
            current_filters = {}

        dims_to_remove: List[str] = [d for d in current_filters.keys() if d not in selections]
        if dims_to_remove:
            cube.remove_filter(dims_to_remove)

        to_add: Dict[str, List[Any]] = {d: vals for d, vals in selections.items() if vals}
        if to_add:
            cube.filter(to_add)

        # On next run, sync widget selections from cube before rendering widgets
        st.session_state['_sync_filters_from_cube'] = True
        st.session_state['filters_dirty'] = False
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()

    # Optionally track dirty state (not used to block rendering)
    try:
        current_filters_compare: Dict[str, List[Any]] = cube.get_filters(0)
    except Exception:
        current_filters_compare = {}
    def _as_set_map(d: Dict[str, List[Any]]):
        return {k: set(v) for k, v in d.items()}
    st.session_state['filters_dirty'] = _as_set_map({d: list(st.session_state.get(f'flt_{d}', [])) for d in all_dims if st.session_state.get(f'flt_{d}', [])}) != _as_set_map(current_filters_compare)

    st.sidebar.write(cube.get_filters(0))
    
    return selections, all_dims

import streamlit as st
from typing import Dict, Any, List


def render_sidebar_filters(cube):
    """Render sidebar filters with minimal logic.

    Behavior:
    - User selections live in widget state (st.session_state) automatically.
    - On submit: reset all cube filters and apply only currently selected values.
    - Clearing selections and submitting results in no filters.
    - No extra flags, overrides, or reruns beyond the form's natural rerun.
    """
    st.sidebar.header('Filters')

    all_dims = ['Year','Region', 'Business Type', 'Category','Subcategory']

    def fetch_options(dimension: str) -> List[str]:
        try:
            vals = cube.dimensions(dimensions=[dimension])[dimension]
            return vals.dropna().sort_values().unique().tolist()
        except Exception:
            return []

    selections: Dict[str, List[str]] = {}
    with st.sidebar.form('filters_form', clear_on_submit=False):
        for dim in all_dims:
            options = fetch_options(dim)
            picked = st.multiselect(dim, options=options, key=f'flt_{dim}')
            if picked:
                selections[dim] = picked
        submitted = st.form_submit_button('Apply filters', use_container_width=True)

    if submitted:
        cube.reset_filters('all')
        if selections:
            cube.filter(selections)

    # Show applied filters (after potential submit)
    try:
        st.sidebar.write(cube.get_filters())
    except Exception:
        st.sidebar.write({})

    return selections, all_dims

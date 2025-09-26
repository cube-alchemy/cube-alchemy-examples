import streamlit as st
from typing import Dict, Any, List
from cube_alchemy_streamlit_components import filter


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
    with st.sidebar:
        
        col1, col2, col3 = st.columns(3)

        if col1.button('Clear'):
            cube.reset_filters('all')
            st.rerun()
        if col2.button('Undo'):
            cube.reset_filters('backward')
            st.rerun()
        if col3.button('Redo'):
            cube.reset_filters('fordward')
            st.rerun()
        
        for dim in all_dims:
            options = fetch_options(dim)
            picked = filter(dim, options=options)
            if picked:
                selections[dim] = picked
                if selections:
                    cube.filter(selections)
                    st.rerun()

        st.write(cube.get_filters())


    return selections, all_dims

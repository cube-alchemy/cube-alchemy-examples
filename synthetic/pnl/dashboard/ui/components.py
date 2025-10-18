import streamlit as st
from typing import Dict, Any, List
from cube_alchemy_streamlit_components import filter as filter_component
from core.cube_factory import get_cube


def load_yaml_button():
    cube = get_cube()
    if st.button('Load YAML'):    
        cube.load_from_model_catalog()

def fetch_options(dimension: str) -> List[str]:
        cube = get_cube()
        try:
            vals = cube.dimensions(dimensions=[dimension])[dimension]
            return vals.dropna().sort_values().unique().tolist()
        except Exception:
            return []
        
def filter(dim: str):
    cube = get_cube()
    options = fetch_options(dim)
    picked = filter_component(dim, options=options)
    if picked:
        cube.filter({dim: picked})
        st.rerun()

def render_sidebar_filters():
    """Render sidebar filters with minimal logic.

    Behavior:
    - User selections live in widget state (st.session_state) automatically.
    - On submit: reset all cube filters and apply only currently selected values.
    - Clearing selections and submitting results in no filters.
    - No extra flags, overrides, or reruns beyond the form's natural rerun.
    """
    st.header("Filters")
    cube = get_cube()
    all_dims = ['year', 'month_year', 'division','pnl_report_line', 'pnl_category']
    
    # Filter action buttons
    col1, col2, col3 = st.columns(3)

    if col1.button('Clear'):
        cube.reset_filters('all')
        st.rerun()
        
    if col2.button('Undo'):
        cube.reset_filters('backward')
        st.rerun()
        
    if col3.button('Redo'):
        cube.reset_filters('forward')
        st.rerun()
    
    # Apply dimension filters    
    for dim in all_dims:
        filter(dim)

    # Display current filters
    st.write("Current Filters:")
    filters = cube.get_filters()
    if filters:
        for dim, vals in filters.items():
            if vals:
                clean_vals = list(vals)
                st.write(f"- **{dim}**: {', '.join(map(str, clean_vals))}")
            else:
                st.write(f"- **{dim}**: None")
    else:
        st.write("No filters applied.")

    

def plot(name: str, height: int = 400, use_container_width: bool = True, **kwargs: Any):
    """Wrapper to plot with error handling."""
    cube = get_cube()
    try:
        cube.plot(name, height=height, **kwargs)
    except Exception as e:
        st.error(f"Error plotting {name}: {e}")
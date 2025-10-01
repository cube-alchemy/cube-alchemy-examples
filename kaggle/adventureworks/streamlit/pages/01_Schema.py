import streamlit as st
from core.cube_factory import get_cardinallity, get_cube, ensure_schema_fig
from ui.components import render_sidebar_filters

st.set_page_config(page_title="AdventureWorks • Schema", layout="wide", initial_sidebar_state="expanded")

cube = get_cube()
render_sidebar_filters(cube)

st.header("Data Schema")
fig = ensure_schema_fig(cube)
if fig is not None:
    st.pyplot(fig)
else:
    st.info("Schema graph unavailable.")

st.header("Cardinalities")
get_cardinallity(cube)

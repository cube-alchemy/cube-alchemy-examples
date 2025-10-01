import streamlit as st
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters
import time

st.set_page_config(page_title="AdventureWorks • Visuals", layout="wide", initial_sidebar_state="expanded")

cube = get_cube()
render_sidebar_filters(cube)

queries = st.session_state.queries
# For each defined query, render its default plot in a 2-column grid
cols = st.columns(2)
tile_height = 320
print(f"\n\nRendering {len(queries)} plots\n")
t_start = time.time()
t = t_start
for i, q in enumerate(queries):    
    with cols[i % 2]:
        try:
            cube.plot(q, height=tile_height, use_container_width=True, show_title=False)
            # Log time taken for each plot
            t1 = time.time()
            print(f"Time taken for plot '{q}': {t1 - t:.3f} seconds")
            t = t1
        except Exception as e:
            try:
                st.write(f'Error rendering plot for query "{q}", rendering table instead: {e}')
                st.dataframe(cube.query(q), use_container_width=True, height=tile_height)
            except Exception as e2:
                st.error(f"Error fetching query '{q}': {e2}")
print(f"Total rendering time for {len(queries)} plots: {t - t_start:.3f} seconds\n")
import streamlit as st
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters
import time

import pandas as pd
pd.options.display.float_format = '{:.2f}'.format

st.set_page_config(page_title="PNL • Overview", layout="wide", initial_sidebar_state="expanded")

cube = get_cube()


if st.button('Load YAML'):
    cube.load_from_model_catalog()

queries = st.session_state.queries
# For each defined query, render its default plot in a n-column layout
n = 1
cols = st.columns(n)
tile_height = 320
print(f"\n\nRendering {len(queries)} plots\n")
t_start = time.time()
t = t_start
for i, q in enumerate(queries):    
    with cols[i % n]:
        try:
            cube.plot(q, height=tile_height, show_title=False)
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

render_sidebar_filters(cube)
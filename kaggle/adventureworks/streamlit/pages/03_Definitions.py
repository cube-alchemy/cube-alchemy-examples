import streamlit as st
import pandas as pd
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters

st.set_page_config(page_title="AdventureWorks • Definitions", layout="wide", initial_sidebar_state="expanded")

cube = get_cube()
render_sidebar_filters(cube)

st.header("Definitions")

st.markdown('#### Table: [Dimensions]')
for table in cube.input_tables_columns:
    st.write(f"{table}: {cube.input_tables_columns[table]}")

st.markdown('#### Metrics')
metrics_dict = cube.get_metrics()
if metrics_dict:
    metrics_list = [{'name': name, **details} for name, details in metrics_dict.items()]
    st.dataframe(pd.json_normalize(metrics_list), use_container_width=True)
else:
    st.info("No metrics defined.")

st.markdown('#### Derived Metrics')
derived_metrics_dict = cube.get_derived_metrics()
if derived_metrics_dict:
    derived_metrics_list = [{'name': name, **details} for name, details in derived_metrics_dict.items()]
    st.dataframe(pd.json_normalize(derived_metrics_list), use_container_width=True)
else:
    st.info("No derived metrics defined.")

st.markdown('#### Queries')
queries_dict = cube.get_queries()
if queries_dict:
    # only queries that are in session state
    queries_dict = {k: v for k, v in queries_dict.items() if k in st.session_state.queries}
    queries_list = [{'name': name, **details} for name, details in queries_dict.items()]
    st.dataframe(pd.json_normalize(queries_list), use_container_width=True)
else:
    st.info("No queries defined.")

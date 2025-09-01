import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
from cube_alchemy import Hypercube

from pathlib import Path
current_dir = Path.cwd()

import pickle
import numpy as np

@st.cache_resource  # Cache the loaded cube
def load_cube():
    with open("cube_pnl.pkl", "rb") as f:
        cube = pickle.load(f)
    
    # Restore the required functions that were removed for pickling
    cube.registered_functions = {
        'pd': pd,
        'np': np
    }

	# set Default context state
    cube.set_state('Default')

    return cube

# --- Build or reuse Hypercube ---
def get_cube():
	if 'cube' not in st.session_state:
		st.session_state.cube = load_cube()
		_define_metrics_and_queries(st.session_state.cube)
	return st.session_state.cube

def _define_metrics_and_queries(cube: Hypercube):

	def count_distinct(x):
		return x.nunique()
	
	# Base metrics

# --- UI helpers ---
def apply_filters(cube: Hypercube, criteria: Dict[str, List[str]]):
	cube.reset_filters('all')
	if criteria:
		cube.filter(criteria)

def bar_chart(df: pd.DataFrame, dims: List[str], measure: str, title: str):
	if df is None or df.empty:
		st.info('No data to plot.')
		return
	if len(dims) == 2:
		piv = df.pivot_table(index=dims[0], columns=dims[1], values=measure, fill_value=0)
		st.bar_chart(piv, height=360, stack=False)
	elif len(dims) == 1:
		s = df.set_index(dims[0])[measure]
		st.bar_chart(s, height=360)
	else:
		st.write("max 2 dimensions")


# --- App ---
st.set_page_config(page_title='Cube Alchemy • P&L example', layout='wide')
st.sidebar.title('P&L Explorer')
#st.caption('Minimal Streamlit app powered by cube_alchemy Hypercube')

cube = get_cube()
def _ensure_schema_fig(cube: Hypercube):
	if 'schema_fig' not in st.session_state:
		try:
			cube.visualize_graph(full_column_names=False)
			st.session_state['schema_fig'] = plt.gcf()
		except Exception as e:
			st.session_state['schema_fig'] = None
			st.warning(f'Unable to render schema graph: {e}')
_ensure_schema_fig(cube)

## Sidebar filters (choose dimensions, then values; options from Unfiltered state)
st.sidebar.header('Filters')
all_dims = cube.get_dimensions()
selected_dims = st.sidebar.multiselect('Filter dimensions', options=all_dims, key='filter_dims')

criteria: Dict[str, List[str]] = {}
for dim in selected_dims:
	try:
		vals = cube.dimensions([dim], context_state_name='Unfiltered')[dim]
		options = vals.dropna().sort_values().unique().tolist()
	except Exception:
		options = []
	picked = st.sidebar.multiselect(dim, options=options, key=f'flt_{dim}')
	if picked:
		criteria[dim] = picked

# Apply filters on every change to mirror the exact UI state
apply_filters(cube, criteria)

# Top navigation tabs
tab_schema, tab_on_the_fly, tab_defs, tab_visuals = st.tabs(["Schema", "On the fly Table", "Definitions", "Defined Queries Visuals"])

with tab_schema:
	st.subheader('Tables and relationships')
	# create a button to refresh schema fig
	if st.button('Refresh Schema'):
		try:
			cube.visualize_graph(full_column_names=False)
			st.session_state['schema_fig'] = plt.gcf()
		except Exception as e:
			st.session_state['schema_fig'] = None
			st.warning(f'Unable to render schema graph: {e}')
	if st.session_state.get('schema_fig') is not None:
		st.pyplot(st.session_state['schema_fig'])
	else:
		st.info('Schema graph not available.')

with tab_on_the_fly:
	st.subheader('On the fly Table')
	ad_hoc_dims = st.multiselect('Dimensions', options=all_dims, key='ad_hoc_dims')
	ad_hoc_metrics = st.multiselect('Metrics', options=list(cube.metrics.keys()), key='ad_hoc_metrics')
	ad_hoc_derived_metrics = st.multiselect('Derived Metrics', options=list(cube.derived_metrics.keys()), key='ad_hoc_derived_metrics')
	if ad_hoc_dims or ad_hoc_metrics or ad_hoc_derived_metrics:
		cube.define_query(
			name="(temp) Ad Hoc Query",
			dimensions=ad_hoc_dims,
			metrics=ad_hoc_metrics,
			derived_metrics=ad_hoc_derived_metrics,
			#drop_null_dimensions=True
		)
		st.write(cube.query("(temp) Ad Hoc Query"))

with tab_defs:

    #st.markdown('#### Filters (current state)')
    #st.json(cube.get_filters())

    st.markdown('#### Table: [Dimensions]')
    for table in cube.input_tables_columns:
        st.write(f"{table}: {cube.input_tables_columns[table]}")
    #st.markdown(markdown_list)

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
        # Convert dict of queries into a list of dicts and add the name
        queries_list = [{'name': name, **details} for name, details in queries_dict.items()]
        st.dataframe(pd.json_normalize(queries_list), use_container_width=True)
    else:
        st.info("No queries defined.")

with tab_visuals:
	# Query selection
	queries = list(cube.queries.keys())
	q = st.selectbox('Query', options=queries, index=0)
	q_def = cube.get_query(q)

	# Results
	res = cube.query(q)

	# Charts for each metric in the selected query
	st.subheader('Charts (only showing bar chart and underlying table for this example)')
	dims = q_def['dimensions']
	for m in q_def['metrics'] + q_def['derived_metrics']:
		st.markdown(f'**{m}**')
		bar_chart(res, dims, m, q)

	st.subheader('Result table')
	st.dataframe(res, use_container_width=True)

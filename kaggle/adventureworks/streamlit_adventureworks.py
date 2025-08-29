import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
from cube_alchemy import Hypercube

# --- Load data (AdventureWorks dummy) ---
def _clean_currency(x):
	if isinstance(x, str):
		return float(x.replace('$', '').replace(',', ''))
	return x

@st.cache_data(show_spinner=False)
def load_tables():
	def clean_currency(x):
		if isinstance(x,str):
			return float(x.replace('$', '').replace(',', ''))
		else:
			return x
	# Load tables
	tables = {}
	for table in ['Product', 'Region', 'Reseller', 'Sales', 'Salesperson']:
		url = f"https://raw.githubusercontent.com/cube-alchemy/cube-alchemy-examples/main/kaggle/adventureworks/Source/{table}.csv"
		df = pd.read_csv(url, sep='\t')
		for columns in ['Unit Price', 'Cost']:
			if columns in df.columns:
				df[columns] = df[columns].apply(clean_currency)
		tables[table] = df
	return tables

# --- Build or reuse Hypercube ---
def get_cube():
	if 'cube' not in st.session_state:
		st.session_state.cube = Hypercube(load_tables())
		_define_metrics_and_queries(st.session_state.cube)
	return st.session_state.cube

def _define_metrics_and_queries(cube: Hypercube):

	def count_distinct(x):
		return x.nunique()
	
	# Base metrics
	cube.define_metric(name='Revenue', expression='[Unit Price] * [Quantity]', aggregation='sum')
	cube.define_metric(name='Unfiltered Revenue', expression='[Unit Price] * [Quantity]', aggregation='sum', context_state_name='Unfiltered')
	cube.define_metric(name='Cost',    expression='[Cost]',                 aggregation='sum')
	cube.define_metric(name='avg Unit Price', expression='[Unit Price]',    aggregation='mean')
	cube.define_metric(name='number of Orders', expression='[SalesOrderNumber]', aggregation=count_distinct)

	# Or..
	import copy
	cube.metrics['Total Revenue'] = copy.deepcopy(cube.metrics['Revenue'])
	cube.metrics['Total Revenue'].name = 'Total Revenue'
	cube.metrics['Total Revenue'].ignore_dimensions = True

	# Computed metrics (post-aggregation)
	cube.define_computed_metric(name='Margin', expression='[Revenue] - [Cost]')
	cube.define_computed_metric(name='Margin %', expression='100 * ([Revenue] - [Cost]) / [Revenue]')
	cube.define_computed_metric(name='Revenue over Total', expression='[Revenue] / [Total Revenue]')

	# Queries
	cube.define_query(
		name='Sales by Region and Category',
		metrics=['Revenue'],
		computed_metrics=['Revenue over Total','Margin %'],
		dimensions=['Region', 'Category'],
		drop_null_dimensions=True,
		sort=[('Revenue', 'desc')]
	)

	cube.define_query(
		name='avg Unit Price by Category & Business Type',
		metrics=['avg Unit Price'],
		dimensions=['Category', 'Business Type'],
		drop_null_dimensions=True
	)

	cube.define_query(
		name='High-Margin Products (>35%)',
		metrics=['number of Orders'],
		computed_metrics=['Margin'],
		dimensions=['Product'],
		having='[Margin %] >= 35',
		drop_null_dimensions=True,
		sort=[('Margin', 'desc')]
	)

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
st.set_page_config(page_title='Cube Alchemy • AdventureWorks', layout='wide')
st.sidebar.title('AdventureWorks Explorer')
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
	if st.session_state.get('schema_fig') is not None:
		st.pyplot(st.session_state['schema_fig'])
	else:
		st.info('Schema graph not available.')

with tab_on_the_fly:
	st.subheader('On the fly Table')
	ad_hoc_dims = st.multiselect('Dimensions', options=all_dims, key='ad_hoc_dims')
	ad_hoc_metrics = st.multiselect('Metrics', options=list(cube.metrics.keys()), key='ad_hoc_metrics')
	ad_hoc_computed_metrics = st.multiselect('Computed Metrics', options=list(cube.computed_metrics.keys()), key='ad_hoc_computed_metrics')
	if ad_hoc_dims or ad_hoc_metrics or ad_hoc_computed_metrics:
		cube.define_query(
			name="(temp) Ad Hoc Query",
			dimensions=ad_hoc_dims,
			metrics=ad_hoc_metrics,
			computed_metrics=ad_hoc_computed_metrics,
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

    st.markdown('#### Computed Metrics')
    computed_metrics_dict = cube.get_computed_metrics()
    if computed_metrics_dict:
        computed_metrics_list = [{'name': name, **details} for name, details in computed_metrics_dict.items()]
        st.dataframe(pd.json_normalize(computed_metrics_list), use_container_width=True)
    else:
        st.info("No computed metrics defined.")
	
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
	for m in q_def['metrics'] + q_def['computed_metrics']:
		st.markdown(f'**{m}**')
		bar_chart(res, dims, m, q)

	st.subheader('Result table')
	st.dataframe(res, use_container_width=True)

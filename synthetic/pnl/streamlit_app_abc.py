import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
from cube_alchemy import Hypercube
from cube_alchemy.plotting import StreamlitRenderer

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
    cube.set_context_state('Default')
    
    # Define plot configurations for queries
    cube.define_plot(
        query_name='PNL',
        plot_name='default',
        plot_type='bar',
        dimensions=['pnl_report_line'],
        metrics=['Amount Actual'],
        orientation='horizontal',
        title='P&L Actual Amount',
        sort_values=True,
        sort_ascending=False
    )
    
    # Define alternate plot views
    cube.define_plot(
        query_name='PNL',
        plot_name='comparison',
        plot_type='bar',
        dimensions=['pnl_report_line'],
        metrics=['Amount Actual'],
        color_by=None,  # Can be set to a dimension if available
        title='Budget vs. Actual Comparison',
        orientation='horizontal',
        sort_values=True,
        sort_ascending=False,
        set_as_default=False
    )
    
    cube.define_plot(
        query_name='PNL',
        plot_name='variance',
        plot_type='bar',
        dimensions=['pnl_report_line'],
        metrics=['difference'],
        title='P&L Variance',
        orientation='horizontal',
        sort_values=True,
        sort_ascending=False,
        set_as_default=False
    )

    return cube

# --- Build or reuse Hypercube ---
def get_cube():
    if 'cube' not in st.session_state:
        st.session_state.cube = load_cube()
        _define_metrics_and_queries(st.session_state.cube)
    return st.session_state.cube

def _define_metrics_and_queries(cube: Hypercube):
    # Add any additional metrics or queries here if needed
    pass

# --- UI helpers ---
def apply_filters(cube: Hypercube, criteria: Dict[str, List[str]]):
    cube.reset_filters('all')
    if criteria:
        cube.filter(criteria)

# --- App ---
st.set_page_config(page_title='Cube Alchemy • P&L example', layout='wide')
st.sidebar.title('P&L Explorer')

# Initialize the renderer
streamlit_renderer = StreamlitRenderer()

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
            derived_metrics=ad_hoc_derived_metrics
        )
        st.write(cube.query("(temp) Ad Hoc Query"))

with tab_defs:
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
    
    # Get available plot configurations for this query
    available_plots = cube.list_plots(q)
    
    if available_plots:
        # Let user select from available plot configurations
        selected_plot = st.selectbox(
            'Plot Configuration', 
            options=available_plots, 
            index=0 if 'default' in available_plots else 0
        )
    else:
        selected_plot = None
    
    st.subheader('Visualization')
    
    # Get plot configuration (either selected or auto-created)
    try:
        plot_config = cube.get_plot_config(q, selected_plot)
        
        # Allow customization of the plot
        with st.expander("Customize Plot"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Plot type
                plot_type = st.selectbox(
                    'Plot Type', 
                    options=['bar', 'line', 'scatter', 'pie', 'area', 'heatmap'], 
                    index=['bar', 'line', 'scatter', 'pie', 'area', 'heatmap'].index(plot_config.get('plot_type', 'bar'))
                )
                
                # Dimensions selection (multi)
                dims_all = q_def.get('dimensions', [])
                default_dims = plot_config.get('dimensions') or dims_all
                sel_dims = st.multiselect('Dimensions', options=dims_all, default=default_dims)
                
                # Color by dimension
                if len(dims_all) >= 1:
                    color_options = [None] + dims_all
                    color_index = 0
                    if plot_config.get('color_by') in dims_all:
                        color_index = color_options.index(plot_config.get('color_by'))
                    color_by = st.selectbox('Color by', options=color_options, index=color_index)
                else:
                    color_by = None
                
            with col2:
                # Metrics selection (multi)
                metrics_all = (q_def.get('metrics', []) or []) + (q_def.get('derived_metrics', []) or [])
                default_metrics = plot_config.get('metrics') or metrics_all[:1]
                sel_metrics = st.multiselect('Metrics', options=metrics_all, default=default_metrics)
                
                # Orientation
                orientation = st.selectbox(
                    'Orientation', 
                    options=['vertical', 'horizontal'], 
                    index=['vertical', 'horizontal'].index(plot_config.get('orientation', 'vertical'))
                )
                
                # Sort values
                sort_values = st.checkbox('Sort by Value', value=plot_config.get('sort_values', False))
                if sort_values:
                    sort_ascending = st.checkbox('Ascending Sort', value=plot_config.get('sort_ascending', True))
                else:
                    sort_ascending = plot_config.get('sort_ascending', True)
        
        # Plot with the configured or customized options
        cube.plot(
            q, 
            renderer=streamlit_renderer,
            plot_name=selected_plot,
            plot_type=plot_type,
            dimensions=sel_dims,
            metrics=sel_metrics,
            color_by=color_by,
            orientation=orientation,
            sort_values=sort_values,
            sort_ascending=sort_ascending
        )
    except ValueError as e:
        st.warning(f"No plot configuration available: {e}")
        
        # Create a simple bar chart with default options
        st.bar_chart(res)

    st.subheader('Result table')
    st.dataframe(res, use_container_width=True)

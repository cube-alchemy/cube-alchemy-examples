import streamlit as st
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters
import uuid

st.set_page_config(page_title="AdventureWorks • On the fly", layout="wide", initial_sidebar_state="expanded")

cube = get_cube()
render_sidebar_filters(cube)
all_dims = cube.get_dimensions()

st.header("On the fly Plot")
ad_hoc_dims = st.multiselect('Dimensions', options=all_dims, key='ad_hoc_dims')
ad_hoc_metrics = st.multiselect('Metrics', options=list(cube.metrics.keys()), key='ad_hoc_metrics')
ad_hoc_derived_metrics = st.multiselect('Derived Metrics', options=list(cube.derived_metrics.keys()), key='ad_hoc_derived_metrics')

null_dims = st.checkbox('Drop Null Dimensions', value=True, key='ad_hoc_null_dims')

if ad_hoc_dims or ad_hoc_metrics or ad_hoc_derived_metrics:
    # get an uuid for this query
    query_id = uuid.uuid4()
    q_name = f'Ad Hoc Query ({query_id})'
    cube.define_query(
        name= q_name,
        dimensions=ad_hoc_dims,
        metrics=ad_hoc_metrics,
        derived_metrics=ad_hoc_derived_metrics,
        drop_null_dimensions=null_dims
    )

    n_dim = len(ad_hoc_dims)
    n_met = len(ad_hoc_metrics) + len(ad_hoc_derived_metrics)

    suggested_plots = ['table']
    for conf_item in cube._config_resolver.suggest(n_dim,n_met):
        if not conf_item['plot_type'] == 'table':
            suggested_plots.append(conf_item['plot_type'])
    
    ad_hoc_plot_type = st.selectbox('Plot Type', options=suggested_plots, key='ad_hoc_plot_type')

    if ad_hoc_plot_type in ['bar']:
        stacked = st.checkbox('Stacked', value=True, key='ad_hoc_stacked')

        cube.plot(q_name, plot_type = ad_hoc_plot_type, stacked = stacked)
    else:
        cube.plot(q_name, plot_type = ad_hoc_plot_type)

    # add a button to persist this query
    if st.button('Save Plot (add to Visuals page)', key='persist_ad_hoc_query'):
        st.session_state.queries.append(q_name)
else:
    st.info("Pick any dimension and metric to preview a table.")



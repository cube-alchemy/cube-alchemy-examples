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

# Track active selections to determine if we need a new query id (only when non-empty selections first appear or change)
prev_signature = st.session_state.get('ad_hoc_active_signature')
current_signature = (tuple(ad_hoc_dims), tuple(ad_hoc_metrics), tuple(ad_hoc_derived_metrics))
selection_changed = current_signature != prev_signature
if selection_changed and (ad_hoc_dims or ad_hoc_metrics or ad_hoc_derived_metrics):
    st.session_state['ad_hoc_query_name'] = f"Ad Hoc Query ({uuid.uuid4()})"
    st.session_state['ad_hoc_active_signature'] = current_signature

q_name = st.session_state.get('ad_hoc_query_name')

null_dims = st.checkbox('Drop Null Dimensions', value=True, key='ad_hoc_null_dims')

if (ad_hoc_dims or ad_hoc_metrics or ad_hoc_derived_metrics) and q_name:
    # (Re)define the query each run so underlying filters apply, but reuse stable name for same selections.
    cube.define_query(
        name=q_name,
        dimensions=ad_hoc_dims,
        metrics=ad_hoc_metrics,
        derived_metrics=ad_hoc_derived_metrics,
        drop_null_dimensions=null_dims
    )

    n_dim = len(ad_hoc_dims)
    n_met = len(ad_hoc_metrics) + len(ad_hoc_derived_metrics)

    # Build suggestion list
    suggested_plots = ['table']
    for conf_item in cube._config_resolver.suggest(n_dim, n_met):
        pt = conf_item['plot_type']
        if pt != 'table' and pt not in suggested_plots:
            suggested_plots.append(pt)

    # Retrieve previously persisted user choice (independent from widget key which Streamlit may overwrite)
    persisted_plot_choice = st.session_state.get('ad_hoc_plot_type_user')
    # Also capture immediate widget state from a prior run before suggestions might have removed it
    current_widget_plot = st.session_state.get('ad_hoc_plot_type')
    preferred_prev_plot = persisted_plot_choice or current_widget_plot

    # If the previously chosen plot type was dropped by new suggestion logic, reinsert it (front for visibility)
    if preferred_prev_plot and preferred_prev_plot not in suggested_plots:
        suggested_plots.insert(0, preferred_prev_plot)

    ad_hoc_plot_type = st.selectbox('Plot Type', options=suggested_plots, key='ad_hoc_plot_type', index=suggested_plots.index(preferred_prev_plot) if preferred_prev_plot in suggested_plots else 0)
    # Persist user plot selection separately so it survives a rerun where widget value might be auto-changed
    st.session_state['ad_hoc_plot_type_user'] = ad_hoc_plot_type

    if ad_hoc_plot_type in ['bar']:
        stacked = st.checkbox('Stacked', value=True, key='ad_hoc_stacked')

        cube.define_plot(q_name, plot_type = ad_hoc_plot_type, stacked = stacked)
    else:
        cube.define_plot(q_name, plot_type = ad_hoc_plot_type)
    
    cube.plot(q_name)
    
    

    # add a button to persist this query
    if st.button('Save Plot (add to Visuals page)', key='persist_ad_hoc_query'):
        st.session_state.queries.append(q_name)
else:
    st.info("Pick any dimension and metric to preview a table.")



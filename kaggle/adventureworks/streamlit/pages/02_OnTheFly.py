import streamlit as st
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters
import uuid

st.set_page_config(page_title="AdventureWorks • On the fly", layout="wide", initial_sidebar_state="expanded")

cube = get_cube()
render_sidebar_filters(cube)
all_dims = cube.get_dimensions()

st.header("On the fly Plot")

# --- Persistence Strategy ---
# We separate the widget key (ui_*) from the stored canonical selection (*_store) so if a
# manual st.rerun() happens elsewhere mid-cycle (e.g., sidebar), we still retain last
# committed selection.

def _persisted_multiselect(label: str, options: list[str], store_key: str, widget_key: str):
    
    st.session_state.setdefault(store_key, [])
    # first render: push stored value (so UI shows previous) via default if widget not yet created
    # Using a distinct widget key prevents Streamlit from overriding default after initial creation.
    current_ui = st.multiselect(label, options=options, default=st.session_state[store_key], key=widget_key)

    # Normal path: update store
    st.session_state[store_key] = list(current_ui)
    return st.session_state[store_key]

ad_hoc_dims = _persisted_multiselect('Dimensions', all_dims, 'ad_hoc_dims_store', 'ad_hoc_dims_widget')
ad_hoc_metrics = _persisted_multiselect('Metrics', list(cube.metrics.keys()), 'ad_hoc_metrics_store', 'ad_hoc_metrics_widget')
ad_hoc_derived_metrics = _persisted_multiselect('Derived Metrics', list(cube.derived_metrics.keys()), 'ad_hoc_derived_metrics_store', 'ad_hoc_derived_metrics_widget')




q_name = f"Ad Hoc Query ({uuid.uuid4()})"

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





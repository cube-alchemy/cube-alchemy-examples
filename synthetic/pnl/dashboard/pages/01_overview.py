import streamlit as st
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters, plot

# Configure page settings
st.set_page_config(
    page_title="PNL • Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header("Overview")

cube = get_cube()


kpi_cols_a = st.columns(2)
with kpi_cols_a[0]:
    plot('Revenue')
with kpi_cols_a[1]:
    plot('Net Income')
kpi_cols_b = st.columns(3)
with kpi_cols_b[0]:
    plot('Gross Margin %')
with kpi_cols_b[1]:
    plot('EBITDA Margin %')
with kpi_cols_b[2]:
    plot('Net Income Margin %')



ov_cols = st.columns(2)
with ov_cols[0]:
    plot('Core Metrics Over Time')
with ov_cols[1]:
    plot('Variation in Amount by Year Quarter')


# Add filters in sidebar
with st.sidebar:
    render_sidebar_filters()
import streamlit as st
from ui.components import render_sidebar_filters, plot, filter

# Configure page settings
st.set_page_config(
    page_title="PNL • Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header("Profit & Loss Analysis")

# create 3 columns for kpis
kpi_cols = st.columns(3)
with kpi_cols[0]:
    plot('Gross Margin %')
with kpi_cols[1]:
    plot('EBITDA Margin %')
with kpi_cols[2]:
    plot('Net Income Margin %')

filters_page = ['segment', 'business_unit', 'country','pnl_account_name']
filter_cols = st.columns(4)
for i, dim in enumerate(filters_page):
    with filter_cols[i]:
        filter(dim)
        
plot('P&L by Year Quarter', height=430, use_container_width=True, show_title=False)
plot('Amount by Account detail')
plot('P&L by account detail')


# Add filters in sidebar
with st.sidebar:
    render_sidebar_filters()
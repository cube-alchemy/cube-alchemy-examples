import streamlit as st
from core.cube_factory import get_cube
from ui.components import render_sidebar_filters, plot,load_yaml_button

# Configure page settings
st.set_page_config(
    page_title="PNL • Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

cube = get_cube()
cube.remove_filter(['segment', 'country','pnl_account_name'])

#load_yaml_button()
st.header("Budget Performance Analysis")
st.markdown("""
This section provides a detailed variance analysis comparing actual financial results against budgeted targets.
These comparisons help identify areas of over/underperformance and provide insights for future planning.
Select one or more PNL categories from the sidebar to filter to compare actuals vs budget trends for those specific categories.
""")

plot('Budget vs Actual by Month', height=430, use_container_width=True, show_title=False)
plot('Budget vs Actual Overview by division', height=430, use_container_width=True, show_title=False)


plot('Profit and Loss Budget vs Actual Overview by P&L line', height=430)
plot('Profit and Loss Budget vs Actual by Account Category and Account Name', height=430)

# Add filters in sidebar
with st.sidebar:
    render_sidebar_filters()

import streamlit as st
from core.cube_factory import get_cube, ensure_schema_fig
from ui.components import render_sidebar_filters

# Configure page settings
st.set_page_config(
    page_title="PNL • Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Get cube for the main page
cube = get_cube()

st.title("Financial Performance Dashboard")
st.caption("Interactive financial analytics powered by CubeAlchemy")

st.markdown("""
## Welcome to Your Financial Command Center

This dashboard provides comprehensive insights into your company's financial performance through basic 
Profit & Loss (P&L) analysis. Track revenue, monitor expenses, and analyze profitability metrics 
across different business dimensions.

Use the **navigation menu** on the left to explore different perspectives, and apply **filters** to focus on specific business units, time periods, regions, and more.
""")

# Display the data model visualization
st.header("Data Model")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("""
    The visualization on the right shows how our financial data is structured and connected:
    
    - **Fact Tables**: Contain actual financial transactions and budget aggregated at various (different) grain levels.
    - **Dimension Tables**: Provide context for analysis (time, accounts, business units, etc.)
    - **Connecting Lines**: Show how different data elements relate to each other
                
    Understanding this model helps in interpreting the reports and ensuring accurate analysis.
    """)
    

with col2:
    fig = ensure_schema_fig(cube)
    if fig is not None:
        st.pyplot(fig, use_container_width=True)
    else:
        st.warning("Data model visualization unavailable in this session.")
        
if st.button('Load YAML'):
    cube.load_from_model_catalog()
# Explain the key metrics
st.header("Key Financial Metrics Explained")
metrics_tab1, metrics_tab2, metrics_tab3, metrics_tab4 = st.tabs(["Performance Indicators", "Variance Metrics", "Profitability Ratios","Detailed Definitions"])

with metrics_tab1:
    st.markdown("""
    ### Core Performance Indicators
    
    | Metric | Description | Business Impact |
    | ------ | ----------- | -------------- |
    | **Amount Actual** | Actual financial figures recorded in the accounting system | Represents real financial performance |
    | **Amount Budget** | Planned or forecasted financial targets | Sets expectations for financial outcomes |
    | **Revenue Actual** | Actual income generated from business activities | Primary indicator of top-line growth |
    | **EBITDA Actual** | Earnings Before Interest, Taxes, Depreciation & Amortization | Indicates operational profitability |
                
    **Note**: Amount Actual represents the summation of all income and expenses given the current filter selection, if no account (pnl_report_line, pnl_category or pnl_account_detail) filter is applied then it will be same as the Net Income. You can use these filters to look at the figures for specific categories like Revenue, Expenses, etc.
    """)

with metrics_tab2:
    st.markdown("""
    ### Variance Analysis
    
    | Metric | Description | Business Impact |
    | ------ | ----------- | -------------- |
    | **Difference (Budget vs. Actual)** | Actual minus Budget (A-B) | Shows absolute variance from plan |
    | **Percentage Difference (Budget vs. Actual)** | (A-B)/B as a percentage | Shows relative variance, normalizing for size |
    | **Variation (Actual)** | Period-over-period change | Highlights trends and growth patterns |
    
    Positive variances in revenue and negative variances in expenses are generally favorable.
    """)

with metrics_tab3:
    st.markdown("""
    ### Key Financial Ratios
    
    | Ratio | Formula | Business Significance |
    | ----- | ------- | -------------------- |
    | **Gross Margin %** | Gross Margin / Revenue | Efficiency in core production/service delivery |
    | **EBITDA Margin %** | EBITDA / Revenue | Operational efficiency before capital structure impacts |
    | **Net Income Margin %** | Net Income / Revenue | Overall profitability as percentage of revenue |
    
    These ratios allow for comparison across different time periods and business units regardless of absolute size.
    
    Bear in mind that the account category and report line filters impact these ratios(e.g., Net Income is just the Amount of all accounts, if any filter is applied it will be the sum of the filtered accounts). Use filters to analyze specific segments of your financial data.
    """)

with metrics_tab4:
    import pandas as pd
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

# Dashboard sections explained
st.header("Dashboard Sections")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Overview")
    st.markdown("""
    The **Overview** page provides an executive summary of financial performance:
    
    - **Key Performance Indicators (KPIs)**: Snapshot of critical financial ratios
    - **Period-over-Period Trends**: Shows how financial figures change over time
    - **Core Metrics Timeline**: Visualizes absolute and percentage metrics together
    
    This page answers: "How is our overall financial health trending?"
    """)
    
    st.subheader("2. Profit & Loss Analysis")
    st.markdown("""
    The **Profit & Loss Analysis** page offers a comprehensive view of key financial figures:

    - **KPIs**: Gross Margin %, EBITDA Margin %, Net Income Margin %
    - **Quarterly Trends**: EBITDA Actual by Quarter by Business Unit
    - **Category & Country Breakdowns**: Actual by Account Category and Actual by Country
    - **Margin Insights**: Gross Margin by Quarter by Business Unit

    This page answers: "How are our core financial metrics evolving across different categories and regions?"
    """)

with col2:
    st.subheader("3. Profit & Loss by Account")
    st.markdown("""
    The **Profit & Loss by Account** page dives into the income statement at the account level:

    - **KPIs**: Gross Margin %, EBITDA Margin %, Net Income Margin %
    - **Account-Level Trends**: P&L by Year Quarter
    - **Detailed Drilldowns**: Amount by Account detail and P&L by account detail

    This page answers: "Which accounts are driving our financial results and trends over time?"
    """)
    
    st.subheader("4. Actual vs Budget")
    st.markdown("""
    The **Actual vs Budget** page focuses on variance analysis:
    
    - **Monthly Variance**: Compares actual vs budget figures across time periods
    - **Full P&L Comparison**: Line-by-line comparison of actual vs budget
    - **Divisional Performance**: How each division is performing against targets
    
    This page answers: "Are we meeting our financial targets, and where are the gaps?"
    """)
    
    st.markdown("""
    ### Using Filters
    
    The sidebar contains filters that apply across all dashboard pages:
    
    - **Time Period**: Focus on specific months, quarters, or years
    - **Business Unit**: Isolate performance for specific divisions
    - **Location**: Analyze performance by geographic region
    
    Applying filters helps identify specific patterns in your financial data.
    """)

# Add filters in sidebar
with st.sidebar:
    st.header("Global Filters")
    render_sidebar_filters()

if __name__ == "__main__":
    pass  # Main code is now at module level

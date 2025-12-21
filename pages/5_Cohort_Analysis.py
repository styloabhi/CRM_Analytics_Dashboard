import streamlit as st
# 🔐 Page security check
if st.session_state["authentication_status"] != True:
    st.error("Please login first.")
    st.stop()

# importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from millify import millify


# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(
    page_title="Cohort Analysis Dashboard",
    page_icon="🕛",
    layout='wide'
)


# ----------------------------
# SIDEBAR THEME STYLE
# ----------------------------
st.markdown("""
<style>

[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #08142c, #0a182f, #0d1e3b);
    color: white;
    padding: 20px;
}

[data-testid="stSidebar"] * {
    color: white !important;
    font-size: 15px;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 20px;
}

.sidebar-label {
    font-size: 16px;
    font-weight: 600;
    color: #9db7d6 !important;
    margin-top: 18px;
    margin-bottom: 5px;
}

div[data-baseweb="select"] > div {
    background-color: #132240 !important;
    border-radius: 10px !important;
    border: 1px solid #3c4f70 !important;
    color: white !important;
}

span[data-baseweb="tag"] {
    background-color: #5e82ff !important;
    color: white !important;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)





# ----------------------------
# HEADER
# ----------------------------
col_logo, col_title = st.columns([1,4])

with col_logo:
    st.image('Resources/logo.jpeg', width=140)

with col_title:
    st.markdown(
        """
        <h1 style='font-size:48px; font-weight:900; margin-bottom:0; color:#1A2A40;'>
            🕛 Cohort Analysis Dashboard
        </h1>
        <p style='font-size:20px; color:#5a6a81; font-weight:500;'>
            Customer Retention Patterns Across Acquisition Cohorts
        </p>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# LOAD DATA
# ----------------------------
cr = pd.read_csv("../crm_streamlit_app/Resources/cohort_raw.csv")
cr['cohort_month'] = pd.to_datetime(cr['cohort_month'],format = '%d-%m-%Y')
cr = cr.sort_values('cohort_month',ascending = True).reset_index(drop = True)

cr['month_num'] = cr['cohort_month'].dt.month
cr['month_name'] = cr['cohort_month'].dt.month_name()

cr['month_year'] = cr['cohort_month'].dt.strftime('%b %Y')

# ----------------------------
# CREATE SLICER LISTS
# ----------------------------
month_list = (
    cr[['cohort_month','month_year']]
    .dropna()
    .drop_duplicates()
    .sort_values('cohort_month')['month_year']
    .tolist()
)

month_s = sorted(cr['month_since_acquisition'].dropna().unique())


# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
with st.sidebar:

    st.image("Resources/logo.jpeg", width=140)

    st.markdown("<div class='sidebar-title'>📊 FILTER PANEL</div>", unsafe_allow_html=True)

    # ------------------ MONTH SLICER ------------------
    st.markdown("<div class='sidebar-label'>📅 Select Cohort Month</div>", unsafe_allow_html=True)
    selected_months = st.multiselect("Select Cohort Month", month_list)
    if not selected_months:
        selected_months = month_list

    # ------------------ Agent SLICER ------------------
    st.markdown("<div class='sidebar-label'>👨‍💼 Select Month Since Acquisition</div>", unsafe_allow_html=True)
    selected_month_s = st.multiselect("Select Month", month_s)
    if not selected_month_s:
        selected_month_s = month_s


# ----------------------------
# APPLY FILTERS
# ----------------------------
filtered = cr[
    cr["month_name"].isin(selected_months) &
    cr["month_since_acquisition"].isin(selected_month_s)
]


# ----------------------------
# KPI VALUES
# ----------------------------
Total_Revenue = filtered['total_revenue_cohort_customers'].max()
if pd.isna(Total_Revenue):
    Total_Revenue_Display = "$0"
else:
    Total_Revenue_Display = "$" + millify(Total_Revenue, precision=2)


avg_month_repeat = filtered['avg_months_to_repeat'].max()
repeat_purchase = (filtered['retention_rate'].max()) * 100
repeat_customer = filtered['repeat_customers'].max()
cohort_size = filtered['cohort_customers'].max()





# ------------------------------------------
# VISUALS
# ------------------------------------------

# ------------------------------------------
# Cohort Analysis
# ------------------------------------------

cohort_pivot = (
    cr.pivot_table(
        index='cohort_month',
        columns='month_since_acquisition',
        values='retention_by_month',
        aggfunc='max'        
    )
    .round(2)
)


cohort_style = (
    cohort_pivot.style
    .background_gradient(cmap='Greens')
    .format("{:.2f}")
)


st.subheader("📊 Cohort Analysis Table")
st.dataframe(cohort_style, use_container_width=True)

col1, col2 = st.columns(2)
# ------------------------------------------
# Cohort Size
# ------------------------------------------
crco = cr.groupby('month_year')['cohort_customers'].max().reset_index().sort_values('month_year',ascending= True)

fig = px.bar(
    crco,
    x = 'month_year',
    y = 'cohort_customers',
    title= 'Cohort Size',
    text_auto= True,
    color_discrete_sequence= px.colors.qualitative.Set2
)
fig.update_layout(
    xaxis_title="Cohort Month",
    yaxis_title="Customers Acquired"
)
with col1:
    st.header("🕛 Cohort Size by Each Cohort Month")
    st.plotly_chart(fig,use_container_width= True)

# ---------------------------------------   ---
# cohort revenue trend
# ------------------------------------------


crcr = cr.groupby('month_year')['total_revenue_cohort_customers'].max().reset_index().sort_values('month_year',ascending= True)
fig = px.line(crcr,
              x = 'month_year',
              y = 'total_revenue_cohort_customers',
              markers = True,
              color_discrete_sequence=px.colors.qualitative.Set2)
with col2:
    st.subheader("💰 Cohort Revenue Trend")
    st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# Retention curve
# ------------------------------------------

ret = (
    cr.groupby(['month_year', 'month_since_acquisition'], as_index=False)
      .agg(retention_by_month=('retention_by_month', 'max'))
      .sort_values(['month_year', 'month_since_acquisition'])
)

fig = px.line(
    ret,
    x='month_since_acquisition',
    y='retention_by_month',
    color='month_year',      
    markers=True,
    title='Retention Curve'
)

fig.update_layout(
    xaxis_title='Month Since Acquisition',
    yaxis_title='Retention Rate',
    yaxis=dict(range=[0, 1.05]),
    legend_title='month_year'
)


st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# Average month to Repeat
# ------------------------------------------
col3, col4 = st.columns(2)

cr_avg = (
    cr.groupby(['month_year'], as_index=False)['avg_months_to_repeat']
      .max()
      .sort_values('month_year')
)

fig = px.pie(
    cr_avg,
    names='month_year',                 
    values='avg_months_to_repeat',     
    title='Avg Months to Repeat by Cohort',
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.3                            
)
fig.update_traces(
    textinfo='percent+label',
    pull=[0.05]*len(cr_avg)  
)

with col3:
    st.plotly_chart(fig, use_container_width=True)



# ------------------------------------------
# Repeat Purchase Analysis
# ------------------------------------------

col5, col6 = st.columns(2)
cr_repeat = (
    cr.groupby('month_year', as_index=False)['repeat_customers']
      .max()
      .sort_values('month_year')
)


fig = px.bar(
    cr_repeat,
    x='month_year',
    y='repeat_customers',
    title='Repeat Purchase Analysis by Cohort',
    text_auto=True,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_layout(
    xaxis_title='Cohort Month',
    yaxis_title='Repeat Customers'
)
with col4:
    st.plotly_chart(fig, use_container_width=True)




st.subheader("📄 Raw Data")
st.dataframe(cr)
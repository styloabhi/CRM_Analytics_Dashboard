
#-------------------------------------
# checking login
#-------------------------------------

import streamlit as st
# 🔐 Page security check
if st.session_state["authentication_status"] != True:
    st.error("Please login first.")
    st.stop()

#-------------------------------------
# importing libraries
#-------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from millify import millify


# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(
    page_title="Product 360 Dashboard",
    page_icon="💼",
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
# KPI CARD STYLE
# ----------------------------
st.markdown("""
<style>
.kpi-box {
    background: rgba(255,255,255,0.20);
    backdrop-filter: blur(8px);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.3);
}
.kpi-title {
    font-size: 18px;
    font-weight: 600;
    color:#2A3E5C;
}
.kpi-value {
    font-size: 32px;
    font-weight: bold;
    color:#1A2A40;
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
            💼 Product 360 Dashboard
        </h1>
        <p style='font-size:20px; color:#5a6a81; font-weight:500;'>
            Comprehensive Performance View Across All Products.
        </p>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# LOAD DATA
# ----------------------------
pr360 = pd.read_csv("Resources/product_360.csv")
pr360['first_engage_date'] = pd.to_datetime(pr360['first_engage_date'],format = '%d-%m-%Y')
pr360['last_close_date']= pd.to_datetime(pr360['last_close_date'],format = '%d-%m-%Y')

pr360['month_num'] = pr360['first_engage_date'].dt.month
pr360['month_name'] = pr360['first_engage_date'].dt.month_name()


# ----------------------------
# CREATE SLICER LISTS
# ----------------------------

month_list = (
    pr360[['month_num','month_name']]
    .dropna()
    .drop_duplicates()
    .sort_values("month_num")["month_name"]
    .tolist()
)

product_list = sorted(pr360['product'].dropna().unique())
series_list = sorted(pr360['series'].dropna().unique())


# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
with st.sidebar:

    st.image("Resources/logo.jpeg", width=140)

    st.markdown("<div class='sidebar-title'>📊 FILTER PANEL</div>", unsafe_allow_html=True)

    # ------------------ MONTH SLICER ------------------
    st.markdown("<div class='sidebar-label'>📅 Select Month</div>", unsafe_allow_html=True)
    selected_months = st.multiselect("Select Month", month_list)
    if not selected_months:
        selected_months = month_list

    # ------------------ PRODUCT SLICER ------------------
    st.markdown("<div class='sidebar-label'> 🎁 Select Product </div>", unsafe_allow_html=True)
    selected_product = st.multiselect("Select Product", product_list)
    if not selected_product:
        selected_product = product_list


    # ------------------ SERIES SLICER ------------------
    st.markdown("<div class='sidebar-label'>🧩 Select Product Series</div>", unsafe_allow_html=True)
    selected_series = st.multiselect("Select Series", series_list)
    if not selected_series:
        selected_series = series_list



# ----------------------------
# APPLY FILTERS
# ----------------------------
filtered = pr360[
    pr360["month_name"].isin(selected_months) &
    pr360["product"].isin(selected_product) &
    pr360['series'].isin(selected_series)
]


# ----------------------------
# KPI VALUES
# ----------------------------
Total_Revenue = pr360['revenue_won'].sum()
Total_Revenue_Display = "$" + millify(Total_Revenue, precision=2)

Total_Opportunities = filtered['total_opportunities'].sum()
Open_Opportunities = filtered['open_opportunities'].sum()
Won_Opportunities = filtered['won_opportunities'].sum()
Lost_Opportunities = filtered['lost_opportunities'].sum()

Win_Rate = (Won_Opportunities / Total_Opportunities * 100) if Total_Opportunities > 0 else 0

Customer_per_Product = filtered['distinct_accounts'].mean()
Avg_Sales_Cycle = filtered['avg_sales_cycle_days'].mean()
avg_deal_value = filtered['avg_win_deal_value'].mean()
Product_Count = filtered['product'].nunique()

# ----------------------------
# KPI CARD FUNCTION
# ----------------------------
def kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# KPI DISPLAY GRID
# ----------------------------
k1, k2, k3 = st.columns(3)
with k1: kpi_card("💰 Total Revenue", Total_Revenue_Display)
with k2: kpi_card("📁 Total Opportunities", millify(Total_Opportunities, 2))
with k3: kpi_card("📂 Open Opportunities", millify(Open_Opportunities, 2))

k4, k5, k6 = st.columns(3)
with k4: kpi_card("🏆 Win Rate", f"{Win_Rate:.2f}%")
with k5: kpi_card("❌ Lost Opportunities", millify(Lost_Opportunities, 2))
with k6: kpi_card("📦 Average Sales Cycle", millify(Avg_Sales_Cycle, 2))

k7, k8, k9 = st.columns(3)
with k7: kpi_card("👥 Customer Per Product", millify(Customer_per_Product, 2))
with k8: kpi_card("💵 Avg Deal Value", "$" + millify(avg_deal_value, 2))
with k9: kpi_card("📅 Total Product", (Product_Count))



# ------------------------------------------
# VISUALS
# ------------------------------------------



# ------------------------------------------
# Product Revenue
# ------------------------------------------

product_revenue = (filtered.groupby(['product'])['revenue_won'].sum().reset_index())
product_revenue ['rev_fmt'] = product_revenue['revenue_won'].apply(lambda x: millify(x,precision = 1))

fig = px.bar(product_revenue,
             x = 'product',
             y = 'revenue_won',
             title = 'Revenue by Product',
             text= 'rev_fmt',
             color_discrete_sequence=px.colors.qualitative.Set2)
st.header("💰 Revenue by Product")
st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# no of opportunities per product
# ------------------------------------------
 
opp_prod = (filtered.groupby('product')[['won_opportunities','lost_opportunities','open_opportunities']]
          .sum().reset_index().sort_values('won_opportunities',ascending = False).head(10).sort_values('won_opportunities',ascending = True)
         )

opp_long = opp_prod.melt(
        id_vars= 'product',
        value_vars= ['won_opportunities','lost_opportunities','open_opportunities'],
        var_name= 'opportunity_type',
        value_name= 'total_opportunities'
)

fig = px.bar(
    opp_long,
    x = 'total_opportunities',
    y = 'product',
    color = 'opportunity_type',
    title= 'No of Opportunities Per Product',
    barmode= 'group',
    text_auto= True,
    color_discrete_sequence= px.colors.qualitative.Set2
)
st.header("🕛 Number of Opportunities Per Product")
st.plotly_chart(fig,use_container_width= True)

# ------------------------------------------
# Avg deal value per product
# ------------------------------------------

avg_del = (filtered.groupby('product')['avg_win_deal_value'].mean().reset_index().sort_values('avg_win_deal_value',ascending= False))
fig = px.line(avg_del,
              x = 'product',
              y = 'avg_win_deal_value',
              markers = True,
              color_discrete_sequence=px.colors.qualitative.Set2)
st.subheader("🕛 Average Deal Value by Product")
st.plotly_chart(fig,use_container_width= True)


# ------------------------------------------
# Win Rate % by Product
# ------------------------------------------

win_rate_product = (filtered.groupby('product')
                    .agg(
                        total = ('total_opportunities','sum'),
                        won = ('won_opportunities','sum')
                    ).reset_index()
                    )
win_rate_product['win_rate'] = (win_rate_product['won']/win_rate_product['total']* 100).round(2)

fig = px.bar(win_rate_product,
             x = 'product',
             y = 'win_rate',
             title= 'win_rate',
             color = 'win_rate',
             color_continuous_scale= [
                 "#C8EAE2",
                 "#66C2A5",
                 "#2F8F83"
             ],text_auto= True) 

st.subheader("📈 Win Rate by Sector")
st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# Product Adoption (distinct Customers)
# ------------------------------------------

prod_ado = (filtered.groupby('product')['distinct_accounts'].sum().reset_index().sort_values('distinct_accounts',ascending= False))

fig = px.bar(prod_ado,
             x = 'product',
             y = 'distinct_accounts',
             title = 'Product Adoption',
             color_discrete_sequence=px.colors.qualitative.Set2,
             text_auto= True)
st.subheader("👨‍💼 Product Adoption (distinct Customers)")
st.plotly_chart(fig,use_container_width= True)


# ------------------------------------------
# avg sales cycle
# ------------------------------------------

avg_sal = (filtered.groupby('product')['avg_sales_cycle_days'].mean()
           .reset_index().sort_values('avg_sales_cycle_days',ascending= False))

fig = px.line(
    avg_sal,
    x = 'product',
    y = 'avg_sales_cycle_days',
    title = 'Avg Sales Cycle (Days) by Sector',
     markers=True,
    color_discrete_sequence=px.colors.qualitative.Set2,
    text='avg_sales_cycle_days')

st.subheader(' 🏆 Average Sales Cycle (Days)')
st.plotly_chart(fig,use_container_width= True)

st.subheader("📄 Raw Data")
st.dataframe(filtered)
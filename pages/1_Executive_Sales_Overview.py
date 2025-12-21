import streamlit as st
if st.session_state["authentication_status"] != True:
    st.error("Please login first.")
    st.stop()



# -----------------------------------------------------
# EXECUTIVE SALES OVERVIEW DASHBOARD (NEW UI DESIGN)
# -----------------------------------------------------


import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import plotly.express as px
from millify import millify
import seaborn as sns

# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(
    page_title="Executive Sales Overview",
    page_icon="🏆",
    layout="wide"
)

# ----------------------------
# SIDEBAR STYLE
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
            🏆 Executive Sales Overview
        </h1>
        <p style='font-size:20px; color:#5a6a81; font-weight:500;'>
            Company-wide revenue, opportunities & performance monitoring.
        </p>
        """,
        unsafe_allow_html=True
    )


# --------------------------
# LOAD DATA
# --------------------------
sales_pipeline = pd.read_csv('Resources/sales_pipeline.csv')
sales_pipeline['close_date'] = pd.to_datetime(sales_pipeline['close_date'], format='%d-%m-%Y', errors="coerce")
sales_pipeline['engage_date'] = pd.to_datetime(sales_pipeline['engage_date'], format='%d-%m-%Y', errors="coerce")
accounts = pd.read_csv('Resources/accounts.csv')

df = sales_pipeline.merge(accounts, on="account", how="inner")

df["month_num"] = df["close_date"].dt.month
df["month_name"] = df["close_date"].dt.month_name()


# --------------------------
# SIDEBAR FILTERS
# --------------------------
with st.sidebar:

    st.image("Resources/logo.jpeg", width=140)

    st.markdown("<div class='sidebar-title'>📊 FILTER PANEL</div>", unsafe_allow_html=True)

    month_list = (df[['month_num','month_name']]
                  .dropna().drop_duplicates()
                  .sort_values('month_num')['month_name']
                  .tolist())

    prod_list = sorted(df["product"].dropna().unique())
    region_list = sorted(df["office_location"].dropna().unique())

    # MONTH
    st.markdown("<div class='sidebar-label'>📅 Select Month</div>", unsafe_allow_html=True)
    selected_months = st.multiselect("Select Month", month_list)
    if not selected_months:
        selected_months = month_list
    # PRODUCT
    st.markdown("<div class='sidebar-label'>📦 Select Product</div>", unsafe_allow_html=True)
    selected_products = st.multiselect("Select Product", prod_list)
    if not selected_products:
        selected_products = prod_list

    # REGION
    st.markdown("<div class='sidebar-label'>🌍 Select Region</div>", unsafe_allow_html=True)
    selected_regions = st.multiselect("Select Region", region_list)
    if not selected_regions:
        selected_regions = region_list



# --------------------------
# FILTER DATA
# --------------------------
filtered = df[
    (df["month_name"].isin(selected_months)) &
    (df["product"].isin(selected_products)) &
    (df["office_location"].isin(selected_regions))
]

open_df = df[df['deal_stage'].isin(['Prospecting','Engaging'])]

open_filtered = open_df[
    (open_df["product"].isin(selected_products)) &
    (open_df["office_location"].isin(selected_regions))
]



# --------------------------
# KPI CALCULATIONS
# --------------------------
Total_Revenue = df['close_value'].sum()
Total_Revenue_Display = "$" + millify(Total_Revenue, precision=2)

total_opps = pd.concat([filtered, open_filtered])["opportunity_id"].nunique()
won_opps = filtered[filtered["deal_stage"]=="Won"]["opportunity_id"].nunique()
lost_opps = filtered[filtered["deal_stage"]=="Lost"]["opportunity_id"].nunique()
open_opps = len(open_filtered)
win_rate = (won_opps / total_opps * 100) if total_opps > 0 else 0
avg_deal_value = filtered.loc[filtered["deal_stage"]=="Won","close_value"].mean()
avg_sales_cycle = (filtered["close_date"] - filtered["engage_date"]).dt.days.mean()
active_customers = accounts["account"].nunique()



# --------------------------
# KPI CARD FUNCTION
# --------------------------
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



# --------------------------
# KPI GRID
# --------------------------
k1,k2,k3 = st.columns(3)
with k1: kpi_card("💰 Total Revenue", Total_Revenue_Display)
with k2: kpi_card("📁 Total Opps", f"{total_opps:,}")
with k3: kpi_card("🏆 Won Opps", f"{won_opps:,}")

k4,k5,k6 = st.columns(3)
with k4: kpi_card("📂 Open Opps", f"{open_opps:,}")
with k5: kpi_card("❌ Lost Opps", f"{lost_opps:,}")
with k6: kpi_card("📈 Win Rate %", f"{win_rate:.2f}%")

k7,k8,k9 = st.columns(3)
with k7: kpi_card("💵 Avg Deal Value", f"${avg_deal_value:,.0f}")
with k8: kpi_card("👥 Active Customers", f"{active_customers:,}")
with k9: kpi_card("⏱ Avg Sales Cycle", f"{avg_sales_cycle:.0f} days")



# --------------------------
# VISUALS
# --------------------------

# ------------------------------------------
# 📊 MONTHLY REVENUE TREND
# ------------------------------------------
st.markdown("## 📈 Monthly Revenue Trend")

monthly = (
    filtered.groupby(["month_num", "month_name"])["close_value"]
    .sum()
    .reset_index()
    .sort_values("month_num")
)

fig = px.line(
    monthly,
    x="month_name",
    y="close_value",
    markers=True,
    title="Monthly Revenue Trend",
    color_discrete_sequence=["#2F8F83"]
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue",
    template="simple_white",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# 🔻 OPPORTUNITY STAGE FUNNEL
# ------------------------------------------

st.markdown("## 🔻 Opportunity Stage Distribution Funnel")

stage = (
    df.groupby("deal_stage")["opportunity_id"]
    .count()
    .reset_index()
)

order = ["Prospecting", "Engaging", "Lost", "Won"]
stage["deal_stage"] = pd.Categorical(stage["deal_stage"], categories=order, ordered=True)
stage = stage.sort_values("deal_stage")

fig = px.funnel(
    stage,
    y="deal_stage",
    x="opportunity_id",
    color="deal_stage",
    title="Opportunity Funnel",
    color_discrete_sequence=[
        "#4B77BE", "#5DADE2", "#F5B041", "#27AE60"
    ]
)

fig.update_layout(
    template="simple_white",
    yaxis_title="Stage",
    xaxis_title="Opportunity Count",
    funnelgap=0
)

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# 📦 REVENUE BY PRODUCT
# ------------------------------------------

st.markdown("## 📦 Revenue Contribution by Product")

prod = (
    filtered.groupby("product")["close_value"]
    .sum()
    .reset_index()
    .sort_values('close_value')
)

fig = px.bar(
    prod,
    x="product",
    y="close_value",
    title="Revenue by Product",
    color="close_value",
    color_continuous_scale=["#C8EAE2", "#2F8F83"]
)

fig.update_layout(
    xaxis_title="Product",
    yaxis_title="Revenue"
)

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# 📂 REVENUE BY SECTOR
# ------------------------------------------

st.markdown("## 📂 Revenue Contribution by Sector")

sect = (
    filtered.groupby('sector')["close_value"]
    .sum()
    .reset_index()
    .sort_values('close_value', ascending=True)
)

fig = px.bar(
    sect,
    x="close_value",
    y="sector",
    orientation="h",
    title="Revenue by Sector",
    color="close_value",
    color_continuous_scale=["#C8EAE2", "#2F8F83"]
)

fig.update_layout(
    xaxis_title="Revenue",
    yaxis_title="Sector"
)

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# 🌍 REVENUE BY REGION
# ------------------------------------------

st.markdown("## 🌍 Revenue by Region")

region = (
    filtered.groupby("office_location")["close_value"]
    .sum()
    .reset_index()
)

fig = px.bar(
    region,
    x="office_location",
    y="close_value",
    title="Revenue by Region",
    color="close_value",
    color_continuous_scale=["#C8EAE2", "#2F8F83"]
)

fig.update_layout(
    xaxis_title="Region",
    yaxis_title="Revenue"
)

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------
# 🏢 TOP ACCOUNTS BY REVENUE
# ------------------------------------------

st.markdown("## 🏢 Top 10 Accounts by Revenue")

acc = (
    filtered.groupby("account")["close_value"]
    .sum()
    .reset_index()
    .sort_values("close_value", ascending=False)
    .head(10)
    .sort_values("close_value", ascending=True)
)

fig = px.bar(
    acc,
    x="close_value",
    y="account",
    orientation="h",
    title="Top Accounts by Revenue",
    color="close_value",
    color_continuous_scale=["#C8EAE2", "#2F8F83"]
)

fig.update_layout(
    xaxis_title="Revenue",
    yaxis_title="Account"
)

st.plotly_chart(fig, use_container_width=True)



st.subheader("📄 Raw Data")
st.dataframe(filtered)


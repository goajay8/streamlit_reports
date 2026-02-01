import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Sales | Production | Stock | Demand | Norms | Lead Time",
    layout="wide"
)

# ================== LOAD DATA ==================

@st.cache_data
def load_sales():
    df = pd.read_csv(
        "/Users/ajaygour/Library/CloudStorage/OneDrive-ALGO8AIPRIVATELIMITED/streamlit_reports.py/files/daily_sales(in).csv"
    )
    df["invoice_date"] = pd.to_datetime(df["invoice_date"]).dt.date
    return df


@st.cache_data
def load_production():
    df = pd.read_csv(
        "/Users/ajaygour/Library/CloudStorage/OneDrive-ALGO8AIPRIVATELIMITED/streamlit_reports.py/files/dly_prod_jan(in).csv"
    )
    df["Prod.Date"] = pd.to_datetime(df["Prod.Date"]).dt.date
    return df


@st.cache_data
def load_stock():
    df = pd.read_csv(
        "/Users/ajaygour/Library/CloudStorage/OneDrive-ALGO8AIPRIVATELIMITED/streamlit_reports.py/files/daily_stock(in).csv"
    )
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.date
    return df


@st.cache_data
def load_demand():
    return pd.read_csv(
        "/Users/ajaygour/Library/CloudStorage/OneDrive-ALGO8AIPRIVATELIMITED/streamlit_reports.py/files/datewise_comparison 1(Requirement).csv"
    )


@st.cache_data
def load_norms():
    return pd.read_csv(
        "/Users/ajaygour/Library/CloudStorage/OneDrive-ALGO8AIPRIVATELIMITED/streamlit_reports.py/files/datewise_comparison 1(Norm).csv"
    )


@st.cache_data
def load_lead_time():
    df = pd.read_csv(
        "/Users/ajaygour/Library/CloudStorage/OneDrive-ALGO8AIPRIVATELIMITED/streamlit_reports.py/files/lead_time(Design LeadTime).csv"
    )
    # 🔑 normalize column names
    df.columns = df.columns.str.strip()
    return df



sales_df = load_sales()
prod_df = load_production()
stock_df = load_stock()
demand_df = load_demand()
norms_df = load_norms()
lead_df = load_lead_time()

# ================== UI ==================

st.title("📊 Sales, Production, Stock, Demand, Norms & Lead Time")

# ---------- Global Filters ----------
selected_date = st.selectbox(
    "Select Date",
    sorted(sales_df["invoice_date"].unique())
)

selected_sku = st.selectbox(
    "Select Material Code",
    sorted(sales_df["SKUCode"].unique())
)

# ================== FILTER DATA ==================

sales_f = sales_df[
    (sales_df["invoice_date"] == selected_date) &
    (sales_df["SKUCode"] == selected_sku)
]

prod_f = prod_df[
    (prod_df["Prod.Date"] == selected_date) &
    (prod_df["Matl.Code"] == selected_sku)
]

stock_f = stock_df[
    (stock_df["date"] == selected_date) &
    (stock_df["SKUCode"] == selected_sku)
]

# ---------- Demand & Norms ----------
date_col = selected_date.strftime("%d%m%Y")

demand_row = demand_df[demand_df["SKUCode"] == selected_sku]
demand_qty = (
    int(demand_row[date_col].iloc[0])
    if not demand_row.empty and date_col in demand_df.columns
    else 0
)

norms_row = norms_df[norms_df["SKUCode"] == selected_sku]
norms_qty = (
    int(norms_row[date_col].iloc[0])
    if not norms_row.empty and date_col in norms_df.columns
    else 0
)

# ---------- Lead Time (SKU-wise only) ----------
lead_row = lead_df[lead_df["SKUCode"] == selected_sku]

if not lead_row.empty:
    lead_time_val = lead_row["Lead Time in days"].iloc[0]
else:
    lead_time_val = "NA"

# ================== MATERIAL INFO ==================

description = (
    sales_f["Description"].iloc[0]
    if not sales_f.empty
    else "NA"
)

st.markdown(
    f"""
    **📅 Date:** {selected_date}  
    **🧾 Material Code:** {selected_sku}  
    **📦 Description:** {description}
    """
)

st.divider()

# ================== KPI SECTION (6 COLUMNS) ==================

sales_qty = int(sales_f["volume"].sum())
prod_qty = int(prod_f["Prod.Qty."].sum())
stock_qty = int(stock_f["total_qty"].sum())

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.subheader("📦 Sales")
    st.metric("Sales Qty", sales_qty)

with c2:
    st.subheader("🏭 Production")
    st.metric("Production Qty", prod_qty)

with c3:
    st.subheader("📊 Stock")
    st.metric("Stock Qty", stock_qty)

with c4:
    st.subheader("📈 Demand")
    st.metric("Demand Qty", demand_qty)

with c5:
    st.subheader("📐 Norms")
    st.metric("Norm Qty", norms_qty)

with c6:
    st.subheader("⏳ Lead Time")
    st.metric("Days", lead_time_val)

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Sales | Production | Stock | Demand | Norms | Lead Time",
    layout="wide"
)

# =========================================================
# UTILITY FUNCTIONS (SAFE CONVERSIONS)
# =========================================================

def safe_int(val, default=0):
    """Safely convert anything to int"""
    try:
        if pd.isna(val):
            return default
        return int(float(val))
    except (ValueError, TypeError):
        return default


def get_pivot_value(df, sku, date_col):
    """Safely fetch value from pivot-style dataframe"""
    try:
        row = df[df["SKUCode"] == sku]
        if row.empty or date_col not in df.columns:
            return 0
        return safe_int(row[date_col].iloc[0])
    except Exception:
        return 0


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_sales():
    df = pd.read_csv("files/daily_sales(in).csv")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce").dt.date
    return df


@st.cache_data
def load_production():
    df = pd.read_csv("files/dly_prod_jan(in).csv")
    df["Prod.Date"] = pd.to_datetime(df["Prod.Date"], errors="coerce").dt.date
    return df


@st.cache_data
def load_stock():
    df = pd.read_csv("files/daily_stock(in).csv")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce").dt.date
    return df


@st.cache_data
def load_demand():
    return pd.read_csv("files/datewise_comparison 1(Requirement).csv")


@st.cache_data
def load_norms():
    return pd.read_csv("files/datewise_comparison 1(Norm).csv")


@st.cache_data
def load_lead_time():
    df = pd.read_csv("files/lead_time(Design LeadTime).csv")
    df.columns = df.columns.str.strip()  # remove hidden spaces
    return df


sales_df = load_sales()
prod_df = load_production()
stock_df = load_stock()
demand_df = load_demand()
norms_df = load_norms()
lead_df = load_lead_time()

# =========================================================
# UI
# =========================================================

st.title("📊 Sales, Production, Stock, Demand, Norms & Lead Time")

selected_date = st.selectbox(
    "Select Date",
    sorted(sales_df["invoice_date"].dropna().unique())
)

selected_sku = st.selectbox(
    "Select Material Code",
    sorted(sales_df["SKUCode"].dropna().unique())
)

# =========================================================
# FILTER DATA
# =========================================================

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

# =========================================================
# DEMAND & NORMS (SAFE)
# =========================================================

date_col = selected_date.strftime("%d%m%Y")

demand_qty = get_pivot_value(demand_df, selected_sku, date_col)
norms_qty = get_pivot_value(norms_df, selected_sku, date_col)

# =========================================================
# LEAD TIME (SKU-WISE, SAFE)
# =========================================================

lead_time_val = "NA"
lead_row = lead_df[lead_df["SKUCode"] == selected_sku]

if not lead_row.empty:
    lead_cols = [c for c in lead_df.columns if "lead" in c.lower()]
    if lead_cols:
        lead_time_val = lead_row[lead_cols[0]].iloc[0]

# =========================================================
# MATERIAL INFO
# =========================================================

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

# =========================================================
# KPI SECTION (6 COLUMNS)
# =========================================================

sales_qty = safe_int(sales_f["volume"].sum())
prod_qty = safe_int(prod_f["Prod.Qty."].sum())
stock_qty = safe_int(stock_f["total_qty"].sum())

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

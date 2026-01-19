import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt

# --- PAGE SETUP ---
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Executive Sales Dashboard")
st.markdown("Analyzing customer purchasing behavior using **RFM Segmentation**.")

# --- DATA LOADING ---
# We use a function to cache the data so the app runs faster
@st.cache_data
def load_data():
    # Load the specific file you have
  df = pd.read_csv("Superstore-Sales.csv", encoding='ISO-8859-1')
    
    # Fix Date Format
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y', errors='coerce')
    return df

try:
    df = load_data()
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Data")
    region = st.sidebar.multiselect(
        "Select Region",
        options=df['Region'].unique(),
        default=df['Region'].unique()
    )
    
    df_selection = df.query("Region == @region")

    # --- TOP KPI METRICS ---
    total_sales = df_selection['Sales'].sum()
    total_profit = df_selection['Profit'].sum()
    avg_order_value = df_selection['Sales'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_sales:,.0f}")
    col2.metric("Total Profit", f"${total_profit:,.0f}")
    col3.metric("Avg. Order Value", f"${avg_order_value:,.2f}")

    st.markdown("---")

    # --- CHARTS ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Sales Trends Over Time")
        # Group by month to make the chart readable
        monthly_sales = df_selection.set_index('Order Date').resample('M')['Sales'].sum().reset_index()
        fig_trend = px.line(monthly_sales, x='Order Date', y='Sales', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("Profit by Product Category")
        fig_cat = px.bar(df_selection, x='Product Category', y='Profit', color='Product Category')
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- ADVANCED: RFM ANALYSIS (Hidden Complexity) ---
    st.subheader("🏆 Top Customer Segments")
    
    # RFM Calculation inside the app
    snapshot_date = df_selection['Order Date'].max() + dt.timedelta(days=1)
    rfm = df_selection.groupby('Customer Name').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'count',
        'Sales': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Simple Segmentation for Display
    # Top 25% of Spenders = 'Gold'
    # Bottom 25% of Spenders = 'Bronze'
    quartiles = rfm['Monetary'].quantile([0.25, 0.75])
    
    def simple_segment(row):
        if row['Monetary'] >= quartiles[0.75]: return 'Gold (Top Spender)'
        elif row['Monetary'] <= quartiles[0.25]: return 'Bronze (Low Spender)'
        else: return 'Silver (Average)'
    
    rfm['Segment'] = rfm.apply(simple_segment, axis=1)
    
    # Show the Segment Chart
    fig_segment = px.scatter(rfm, x='Recency', y='Monetary', color='Segment', 
                             title="Recency vs Monetary Value (Who buys often & spends more?)",
                             hover_data=['Frequency'])
    st.plotly_chart(fig_segment, use_container_width=True)

except FileNotFoundError:

    st.error("The file 'Superstore-Sales.csv' was not found. Please upload it to your GitHub repository.")

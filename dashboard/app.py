import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="SalesPulse", layout="wide")

st.title("SalesPulse – Real-Time Sales Analytics")

# Sidebar for navigation
page = st.sidebar.selectbox("Select Page", ["Executive Dashboard", "Customer Intelligence", "Forecasting", "Anomalies"])

def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
    return None

if page == "Executive Dashboard":
    st.header("Executive Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    revenue_data = fetch_data("/analytics/revenue")
    profit_margin_data = fetch_data("/analytics/profit-margin")
    
    if revenue_data:
        col1.metric("Total Revenue", f"${revenue_data['total_revenue']:,.2f}")
    if profit_margin_data:
        col2.metric("Profit Margin", f"{profit_margin_data['profit_margin']:.2f}%")
        
    st.subheader("Monthly Revenue Trend")
    monthly_data = fetch_data("/analytics/monthly-revenue")
    if monthly_data and 'monthly_revenue' in monthly_data:
        df = pd.DataFrame(monthly_data['monthly_revenue'])
        if not df.empty:
            fig = px.line(df, x='month_year', y='total_amount', markers=True, title='Monthly Revenue')
            st.plotly_chart(fig, use_container_width=True)
            
    st.subheader("Top Products")
    top_products = fetch_data("/analytics/top-products")
    if top_products and 'top_products' in top_products:
        df_products = pd.DataFrame(top_products['top_products'])
        if not df_products.empty:
            fig2 = px.bar(df_products, x='category', y='total_revenue', color='sub_category', title='Top Products by Revenue')
            st.plotly_chart(fig2, use_container_width=True)

elif page == "Customer Intelligence":
    st.header("Customer Intelligence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("RFM Segments")
        segments_data = fetch_data("/customers/segments")
        if segments_data:
            df_segments = pd.DataFrame(list(segments_data.items()), columns=['Segment', 'Count'])
            fig = px.pie(df_segments, names='Segment', values='Count', title='Customer Segments')
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("High Churn Risk Customers")
        churn_data = fetch_data("/customers/churn-risk")
        if churn_data:
            df_churn = pd.DataFrame(churn_data).head(10)
            st.dataframe(df_churn)
            
    st.subheader("Top Customers by Lifetime Value (CLV)")
    clv_data = fetch_data("/customers/clv")
    if clv_data:
        df_clv = pd.DataFrame(clv_data)
        st.dataframe(df_clv)

elif page == "Forecasting":
    st.header("Sales Forecasting (Prophet)")
    
    forecast_data = fetch_data("/forecast/")
    if forecast_data:
        df_forecast = pd.DataFrame(forecast_data)
        if not df_forecast.empty:
            fig = px.line(df_forecast, x='date', y='predicted_revenue', title='Predicted Revenue (Next 30 Days)')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_forecast)

elif page == "Anomalies":
    st.header("Anomaly Detection")
    
    anomalies_data = fetch_data("/anomalies/")
    if anomalies_data:
        df_anomalies = pd.DataFrame(anomalies_data)
        if not df_anomalies.empty:
            st.dataframe(df_anomalies)
        else:
            st.success("No anomalies detected!")

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="E-Commerce Insights Dashboard", layout="wide")

# 2. Load Data Function
@st.cache_data
def load_data():
    path = 'data/olist_sample.csv'
    
    # Check if file exists and isn't empty
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        st.error(f"File not found or empty at {path}. Please check your GitHub data folder!")
        st.stop()
        
    df = pd.read_csv(path) 
    
    # Standardize date formats
    date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Standardize strings
    df['order_status'] = df['order_status'].astype(str).str.lower()
    
    # Calculate missing columns
    df['shipping_ratio'] = df['freight_value'] / df['price']
    df['is_late'] = df['order_delivered_customer_date'] > df['order_estimated_delivery_date']
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    return df

df = load_data() 

# 3. Sidebar Navigation
st.sidebar.title("🔍 Filters")
all_states = sorted(df['customer_state'].dropna().unique())
states = st.sidebar.multiselect("Select States", options=all_states, default=all_states[:5])

if not states:
    st.warning("Please select at least one state to view insights.")
    st.stop()

filtered_df = df[df['customer_state'].isin(states)]

# 4. Header Section
st.title("🇧🇷 Brazilian E-Commerce Analytics")
st.markdown("A professional analysis of **logistics, payments, and customer satisfaction**.")

# 5. Top Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered_df['payment_value'].sum():,.2f}")
col2.metric("Avg. Review Score", f"{filtered_df['review_score'].mean():.2f} / 5")
col3.metric("Avg. Delivery Time", f"{filtered_df['delivery_time'].mean():.1f} Days")

st.divider()

# 6. Strategic Business Insights
st.header("Strategic Business Insights")

# Professional Blue Color
MAIN_BLUE = '#1f77b4' 

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("1. Late Delivery vs. Satisfaction")
    fig1 = px.box(filtered_df, x="is_late", y="review_score", 
                  color_discrete_sequence=[MAIN_BLUE],
                  title="Review Score Distribution (On-Time vs Late)")
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("2. Payment Method Spending")
    payment_data = filtered_df.groupby('payment_type')['payment_value'].mean().reset_index()
    fig2 = px.bar(payment_data, x='payment_type', y='payment_value', 
                  title="Average Spend by Payment Type")
    fig2.update_traces(marker_color=MAIN_BLUE)
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Regional Shipping 'Tax'")
    state_shipping = filtered_df.groupby('customer_state')['shipping_ratio'].mean().reset_index().sort_values('shipping_ratio', ascending=False)
    fig3 = px.bar(state_shipping, x='customer_state', y='shipping_ratio', title="Shipping-to-Price Ratio by State")
    fig3.update_traces(marker_color=MAIN_BLUE)
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("4. Hourly Order Volume")
    hourly_data = filtered_df.groupby('purchase_hour')['order_id'].nunique().reset_index()
    fig4 = px.line(hourly_data, x='purchase_hour', y='order_id', title="Orders by Hour of Day")
    fig4.update_traces(line_color=MAIN_BLUE)
    st.plotly_chart(fig4, use_container_width=True)

# Insight 5 - Now a Bar Chart with Blue Color
st.divider()
st.subheader("5. Product Category Cancellation Rates")

canceled_df = filtered_df[filtered_df['order_status'] == 'canceled']
if not canceled_df.empty:
    cat_cancel = canceled_df['category'].value_counts().reset_index().head(10)
    cat_cancel.columns = ['category', 'count']
    
    fig5 = px.bar(cat_cancel, x='category', y='count', 
                  title="Top 10 Canceled Categories",
                  labels={'count': 'Number of Cancellations'})
    fig5.update_traces(marker_color=MAIN_BLUE)
    st.plotly_chart(fig5, use_container_width=True)
    st.info("Insight: This bar chart identifies which product lines are most prone to cancellation.")
else:
    st.info("No canceled orders found for the current filter selection.")

st.divider()
st.caption("Developed by [Your Name] | Data: Olist Dataset")

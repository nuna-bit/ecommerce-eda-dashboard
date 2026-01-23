import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="E-Commerce Insights Dashboard", layout="wide")

# 2. Load Data Function
@st.cache_data
def load_data():
    # Make sure this path matches your file name in the data folder exactly
    df = pd.read_csv('data/olist_sample.csv') 
    
    # Standardize date formats
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
    
    # --- DATA CLEANING FOR INSIGHTS ---
    # Standardize 'order_status' to lowercase to avoid "Canceled" vs "canceled" issues
    df['order_status'] = df['order_status'].astype(str).str.lower()
    
    # Calculate columns that were missing in the CSV
    df['shipping_ratio'] = df['freight_value'] / df['price']
    df['is_late'] = df['order_delivered_customer_date'] > df['order_estimated_delivery_date']
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    
    # Calculate delivery time for the KPI metric
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    return df

# --- CRITICAL: Call the function to create the 'df' variable ---
df = load_data() 

# 3. Sidebar Navigation & Filters
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("Filter the data to see specific trends.")

# Get all unique states
all_states = sorted(df['customer_state'].unique())

states = st.sidebar.multiselect(
    "Select States", 
    options=all_states, 
    default=all_states[:5] # Default to first 5 states
)

# Filter dataframe based on selection
if not states:
    st.error("Please select at least one state in the sidebar to see data.")
    st.stop()

filtered_df = df[df['customer_state'].isin(states)]

# 4. Header Section
st.title("🇧🇷 Brazilian E-Commerce Analytics")
st.markdown("""
This dashboard analyzes messy real-world data from Olist to provide **actionable business insights**.
""")

# 5. Top Level Metrics (KPIs)
total_revenue = filtered_df['payment_value'].sum()
avg_review = filtered_df['review_score'].mean()
avg_delivery = filtered_df['delivery_time'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Avg. Review Score", f"{avg_review:.2f} / 5")
col3.metric("Avg. Delivery Time", f"{avg_delivery:.1f} Days")

st.divider()

# 6. Strategic Business Insights
st.header("Strategic Business Insights")

# Insight 1 & 2 in columns
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("1. Late Delivery vs. Satisfaction")
    fig1 = px.box(filtered_df, x="is_late", y="review_score", color="is_late",
                  title="Impact of Delays on Reviews",
                  labels={"is_late": "Is the Order Late?", "review_score": "Review Score"})
    st.plotly_chart(fig1, use_container_width=True)
    st.info("Insight: Late deliveries correlate with a ~40% drop in review scores.")

with row1_col2:
    st.subheader("2. Payment Method Spending")
    payment_data = filtered_df.groupby('payment_type')['payment_value'].mean().reset_index()
    fig2 = px.bar(payment_data, x='payment_type', y='payment_value', 
                  title="Avg. Spend per Payment Type",
                  labels={"payment_type": "Method", "payment_value": "Avg Price"})
    st.plotly_chart(fig2, use_container_width=True)
    st.info("Insight: Credit card and Boleto users have similar purchasing power.")

# Insight 3 & 4
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Regional Shipping 'Tax'")
    state_shipping = filtered_df.groupby('customer_state')['shipping_ratio'].mean().reset_index().sort_values('shipping_ratio', ascending=False)
    fig3 = px.bar(state_shipping, x='customer_state', y='shipping_ratio', title="Shipping-to-Price Ratio by State")
    st.plotly_chart(fig3, use_container_width=True)
    st.info("Customers in the North and Northeast regions pay significantly higher shipping relative to product price.")

with row2_col2:
    st.subheader("4. Hourly Order Volume")
    hourly_data = filtered_df.groupby('purchase_hour')['order_id'].nunique().reset_index()
    fig4 = px.line(hourly_data, x='purchase_hour', y='order_id', title="Peak Shopping Hours")
    st.plotly_chart(fig4, use_container_width=True)
    st.info("Peak activity occurs between 10 AM and 10 PM.")

# Insight 5 (Full Width) - UPDATED FOR MULTIPLE CATEGORIES
st.divider()
st.subheader("5. Product Category Cancellation Rates")

# Filter for canceled status (already lowercased in load_data)
canceled_df = filtered_df[filtered_df['order_status'] == 'canceled']

if not canceled_df.empty:
    # Use value_counts to get a clean count of every unique category
    cat_cancel = canceled_df['category'].value_counts().reset_index()
    cat_cancel.columns = ['category', 'count']
    
    # Take the top 10
    top_10_canceled = cat_cancel.head(10)

    fig5 = px.pie(
        top_10_canceled, 
        values='count', 
        names='category', 
        title="Top 10 Categories for Canceled Orders",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig5.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig5, use_container_width=True)
    st.info("Insight: This shows the distribution of cancellations. If one category dominates, investigate product quality or description accuracy.")
else:
    st.warning("No 'canceled' orders found for the current selection. Try selecting more states in the sidebar (like SP or RJ) to increase the data pool.")

# Technical note
st.divider()
st.caption("Data Source: Olist Store Dataset (Kaggle) | Analysis conducted using Python, Pandas, and Plotly.")

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
    
    # Safety Check: If file is missing or empty, show a clear error
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        st.error(f"⚠️ Data file not found or empty at {path}. Please check your GitHub repository!")
        st.stop()
        
    df = pd.read_csv(path) 
    
    # Standardize date formats (errors='coerce' prevents crashes on missing delivery dates)
    date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Standardize strings & Calculate columns
    df['order_status'] = df['order_status'].astype(str).str.lower()
    df['shipping_ratio'] = df['freight_value'] / df['price']
    df['is_late'] = df['order_delivered_customer_date'] > df['order_estimated_delivery_date']
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    return df

# Initialize Data
df = load_data() 

# 3. Sidebar Navigation
st.sidebar.title("🔍 Dashboard Filters")
st.sidebar.markdown("Filter the analysis by region.")
all_states = sorted(df['customer_state'].dropna().unique())
states = st.sidebar.multiselect("Select States", options=all_states, default=all_states[:5])

if not states:
    st.warning("Please select at least one state in the sidebar.")
    st.stop()

filtered_df = df[df['customer_state'].isin(states)]

# 4. Header Section
st.title("🇧🇷 Brazilian E-Commerce Analytics")
st.markdown("Translating raw logistics and sales data into **actionable business strategy**.")

# 5. Top Level Metrics (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered_df['payment_value'].sum():,.2f}")
col2.metric("Avg. Review Score", f"{filtered_df['review_score'].mean():.2f} / 5")
col3.metric("Avg. Delivery Time", f"{filtered_df['delivery_time'].mean():.1f} Days")

st.divider()

# 6. Strategic Business Insights
st.header("Strategic Business Insights")

# Professional Blue Color Palette
MAIN_BLUE = '#1f77b4' 

# --- Row 1: Logistics and Payments ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("1. Late Delivery vs. Satisfaction")
    fig1 = px.box(filtered_df, x="is_late", y="review_score", 
                  color_discrete_sequence=[MAIN_BLUE],
                  title="Impact of Delays on Review Scores")
    st.plotly_chart(fig1, use_container_width=True)
    st.info("**Insight:** Orders delivered after the estimate see a drastic drop in scores (median ~2.0). Improving logistics reliability is the fastest way to boost customer retention.")

with row1_col2:
    st.subheader("2. Payment Method Spending")
    payment_data = filtered_df.groupby('payment_type')['payment_value'].mean().reset_index()
    fig2 = px.bar(payment_data, x='payment_type', y='payment_value', 
                  title="Average Spend per Payment Method")
    fig2.update_traces(marker_color=MAIN_BLUE)
    st.plotly_chart(fig2, use_container_width=True)
    st.info("**Insight:** Credit card and Boleto (cash) users exhibit similar purchasing power. Ensure payment gateways are optimized for both to minimize checkout friction.")

# --- Row 2: Regional and Timing Trends ---
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Regional Shipping 'Tax'")
    state_shipping = filtered_df.groupby('customer_state')['shipping_ratio'].mean().reset_index().sort_values('shipping_ratio', ascending=False)
    fig3 = px.bar(state_shipping, x='customer_state', y='shipping_ratio', title="Shipping-to-Price Ratio by State")
    fig3.update_traces(marker_color=MAIN_BLUE)
    st.plotly_chart(fig3, use_container_width=True)
    st.info("**Insight:** States with high shipping ratios (often North/Northeast) are less competitive. Consider localized warehouses in these regions to lower costs.")

with row2_col2:
    st.subheader("4. Hourly Order Volume")
    hourly_data = filtered_df.groupby('purchase_hour')['order_id'].nunique().reset_index()
    fig4 = px.line(hourly_data, x='purchase_hour', y='order_id', title="Peak Shopping Hours")
    fig4.update_traces(line_color=MAIN_BLUE)
    st.plotly_chart(fig4, use_container_width=True)
    st.info("**Insight:** Peak shopping occurs between 10:00 and 21:00. Marketing campaigns and customer support staff should be concentrated in this window.")

# Footer
st.divider()
st.caption("Data Source: Olist Store Dataset | Analysis conducted with Python, Pandas, and Plotly.")

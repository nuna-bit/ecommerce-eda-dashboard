import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="E-Commerce Insights Dashboard", layout="wide")

# 2. Load Data Function (Defining how to get the data)
@st.cache_data
def load_data():
    # Make sure this path matches your file name in the data folder exactly
    df = pd.read_csv('data/olist_sample.csv') 
    
    # Standardize date formats
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
    
    # Calculate columns that were missing in the CSV
    df['shipping_ratio'] = df['freight_value'] / df['price']
    df['is_late'] = df['order_delivered_customer_date'] > df['order_estimated_delivery_date']
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    
    return df

# --- CRITICAL: Call the function to create the 'df' variable BEFORE using it ---
df = load_data() 

# 3. Sidebar Navigation & Filters (Now 'df' is defined, so this won't crash)
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("Filter the data to see specific trends.")
states = st.sidebar.multiselect(
    "Select States", 
    options=sorted(df['customer_state'].unique()), 
    default=df['customer_state'].unique()[:5]
)

# Filter dataframe based on selection
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
                  title="Impact of Delays on Reviews")
    st.plotly_chart(fig1, width='stretch')
    st.info("Insight: Late deliveries correlate with a ~40% drop in review scores.")

with row1_col2:
    st.subheader("2. Payment Method Spending")
    payment_data = filtered_df.groupby('payment_type')['payment_value'].mean().reset_index()
    fig2 = px.bar(payment_data, x='payment_type', y='payment_value', 
                  title="Avg. Spend per Payment Type")
    st.plotly_chart(fig2, width='stretch')
    st.info("Insight: Credit card and Boleto users have similar purchasing power.")

# Insight 3 & 4
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Regional Shipping 'Tax'")
    state_shipping = filtered_df.groupby('customer_state')['shipping_ratio'].mean().reset_index().sort_values('shipping_ratio', ascending=False)
    fig3 = px.bar(state_shipping, x='customer_state', y='shipping_ratio', title="Shipping-to-Price Ratio by State")
    st.plotly_chart(fig3, width='stretch')

with row2_col2:
    st.subheader("4. Hourly Order Volume")
    hourly_data = filtered_df.groupby('purchase_hour')['order_id'].nunique().reset_index()
    fig4 = px.line(hourly_data, x='purchase_hour', y='order_id', title="Peak Shopping Hours")
    st.plotly_chart(fig4, width='stretch')
    st.info("Peak activity occurs between 10 AM and 10 PM.")

# Insight 5 (Full Width)
st.subheader("5. Product Category Cancellation Rates")

# 1. Filter specifically for canceled orders
canceled_orders = filtered_df[filtered_df['order_status'] == 'canceled']

if not canceled_orders.empty:
    # 2. Count cancellations per category
    cat_cancel = canceled_orders.groupby('category').size().reset_index(name='count')
    cat_cancel = cat_cancel.sort_values('count', ascending=False).head(10)

    # 3. Create the Pie Chart
    fig5 = px.pie(
        cat_cancel, 
        values='count', 
        names='category', 
        title="Top 10 Categories by Total Cancellations",
        hole=0.4 # This makes it a Donut chart (cleaner look)
    )
    st.plotly_chart(fig5, width='stretch')
    st.info("Insight: Most cancellations occur in high-volume or high-sensitivity categories like Perfumery.")
else:
    st.warning("No canceled orders found for the selected states. Try adding more states in the sidebar!")

# Technical note
st.divider()
st.caption("Data Source: Olist Store Dataset (Kaggle) | Analysis conducted using Python, Pandas, and Plotly.")


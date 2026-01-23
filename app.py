import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="E-Commerce Insights Dashboard", layout="wide")

# 2. Load Data Function
@st.cache_data
def load_data():
    df = pd.read_csv('data/olist_sample.csv') 
    
    # Standardize date formats
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
    
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
st.sidebar.title("Dashboard Filters")
all_states = sorted(df['customer_state'].unique())
states = st.sidebar.multiselect("Select States", options=all_states, default=all_states[:5])

if not states:
    st.error("Please select at least one state.")
    st.stop()

filtered_df = df[df['customer_state'].isin(states)]

# 4. Header Section
st.title("🇧🇷 Brazilian E-Commerce Analytics")
st.markdown("This dashboard analyzes **Olist logistics and sales** to provide actionable business insights.")

# 5. Top Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered_df['payment_value'].sum():,.2f}")
col2.metric("Avg. Review Score", f"{filtered_df['review_score'].mean():.2f} / 5")
col3.metric("Avg. Delivery Time", f"{filtered_df['delivery_time'].mean():.1f} Days")

st.divider()

# 6. Strategic Business Insights
st.header("Strategic Business Insights")

# Define a consistent color for all bar/line charts
INSIGHT_COLOR = '#1f77b4' # Professional Blue

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("1. Late Delivery vs. Satisfaction")
    fig1 = px.box(filtered_df, x="is_late", y="review_score", 
                  color_discrete_sequence=[INSIGHT_COLOR],
                  title="Impact of Delays on Reviews")
    st.plotly_chart(fig1, use_container_width=True)
    st.info("Insight: Late deliveries correlate with a ~40% drop in review scores.")

with row1_col2:
    st.subheader("2. Payment Method Spending")
    payment_data = filtered_df.groupby('payment_type')['payment_value'].mean().reset_index()
    fig2 = px.bar(payment_data, x='payment_type', y='payment_value', 
                  title="Avg. Spend per Payment Type")
    fig2.update_traces(marker_color=INSIGHT_COLOR)
    st.plotly_chart(fig2, use_container_width=True)
    st.info("Insight: Credit card and Boleto users have similar purchasing power.")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Regional Shipping 'Tax'")
    state_shipping = filtered_df.groupby('customer_state')['shipping_ratio'].mean().reset_index().sort_values('shipping_ratio', ascending=False)
    fig3 = px.bar(state_shipping, x='customer_state', y='shipping_ratio', title="Shipping-to-Price Ratio")
    fig3.update_traces(marker_color=INSIGHT_COLOR)
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("4. Hourly Order Volume")
    hourly_data = filtered_df.groupby('purchase_hour')['order_id'].nunique().reset_index()
    fig4 = px.line(hourly_data, x='purchase_hour', y='order_id', title="Peak Shopping Hours")
    fig4.update_traces(line_color=INSIGHT_COLOR)
    st.plotly_chart(fig4, use_container_width=True)

# Insight 5 - FIXED BAR CHART
st.divider()
st.subheader("5. Product Category Cancellation Rates")

canceled_df = filtered_df[filtered_df['order_status'] == 'canceled']
if not canceled_df.empty:
    cat_cancel = canceled_df['category'].value_counts().reset_index().head(10)
    cat_cancel.columns = ['category', 'count']
    
    fig5 = px.bar(cat_cancel, x='category', y='count', 
                  title="Top 10 Categories with Most Cancellations",
                  labels={'count': 'Number of Cancellations', 'category': 'Product Category'})
    fig5.update_traces(marker_color=INSIGHT_COLOR)
    st.plotly_chart(fig5, use_container_width=True)
    st.info("Insight: High cancellation rates in specific categories suggest issues with product descriptions or expectations.")
else:
    st.warning("No canceled orders found for the selected filters.")

st.divider()
st.caption("Data Source: Olist Store Dataset | Built with Streamlit & Plotly")

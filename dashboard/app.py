import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="RetailPulse Analytics", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    base_path = Path(__file__).resolve().parent.parent
    csv_path = base_path / "data" / "cleaned" / "cleaned_sales_master.csv"
    return pd.read_csv(csv_path)

df = load_data()

st.title("RetailPulse: E-Commerce Business Intelligence Dashboard")
st.markdown("Analyzing 100k+ orders from the Olist Brazilian E-Commerce dataset to uncover revenue trends, logistics bottlenecks, and customer satisfaction impact.")

total_revenue = df['payment_value'].sum()
total_orders = df['order_id'].nunique()
avg_review = df['review_score'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Delivered Orders", f"{total_orders:,}")
col3.metric("Average Review Score", f"{avg_review:.2f} / 5.0")

st.markdown("---")

st.subheader("The Cost of Late Deliveries")
delay_df = df.groupby('delivery_status').agg(
    order_count=('order_id', 'nunique'),
    avg_score=('review_score', 'mean')
).reset_index()

fig_delay = px.bar(
    delay_df, 
    x='delivery_status', 
    y='avg_score', 
    color='delivery_status',
    text='avg_score',
    title="Average Review Score: On-Time vs. Late Deliveries"
)
fig_delay.update_traces(texttemplate='%{text:.2f}', textposition='outside')
st.plotly_chart(fig_delay, use_container_width=True)

st.subheader("Top Product Categories by Revenue")
category_rev = df.groupby('product_category')['payment_value'].sum().reset_index().sort_values(by='payment_value', ascending=False).head(10)

fig_cat = px.bar(
    category_rev, 
    x='payment_value', 
    y='product_category', 
    orientation='h',
    title="Top 10 Product Categories by Total Revenue"
)
fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_cat, use_container_width=True)
from pathlib import Path
import pandas as pd
import streamlit as st
from src.config import ROOT, CLEAN, FORECAST, REORDERS, SIMULATION

st.set_page_config(page_title="Retail Forecasting & Inventory", layout="wide")
st.title("Retail Sales Forecasting & Inventory Optimization")
st.caption("Educational prototype | Synthetic retail sales and inventory | Not real retailer results")
if not FORECAST.exists() or not REORDERS.exists():
    st.error("Run `python main.py all` from the project root first.")
    st.stop()

sales = pd.read_csv(CLEAN, parse_dates=["date"])
future = pd.read_csv(FORECAST, parse_dates=["date"])
orders = pd.read_csv(REORDERS)
stores = sorted(sales.store_id.unique())
store = st.sidebar.selectbox("Store", stores)
products = sorted(sales.product_id.unique())
product = st.sidebar.selectbox("Product", products)
selected = sales[(sales.store_id == store) & (sales.product_id == product)].sort_values("date")
f = future[(future.store_id == store) & (future.product_id == product)].sort_values("date")
r = orders[(orders.store_id == store) & (orders.product_id == product)].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Historical units", f"{selected.units_sold.sum():,}")
col2.metric("Avg daily forecast", f"{r.daily_forecast:.1f}")
col3.metric("Reorder point", int(r.reorder_point))
col4.metric("Suggested order", int(r.suggested_order))

st.subheader("Historical sales")
st.line_chart(selected.set_index("date")["units_sold"])
st.subheader("Future demand (14 days)")
st.line_chart(f.set_index("date")["predicted_demand"])
st.subheader("Replenishment recommendations")
st.dataframe(orders, use_container_width=True)
st.download_button("Download recommendations CSV", orders.to_csv(index=False), "reorder_recommendations.csv", "text/csv")

scores_path = ROOT / "reports" / "model_scores.csv"
if scores_path.exists():
    st.subheader("Model evaluation (one-step holdout)")
    st.dataframe(pd.read_csv(scores_path), use_container_width=True)
comparison_path = ROOT / "outputs" / "simulation" / "policy_comparison.csv"
if comparison_path.exists():
    st.subheader("Illustrative inventory policy comparison")
    st.caption("Synthetic demand. Policy model selection reused the holdout; not an unbiased estimate of policy improvement.")
    comparison = pd.read_csv(comparison_path)
    st.dataframe(comparison, use_container_width=True)
    st.bar_chart(comparison.set_index("policy")["fill_rate_percent"])
if SIMULATION.exists():
    st.subheader("Inventory simulation: daily stock")
    sim = pd.read_csv(SIMULATION)
    st.line_chart(sim.pivot(index="day", columns="policy", values="closing_stock"))

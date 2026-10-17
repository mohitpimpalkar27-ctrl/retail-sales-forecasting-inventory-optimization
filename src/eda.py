import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from src.config import ROOT

def create_charts(clean, eval_predictions, future, comparison):
    path = ROOT / "images" / "charts"
    path.mkdir(parents=True, exist_ok=True)
    daily = clean.groupby("date")["units_sold"].sum()
    ax = daily.plot(figsize=(10, 4), title="Daily sales (synthetic data)")
    ax.set_ylabel("Units")
    plt.tight_layout(); plt.savefig(path / "daily_sales.png"); plt.close()
    sample = eval_predictions.query("store_id == 'S01' and product_id == 'P001'").sort_values("date")
    ax = sample.plot(x="date", y=["actual", "predicted"], figsize=(10, 4), title="Holdout: actual vs one-step predictions")
    ax.set_ylabel("Units")
    plt.tight_layout(); plt.savefig(path / "holdout_forecast.png"); plt.close()
    sample_future = future.query("store_id == 'S01' and product_id == 'P001'").sort_values("date")
    ax = sample_future.plot(x="date", y="predicted_demand", figsize=(10, 4), title="Future 14-day demand forecast")
    ax.set_ylabel("Units")
    plt.tight_layout(); plt.savefig(path / "future_forecast.png"); plt.close()
    ax = comparison.plot(x="policy", y="fill_rate_percent", kind="bar", legend=False, figsize=(7, 4), title="Illustrative simulation: fill rate")
    ax.set_ylabel("Fill rate (%)"); ax.set_ylim(0, 105)
    plt.tight_layout(); plt.savefig(path / "simulation_comparison.png"); plt.close()

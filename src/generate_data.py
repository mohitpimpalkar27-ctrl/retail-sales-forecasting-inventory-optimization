"""Reproducible SYNTHETIC data; no real retailer data is claimed."""
import numpy as np
import pandas as pd
from src.config import RAW, DATA, SEED, ensure_directories

PRODUCTS = [("P001", "Rice", "Grocery", 70), ("P002", "Oil", "Grocery", 160),
            ("P003", "Biscuits", "Snacks", 30), ("P004", "Milk", "Dairy", 55),
            ("P005", "Soap", "Personal Care", 45), ("P006", "Juice", "Beverages", 80)]
STORES = ["S01", "S02", "S03"]

def generate(days=300):
    ensure_directories()
    rng = np.random.default_rng(SEED)
    dates = pd.date_range("2025-01-01", periods=days, freq="D")
    records, inventory, suppliers = [], [], []
    for si, store in enumerate(STORES):
        for pi, (pid, name, category, price) in enumerate(PRODUCTS):
            base = 15 + 5 * si + 3 * pi
            for t, date in enumerate(dates):
                weekend = 1.23 if date.dayofweek >= 5 else 1.0
                yearly = 1 + 0.13 * np.sin(2 * np.pi * t / 365 + pi)
                trend = 1 + 0.0006 * t
                noise = rng.normal(0, 3.0)
                demand = max(0, round(base * weekend * yearly * trend + noise))
                records.append((date.date().isoformat(), store, pid, name, category, int(demand), price))
            inventory.append((store, pid, int(base * 5), 0, 0))
    for pi, (pid, _, _, _) in enumerate(PRODUCTS):
        suppliers.append((pid, f"SUP{pi+1:02d}", 3 + pi % 4, 20 + pi * 2))
    sales = pd.DataFrame(records, columns=["date", "store_id", "product_id", "product_name", "category", "units_sold", "unit_price"])
    sales.to_csv(RAW, index=False)
    pd.DataFrame(inventory, columns=["store_id", "product_id", "on_hand", "on_order", "backorders"]).to_csv(DATA / "simulated" / "inventory.csv", index=False)
    pd.DataFrame(suppliers, columns=["product_id", "supplier_id", "lead_time_days", "unit_cost"]).to_csv(DATA / "simulated" / "suppliers.csv", index=False)
    sales.head(20).to_csv(DATA / "sample" / "sample_sales.csv", index=False)
    print(f"Generated {len(sales):,} synthetic sales rows for {len(STORES)} stores and {len(PRODUCTS)} products.")
    return sales

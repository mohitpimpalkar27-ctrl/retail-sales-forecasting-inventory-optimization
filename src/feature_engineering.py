import numpy as np
import pandas as pd
FEATURES = ["store_code", "product_code", "day_of_week", "month", "day_index", "lag_1", "lag_7", "rolling_7"]

def add_features(df):
    out = df.sort_values(["store_id", "product_id", "date"]).copy()
    out["store_code"] = out["store_id"].str.extract(r"(\d+)$").astype(int)
    out["product_code"] = out["product_id"].str.extract(r"(\d+)$").astype(int)
    out["day_of_week"] = out["date"].dt.dayofweek
    out["month"] = out["date"].dt.month
    out["day_index"] = (out["date"] - pd.Timestamp("2025-01-01")).dt.days
    grouped = out.groupby(["store_id", "product_id"])["units_sold"]
    out["lag_1"] = grouped.shift(1)
    out["lag_7"] = grouped.shift(7)
    out["rolling_7"] = grouped.transform(lambda s: s.shift(1).rolling(7).mean())
    return out.dropna(subset=FEATURES).reset_index(drop=True)

def next_features(store, product, date, history):
    if len(history) < 7:
        raise ValueError("At least 7 days of demand history are required")
    return {"store_code": int(store[1:]), "product_code": int(product[1:]),
            "day_of_week": date.dayofweek, "month": date.month,
            "day_index": (date - pd.Timestamp("2025-01-01")).days,
            "lag_1": float(history[-1]), "lag_7": float(history[-7]),
            "rolling_7": float(np.mean(history[-7:]))}

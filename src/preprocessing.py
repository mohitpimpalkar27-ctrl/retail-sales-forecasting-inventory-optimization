import pandas as pd
from src.config import CLEAN, ensure_directories

REQUIRED = ["date", "store_id", "product_id", "product_name", "category", "units_sold", "unit_price"]

def clean_sales(df):
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    for column in ["units_sold", "unit_price"]:
        out[column] = pd.to_numeric(out[column], errors="raise")
    if out[["date", "store_id", "product_id"]].isna().any().any():
        raise ValueError("Missing date/store/product identifiers")
    if (out["units_sold"] < 0).any() or (out["unit_price"] < 0).any():
        raise ValueError("Negative units or prices found")
    if out.duplicated(["date", "store_id", "product_id"]).any():
        raise ValueError("Duplicate daily store-product records")
    out = out.sort_values(["store_id", "product_id", "date"]).reset_index(drop=True)
    # This starter expects a complete daily panel; absent dates are not silently treated as zero.
    for _, group in out.groupby(["store_id", "product_id"]):
        if not group["date"].diff().dropna().eq(pd.Timedelta(days=1)).all():
            raise ValueError("Missing daily observations: investigate before forecasting")
    out["revenue"] = out["units_sold"] * out["unit_price"]
    return out

def save_clean(df):
    ensure_directories()
    df.to_csv(CLEAN, index=False)

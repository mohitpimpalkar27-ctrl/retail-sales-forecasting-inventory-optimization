import pandas as pd
from src.feature_engineering import add_features

def test_lag_only_uses_past():
    df = pd.DataFrame({"date":pd.date_range("2025-01-01", periods=10), "store_id":"S01", "product_id":"P001", "units_sold":range(10)})
    f = add_features(df)
    assert f.iloc[0].lag_1 == 6
    assert f.iloc[0].lag_7 == 0

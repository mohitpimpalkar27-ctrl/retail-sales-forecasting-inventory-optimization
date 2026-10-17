import pandas as pd
from src.forecasting import forecast_recursive

def test_recursive_naive():
    history = pd.DataFrame({"date":pd.date_range("2025-01-01", periods=10), "store_id":"S01", "product_id":"P001", "units_sold":range(10)})
    result = forecast_recursive(history, 3, "seasonal_naive")
    assert len(result) == 3
    assert result.predicted_demand.tolist() == [3, 4, 5]

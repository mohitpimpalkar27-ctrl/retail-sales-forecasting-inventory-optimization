import pandas as pd
import pytest
from src.preprocessing import clean_sales

def test_negative_sales_rejected():
    data = pd.DataFrame([{"date":"2025-01-01", "store_id":"S01", "product_id":"P001", "product_name":"Rice", "category":"Grocery", "units_sold":-1, "unit_price":50}])
    with pytest.raises(ValueError):
        clean_sales(data)

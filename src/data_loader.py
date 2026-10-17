import pandas as pd
from src.config import RAW

def load_sales(path=RAW):
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run: python main.py generate")
    return pd.read_csv(path)

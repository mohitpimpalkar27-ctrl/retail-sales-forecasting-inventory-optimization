from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw" / "sales.csv"
CLEAN = DATA / "processed" / "clean_sales.csv"
FORECAST = ROOT / "outputs" / "forecasts" / "future_forecast.csv"
REORDERS = ROOT / "outputs" / "inventory" / "reorder_recommendations.csv"
SIMULATION = ROOT / "outputs" / "simulation" / "simulation_daily.csv"
MODEL = ROOT / "models" / "forecast_model.joblib"
HORIZON = 14
TEST_DAYS = 28
SEED = 42

def ensure_directories():
    for name in ["data/raw", "data/processed", "data/simulated", "data/sample", "models", "outputs/forecasts", "outputs/inventory", "outputs/simulation", "images/charts", "images/dashboard", "reports"]:
        (ROOT / name).mkdir(parents=True, exist_ok=True)

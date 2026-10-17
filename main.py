"""Run from repository root: python main.py all"""
import argparse
import joblib
import pandas as pd
from src.config import (ROOT, DATA, CLEAN, RAW, FORECAST, REORDERS, SIMULATION,
                        MODEL, TEST_DAYS, HORIZON, ensure_directories)
from src.generate_data import generate
from src.data_loader import load_sales
from src.preprocessing import clean_sales, save_clean
from src.feature_engineering import add_features, FEATURES
from src.forecasting import train_and_evaluate, forecast_recursive
from src.recommendations import recommend
from src.simulation import simulate_policy, summarize_simulation
from src.eda import create_charts
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression


def preprocess():
    clean = clean_sales(load_sales())
    save_clean(clean)
    print(f"CLEAN: {len(clean):,} rows -> {CLEAN.relative_to(ROOT)}")
    return clean

def train(clean):
    features = add_features(clean)
    cutoff = clean.date.max() - pd.Timedelta(days=TEST_DAYS - 1)
    best_name, scores, evaluation = train_and_evaluate(features, cutoff)
    scores.to_csv(ROOT / "reports" / "model_scores.csv", index=False)
    evaluation.to_csv(ROOT / "outputs" / "forecasts" / "holdout_one_step.csv", index=False)
    print("MODEL SCORES (one-step holdout, actual past available):")
    print(scores.to_string(index=False))
    print(f"SELECTED: {best_name}")
    return best_name, scores, evaluation, cutoff

def get_model(name, history):
    if name == "seasonal_naive":
        return None
    # Model for a historical backtest origin, trained strictly BEFORE test dates.
    features = add_features(history)
    model = LinearRegression() if name == "linear_regression" else RandomForestRegressor(n_estimators=60, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model.fit(features[FEATURES], features.units_sold)
    return model

def predict(clean, best_name):
    model = None if best_name == "seasonal_naive" else joblib.load(MODEL)["model"]
    future = forecast_recursive(clean, HORIZON, best_name, model)
    future.to_csv(FORECAST, index=False)
    print(f"FORECAST: {len(future)} rows -> {FORECAST.relative_to(ROOT)}")
    return future

def inventory(clean, future):
    stock = pd.read_csv(DATA / "simulated" / "inventory.csv")
    suppliers = pd.read_csv(DATA / "simulated" / "suppliers.csv")
    result = recommend(future, clean, stock, suppliers)
    result.to_csv(REORDERS, index=False)
    print(f"REORDER: {len(result)} rows -> {REORDERS.relative_to(ROOT)}")
    return result

def simulation(clean, best_name, cutoff):
    """Test two policies using identical holdout actuals and origin-time forecasts."""
    history = clean[clean.date < cutoff]
    test = clean[clean.date >= cutoff]
    # Avoid selecting model using this same holdout for a formal policy comparison.
    # Here the model was selected using the holdout; results are illustrative only.
    model = get_model(best_name, history)
    origin_forecast = forecast_recursive(history, TEST_DAYS, best_name, model)
    actual = test.query("store_id == 'S01' and product_id == 'P001'").sort_values("date").units_sold.tolist()
    pred = origin_forecast.query("store_id == 'S01' and product_id == 'P001'").sort_values("date").predicted_demand.tolist()
    supplier = pd.read_csv(DATA / "simulated" / "suppliers.csv")
    lead = int(supplier.loc[supplier.product_id == 'P001', 'lead_time_days'].iloc[0])
    daily = []
    for policy in ["fixed", "forecast"]:
        result = simulate_policy(actual, pred, starting_stock=90, lead_days=lead, policy=policy)
        daily.append(result)
    combined = pd.concat(daily, ignore_index=True)
    combined.to_csv(SIMULATION, index=False)
    comparison = pd.DataFrame([summarize_simulation(df) for df in daily])
    comparison.to_csv(ROOT / "outputs" / "simulation" / "policy_comparison.csv", index=False)
    print("SIMULATION (illustrative, model selected using same holdout):")
    print(comparison.to_string(index=False))
    return comparison

def run_all():
    ensure_directories()
    if not RAW.exists():
        generate()
    clean = preprocess()
    best, scores, evaluation, cutoff = train(clean)
    future = predict(clean, best)
    inventory(clean, future)
    comparison = simulation(clean, best, cutoff)
    create_charts(clean, evaluation, future, comparison)
    print("SUCCESS: Open dashboard with: python -m streamlit run app/dashboard.py")

def main():
    parser = argparse.ArgumentParser(description="Retail demand forecasting and inventory simulation")
    parser.add_argument("stage", choices=["generate", "preprocess", "train", "forecast", "inventory", "simulate", "all"])
    args = parser.parse_args()
    ensure_directories()
    if args.stage == "generate":
        generate(); return
    if args.stage == "all":
        run_all(); return
    if args.stage == "preprocess":
        preprocess(); return
    if not CLEAN.exists():
        raise SystemExit("First run: python main.py preprocess")
    clean = pd.read_csv(CLEAN, parse_dates=["date"])
    if args.stage == "train":
        train(clean); return
    # Reload saved selected model name from evaluation table.
    scores_path = ROOT / "reports" / "model_scores.csv"
    if not scores_path.exists():
        raise SystemExit("First run: python main.py train")
    best = str(pd.read_csv(scores_path).iloc[0].model)
    if args.stage == "forecast":
        predict(clean, best)
    elif args.stage == "inventory":
        if not FORECAST.exists():
            raise SystemExit("First run: python main.py forecast")
        inventory(clean, pd.read_csv(FORECAST, parse_dates=["date"]))
    elif args.stage == "simulate":
        cutoff = clean.date.max() - pd.Timedelta(days=TEST_DAYS - 1)
        simulation(clean, best, cutoff)

if __name__ == "__main__":
    main()

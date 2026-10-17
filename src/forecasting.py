"""One-step evaluation and honest recursive multi-day forecasting."""
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.feature_engineering import FEATURES, next_features
from src.config import MODEL

def metrics(actual, predicted):
    a, p = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    return {"MAE": float(mean_absolute_error(a, p)),
            "RMSE": float(np.sqrt(mean_squared_error(a, p))),
            "WAPE_percent": float(100 * np.sum(np.abs(a-p)) / max(np.sum(np.abs(a)), 1))}

def train_and_evaluate(feature_df, cutoff):
    train = feature_df[feature_df["date"] < cutoff]
    test = feature_df[feature_df["date"] >= cutoff]
    if train.empty or test.empty:
        raise ValueError("Insufficient train/test data")
    candidates = {"linear_regression": LinearRegression(),
                  "random_forest": RandomForestRegressor(n_estimators=60, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1)}
    evaluations = []
    predictions = {"seasonal_naive": test["lag_7"].to_numpy()}
    evaluations.append({"model": "seasonal_naive", **metrics(test["units_sold"], predictions["seasonal_naive"])})
    for name, model in candidates.items():
        model.fit(train[FEATURES], train["units_sold"])
        predictions[name] = np.maximum(0, model.predict(test[FEATURES]))
        evaluations.append({"model": name, **metrics(test["units_sold"], predictions[name])})
    scores = pd.DataFrame(evaluations).sort_values("MAE").reset_index(drop=True)
    best_name = str(scores.iloc[0]["model"])
    # Refit selected ML model on all available history for deployment.
    if best_name != "seasonal_naive":
        best = candidates[best_name]
        best.fit(feature_df[FEATURES], feature_df["units_sold"])
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": best, "features": FEATURES, "name": best_name}, MODEL)
    else:
        MODEL.unlink(missing_ok=True)
    return best_name, scores, pd.DataFrame({"date": test["date"], "store_id": test["store_id"], "product_id": test["product_id"], "actual": test["units_sold"], "predicted": predictions[best_name]})

def forecast_recursive(history_df, horizon, model_name, model=None):
    """Forecast from an origin without using future actual sales."""
    rows = []
    for (store, product), group in history_df.groupby(["store_id", "product_id"]):
        group = group.sort_values("date")
        history = group["units_sold"].astype(float).tolist()
        last_date = pd.Timestamp(group["date"].max())
        for day in range(1, horizon + 1):
            date = last_date + pd.Timedelta(days=day)
            if model_name == "seasonal_naive":
                prediction = history[-7]
            else:
                features = pd.DataFrame([next_features(store, product, date, history)])[FEATURES]
                prediction = float(model.predict(features)[0])
            prediction = max(0.0, float(prediction))
            rows.append({"date": date, "store_id": store, "product_id": product, "predicted_demand": round(prediction, 2)})
            history.append(prediction)
    return pd.DataFrame(rows)

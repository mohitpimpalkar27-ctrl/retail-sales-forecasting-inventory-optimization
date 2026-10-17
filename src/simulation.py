"""Deterministic stock-flow simulator. Supplier lead time is in whole days."""
import math
import pandas as pd
from src.inventory import reorder_point, order_quantity

def simulate_policy(actual, forecast, starting_stock, lead_days, policy="forecast", review_days=7):
    """One store-product, daily orders; deliveries arrive at START of due date.

    Actual is a historical held-out demand sequence. Forecast is fixed at the
    simulation start; future actuals are NEVER used for planning.
    """
    if policy not in {"forecast", "fixed"}:
        raise ValueError("Unknown policy")
    if lead_days < 1:
        raise ValueError("Lead time must be >= 1")
    actual = list(map(int, actual))
    forecast = list(map(float, forecast))
    if len(actual) != len(forecast):
        raise ValueError("Actual and forecast lengths differ")
    stock, pipeline, rows = int(starting_stock), [], []
    # Fixed policy uses an externally supplied baseline from the forecast's first day.
    baseline_daily = max(0.0, forecast[0]) if forecast else 0.0
    for day, demand in enumerate(actual):
        arrivals = sum(q for due, q in pipeline if due == day)
        pipeline = [(due, q) for due, q in pipeline if due != day]
        stock += arrivals
        opening = stock
        sold = min(stock, demand)
        lost = demand - sold
        stock -= sold
        # Only current and future forecasts are available to the planner.
        if policy == "forecast":
            future = forecast[day:day + lead_days + review_days]
            if len(future) < lead_days + review_days:
                future += [forecast[-1]] * (lead_days + review_days - len(future))
            lead_need = sum(future[:lead_days])
            target = math.ceil(sum(future))
            threshold = math.ceil(lead_need)
        else:
            threshold = math.ceil(baseline_daily * lead_days)
            target = math.ceil(baseline_daily * (lead_days + review_days))
        position = stock + sum(q for _, q in pipeline)
        order = order_quantity(position, threshold, target)
        if order:
            pipeline.append((day + lead_days, order))
        rows.append({"day": day + 1, "opening_stock": opening, "arrivals": arrivals,
                     "demand": demand, "units_sold": sold, "lost_units": lost,
                     "closing_stock": stock, "ordered": order, "on_order": sum(q for _, q in pipeline),
                     "policy": policy})
    return pd.DataFrame(rows)

def summarize_simulation(df, holding_cost_per_unit_day=0.1, order_cost=25.0):
    demand = df.demand.sum()
    return {"policy": str(df.policy.iloc[0]),
            "fill_rate_percent": round(100 * df.units_sold.sum() / max(demand, 1), 2),
            "stockout_days": int((df.lost_units > 0).sum()),
            "lost_units": int(df.lost_units.sum()),
            "average_closing_stock": round(float(df.closing_stock.mean()), 2),
            "holding_cost": round(float(df.closing_stock.sum() * holding_cost_per_unit_day), 2),
            "ordering_cost": round(float((df.ordered > 0).sum() * order_cost), 2)}

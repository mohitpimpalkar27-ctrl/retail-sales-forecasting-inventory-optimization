import math
import pandas as pd
from src.inventory import safety_stock, reorder_point, inventory_position, order_quantity

def recommend(forecast, history, inventory, suppliers, review_days=7):
    rows = []
    for (store, product), f in forecast.groupby(["store_id", "product_id"]):
        inv = inventory[(inventory.store_id == store) & (inventory.product_id == product)].iloc[0]
        sup = suppliers[suppliers.product_id == product].iloc[0]
        past = history[(history.store_id == store) & (history.product_id == product)].sort_values("date").tail(60)
        daily = float(f.predicted_demand.mean())
        std = float(past.units_sold.std(ddof=1)) if len(past) > 1 else 0
        lead = int(sup.lead_time_days)
        reserve = safety_stock(std, lead)
        threshold = reorder_point(daily, lead, reserve)
        position = inventory_position(int(inv.on_hand), int(inv.on_order), int(inv.backorders))
        # Target covers lead time plus one review cycle, plus the same safety stock.
        target = math.ceil(daily * (lead + review_days) + reserve)
        quantity = order_quantity(position, threshold, target)
        rows.append({"store_id": store, "product_id": product, "daily_forecast": round(daily, 2),
                     "on_hand": int(inv.on_hand), "on_order": int(inv.on_order),
                     "lead_time_days": lead, "safety_stock": reserve, "reorder_point": threshold,
                     "inventory_position": position, "target_stock": target,
                     "suggested_order": quantity, "status": "REORDER" if quantity else "OK"})
    return pd.DataFrame(rows).sort_values(["status", "store_id", "product_id"])

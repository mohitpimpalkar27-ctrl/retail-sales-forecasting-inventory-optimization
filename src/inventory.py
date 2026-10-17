"""Simple continuous-review reorder point and order-up-to policy."""
import math
import numpy as np

def safety_stock(daily_std, lead_days, z=1.65):
    if daily_std < 0 or lead_days < 0:
        raise ValueError("Std dev and lead time must be nonnegative")
    return math.ceil(z * daily_std * math.sqrt(lead_days))

def reorder_point(daily_demand, lead_days, reserve):
    return math.ceil(daily_demand * lead_days + reserve)

def inventory_position(on_hand, on_order, backorders=0):
    return on_hand + on_order - backorders

def order_quantity(position, threshold, target):
    return max(0, math.ceil(target - position)) if position <= threshold else 0

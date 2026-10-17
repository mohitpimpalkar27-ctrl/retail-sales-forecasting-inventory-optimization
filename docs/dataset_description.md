# Dataset

All datasets in the starter are **synthetic** and reproducible with seed 42.

Sales fields: date, store_id, product_id, product_name, category, units_sold, unit_price.
Inventory fields: store_id, product_id, on_hand, on_order, backorders.
Supplier fields: product_id, supplier_id, lead_time_days, unit_cost.

The generator creates 3 stores × 6 products × 300 consecutive days, with weekends, seasonal sinusoid, trend and random noise.

To use real public sales data later, adapt its schema to the expected columns, respect licensing, and verify the interpretation of missing days and censored sales.

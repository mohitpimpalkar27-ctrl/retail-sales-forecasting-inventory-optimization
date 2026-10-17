# Methodology

Forecasts: one-step chronological holdout comparison; best model refit on all history; 14-day recursive inference.

Inventory: `SS = ceil(z * std(demand) * sqrt(lead_days))`, with z=1.65, constant lead time and approximate independent demand; `ROP = ceil(avg_forecast * lead_days + SS)`; `IP = on_hand + on_order - backorders`; if IP <= ROP, order `max(0, target - IP)` where target covers lead + review days + SS.

Simulation: 28-day historical synthetic holdout; forecasting model trained on pre-holdout history; fixed forecast at origin; same realized demand for both policies. Baseline and forecast policies in simulation do not use safety stock; simulation is illustrative rather than a controlled out-of-sample business performance study.

# Architecture

Synthetic sales generator → data loader → preprocessing → feature engineering → chronological model comparison → recursive forecast → inventory calculations → reorder recommendations → Streamlit dashboard.

Parallel path: train-at-origin forecast → held-out actual synthetic demand → two inventory policy simulations → KPI comparison → dashboard.

EDA generates PNG charts; CSVs are saved under outputs and reports.

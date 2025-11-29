import pandas as pd
import numpy as np

# ====== CONFIG ======
FILE_PATH = "/content/superjoin_large/forecasting_large (1).xlsx"
TOLERANCE = 0.01  # 1%

# ====== LOAD SHEETS ======
hist_df = pd.read_excel(FILE_PATH, sheet_name="historical_revenue")

# ✅ HEADER IS ON ROW 7 → index 6
forecast_df = pd.read_excel(
    FILE_PATH,
    sheet_name="Revenue_Forecast",
    header=6
)

# ====== CLEAN HISTORICAL DATA ======
hist_df["Revenue"] = pd.to_numeric(hist_df["Revenue"], errors="coerce")
hist_df = hist_df.dropna(subset=["Revenue"])

# ====== CALCULATE CMGR ======
start_val = hist_df["Revenue"].iloc[0]
end_val = hist_df["Revenue"].iloc[-1]
periods = len(hist_df) - 1

cmgr = (end_val / start_val) ** (1 / periods) - 1
print("Calculated CMGR:", round(cmgr * 100, 4), "%")

# ====== RECOMPUTE EXPECTED FORECAST ======
expected_forecast = []
current_val = end_val

for _ in range(6):
    current_val *= (1 + cmgr)
    expected_forecast.append(round(current_val, 2))

# ====== AUTO-DETECT FORECAST COLUMN ======
print("Detected forecast table columns:", list(forecast_df.columns))

forecast_col = None
for col in forecast_df.columns:
    if "forecast" in col.lower() or "revenue" in col.lower():
        forecast_col = col
        break

if forecast_col is None:
    raise ValueError("❌ No forecast revenue column found.")

model_forecast = pd.to_numeric(
    forecast_df[forecast_col], errors="coerce"
).dropna().values[:6]

# ====== VALIDATE ======
results = []

for i in range(6):
    actual = model_forecast[i]
    expected = expected_forecast[i]
    error_pct = abs(actual - expected) / expected

    results.append({
        "Month": f"M{37+i}",
        "Expected": round(expected, 2),
        "Model_Output": round(actual, 2),
        "Error_%": round(error_pct * 100, 4),
        "Pass": error_pct <= TOLERANCE
    })

# ====== FINAL RESULT ======
result_df = pd.DataFrame(results)
overall_status = "PASS ✅" if result_df["Pass"].all() else "FAIL ❌"

print("\n===== FORECAST EVALUATION RESULT =====")
print(result_df)
print("\nFINAL STATUS:", overall_status)

# ====== SAVE CSV ======
result_df.to_csv("forecast_eval_results.csv", index=False)
print("\nSaved: forecast_eval_results.csv")

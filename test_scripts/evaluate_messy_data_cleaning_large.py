import pandas as pd
import re

# ====== CONFIG ======
FILE_PATH = "/content/superjoin_large/messy_data_cleaning_large.xlsx" 
SHEET_NAME = "Cleaned_Data"

# ====== LOAD CLEANED DATA ======
df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)

print("Total cleaned rows:", len(df))
print("Detected columns:", list(df.columns))

# ====== RESULT TRACKER ======
results = {
    "valid_revenue": True,
    "title_case_names": True,
    "valid_dates": True,
    "no_duplicate_orderid": True,
    "correct_columns": True,
}

# ====== 1️⃣ COLUMN VALIDATION ======
expected_cols = {"OrderID", "Customer_Name", "revenue", "Order Date"}
if set(df.columns) != expected_cols:
    results["correct_columns"] = False

# ====== 2️⃣ REVENUE VALIDATION ======
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
if df["revenue"].isna().any():
    results["valid_revenue"] = False

# ====== 3️⃣ CUSTOMER NAME TITLE CASE CHECK ======
def is_title_case(name):
    return bool(re.match(r"^([A-Z][a-z]+)(\s[A-Z][a-z]+)*$", str(name)))

invalid_names = df[~df["Customer_Name"].apply(is_title_case)]
if len(invalid_names) > 0:
    results["title_case_names"] = False

# ====== 4️⃣ DATE FORMAT CHECK (YYYY-MM-DD) ======
date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

df["Order Date"] = df["Order Date"].astype(str)
invalid_dates = df[~df["Order Date"].apply(lambda x: bool(date_pattern.match(x)))]

if len(invalid_dates) > 0:
    results["valid_dates"] = False

# ====== 5️⃣ DUPLICATE ORDERID CHECK ======
if df["OrderID"].duplicated().any():
    results["no_duplicate_orderid"] = False

# ====== FINAL REPORT ======
report_rows = []

for k, v in results.items():
    report_rows.append({
        "Check": k,
        "Status": "PASS ✅" if v else "FAIL ❌"
    })

report_df = pd.DataFrame(report_rows)

overall_status = "PASS ✅" if all(results.values()) else "FAIL ❌"

print("\n===== CLEANING EVALUATION REPORT =====")
print(report_df)
print("\nFINAL STATUS:", overall_status)

# ====== SAVE REPORT ======
report_df.to_csv("messy_cleaning_eval_results.csv", index=False)
print("\nSaved: messy_cleaning_eval_results.csv")

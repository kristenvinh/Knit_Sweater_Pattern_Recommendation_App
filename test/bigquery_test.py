import os
from google.cloud import bigquery

# --- Configuration ---
GCP_PROJECT = "knitwear-app"
eval_folders = [
    "Evaluation_Sweaters/pullovers",
    "Evaluation_Sweaters/cardigans"
]

# --- Extract Local IDs ---
local_pattern_ids = []
for folder in eval_folders:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Extract numeric ID from "123456.jpeg" -> 123456
                pid_str = os.path.splitext(fname)[0]
                if pid_str.isdigit():
                    local_pattern_ids.append(int(pid_str))

print(f"Extracted {len(local_pattern_ids)} total evaluation IDs from local folders.")

# --- Check BigQuery ---
bq_client = bigquery.Client(project=GCP_PROJECT)
ids_str = ", ".join(str(pid) for pid in local_pattern_ids)

sql = f"""
SELECT DISTINCT pattern_id 
FROM `{GCP_PROJECT}.ravelry_data.dim_patterns`
WHERE pattern_id IN ({ids_str})
"""

bq_ids = set(bq_client.query(sql).to_dataframe()["pattern_id"].tolist())
missing_ids = [pid for pid in local_pattern_ids if pid not in bq_ids]

print(f"Found in BigQuery: {len(bq_ids)} / {len(local_pattern_ids)}")
if missing_ids:
    print(f"Missing IDs ({len(missing_ids)}): {missing_ids}")
else:
    print("All evaluation patterns are present in BigQuery!")
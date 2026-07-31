import os
import time
import numpy as np
import pandas as pd
from google.cloud import bigquery
from extract_features import extract_features

# --- Configuration ---
GCP_PROJECT = "knitwear-app"
test_image_folders = [
    'Evaluation_Sweaters_Sampled/pullovers',
    'Evaluation_Sweaters_Sampled/cardigans'
]
valid_image_extensions = ('.jpg', '.jpeg', '.png')
num_recommendations = 20
csv_output_filename = "evaluation_results_recall_20.csv"  # New: Define the output file name

bq_client = bigquery.Client(project=GCP_PROJECT)

def query_bigquery_vector_search(query_vector, top_k=10):
    """Executes COSINE vector search in BigQuery."""
    sql = f"""
    SELECT base.pattern_id, distance AS image_distance
    FROM VECTOR_SEARCH(
      TABLE `{GCP_PROJECT}.ravelry_data.dim_pattern_image_embeddings_Dino3_filtered`,
      'image_embedding',
      (SELECT @vec AS image_embedding),
      top_k => {top_k}, distance_type => 'COSINE'
    );
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("vec", "FLOAT64", query_vector)]
    )
    df = bq_client.query(sql, job_config=job_config).to_dataframe()
    return df['pattern_id'].tolist()

# --- Run Evaluation Across Folders ---
all_query_times_ms = []
all_hits = []
results_data = []  # New: List to hold row data for the CSV

for folder in test_image_folders:
    if not os.path.isdir(folder):
        print(f"Skipping missing directory: {folder}")
        continue
        
    print(f"\n--- Processing Evaluation Folder: {folder} ---")
    image_files = [f for f in sorted(os.listdir(folder)) if f.lower().endswith(valid_image_extensions)]
    
    for i, fname in enumerate(image_files, start=1):
        test_image_path = os.path.join(folder, fname)
        raw_id = os.path.splitext(fname)[0]
        ground_truth_id = int(raw_id) if raw_id.isdigit() else raw_id
        
        print(f"\n=============================================")
        print(f"Testing [{folder}] Image {i}/{len(image_files)}: {fname}")
        print(f"  > Ground Truth Pattern ID: {ground_truth_id}")
        
        # 1. Feature Extraction
        _, query_vector = extract_features(test_image_path)
        if not isinstance(query_vector, np.ndarray):
            print("  > ERROR: Feature extraction failed.")
            continue
            
        # 2. BigQuery Search & Timing
        start_time = time.perf_counter()
        recs = query_bigquery_vector_search(query_vector.tolist(), top_k=num_recommendations)
        end_time = time.perf_counter()
        
        query_time_ms = (end_time - start_time) * 1000
        all_query_times_ms.append(query_time_ms)
        
        # 3. Hit / Miss Check
        print(f"  > Query Time: {query_time_ms:.2f} ms")
        print(f"  > Recommended IDs: {recs}")
        
        is_hit = 1 if ground_truth_id in recs else 0
        if is_hit:
            all_hits.append(1)
            print(f"  > RESULT: HIT! ID {ground_truth_id} was returned.")
        else:
            all_hits.append(0)
            print(f"  > RESULT: MISS. ID {ground_truth_id} was not returned.")
            
        # New: Append data for this image to our results list
        results_data.append({
            'Category': os.path.basename(folder),
            'Filename': fname,
            'Ground_Truth_ID': ground_truth_id,
            'Hit': is_hit,
            'Query_Time_ms': round(query_time_ms, 2),
            'Recommendations': str(recs)
        })

# --- Summary Metrics & CSV Export ---
if all_hits:
    total_processed = len(all_hits)
    num_hits = sum(all_hits)
    recall = (num_hits / total_processed) * 100
    avg_latency = np.mean(all_query_times_ms)
    
    print("\n================== FINAL EVALUATION METRICS ==================")
    print(f"Total Sweaters Processed: {total_processed}")
    print(f"Recall@{num_recommendations}: {recall:.2f}% ({num_hits}/{total_processed} hits)")
    print(f"Average Query Latency: {avg_latency:.2f} ms")
    print("==============================================================")
    
    # New: Export to CSV using pandas
    df_results = pd.DataFrame(results_data)
    df_results.to_csv(csv_output_filename, index=False)
    print(f"\nRow-level evaluation results exported successfully to: {csv_output_filename}")
import os
import urllib.parse
import time
import requests
import pandas as pd
from google.cloud import bigquery, storage
from google.oauth2 import service_account


# --- Configuration ---
BUCKET_NAME = 'knitwear-pattern-images' # <-- Replace with your actual GCS bucket name
CREDENTIALS_PATH = 'src/knitwear-app-37e6574c4829.json' 

def stream_images_to_gcs():
    # 1. Initialize Google Cloud credentials
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    
    # 2. Initialize BigQuery and GCS clients
    bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    gcs_client = storage.Client(credentials=credentials, project=credentials.project_id)
    bucket = gcs_client.bucket(BUCKET_NAME)

    # 3. Query BigQuery for up to 5 photos per pattern
    query = """
        SELECT pattern_id, photo_url
        FROM (
            SELECT 
                pattern_id, 
                photo_url, 
                ROW_NUMBER() OVER(PARTITION BY pattern_id ORDER BY sort_order) as rn
            FROM `knitwear-app.ravelry_data.dim_pattern_photos`
        )
        WHERE rn <= 5
        ORDER BY pattern_id, rn
        LIMIT 10000
    """
    
    print("Extracting photo URLs from BigQuery...")
    df = bq_client.query(query).to_dataframe()
    
    # Group by pattern to manage files as sub-folders
    grouped_patterns = df.groupby('pattern_id')
    total_patterns = len(grouped_patterns)
    
    print(f"Found {total_patterns} unique patterns to process. Starting streaming to GCS...")

    processed_count = 0
    skipped_count = 0
    uploaded_images_count = 0
    print_interval = 50

    for pattern_id, group in grouped_patterns:
        try:
            # We will name files inside GCS using a folder structure: pattern_ID/01.jpg, pattern_ID/02.jpg...
            # To see if we can skip this pattern, check if the first image already exists in GCS
            first_blob = bucket.blob(f"pattern_{pattern_id}/01.jpg")
            if first_blob.exists():
                skipped_count += 1
                continue

            img_num = 1
            for _, row in group.iterrows():
                url = row['photo_url']
                if pd.isna(url):
                    continue
                
                try:
                    # Clean and encode URL paths (handles spaces, special chars)
                    parts = urllib.parse.urlsplit(url)
                    safe_path = urllib.parse.quote(parts.path)
                    safe_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment))

                    # Download image bytes into memory
                    response = requests.get(safe_url, timeout=10)
                    response.raise_for_status()

                    # Define target GCS path and upload raw bytes in-memory
                    blob_name = f"pattern_{pattern_id}/{img_num:02d}.jpg"
                    blob = bucket.blob(blob_name)
                    blob.upload_from_string(response.content, content_type='image/jpeg')

                    img_num += 1
                    uploaded_images_count += 1
                    time.sleep(0.1) # Soft rate-limiting to be nice to Ravelry's CDN
                    
                except Exception as e:
                    print(f"Failed on image {img_num} for pattern {pattern_id}: {e}")

        except Exception as e:
            print(f"Error processing pattern {pattern_id}: {e}")
            pass

        processed_count += 1
        
        # Periodic progress updates
        if (processed_count + skipped_count) % print_interval == 0:
            status_text = f"Checked {processed_count + skipped_count} of {total_patterns} patterns (Uploaded: {uploaded_images_count} images, Skipped: {skipped_count} patterns)..."
            print(status_text)

    print("\n--- Pipeline Completed ---")
    print(f"Total patterns processed: {processed_count}")
    print(f"Total patterns skipped: {skipped_count}")
    print(f"Total images uploaded: {uploaded_images_count}")

if __name__ == '__main__':
    stream_images_to_gcs()
import os
import urllib.parse
import time
import requests
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# --- Configuration ---
LOCAL_SAVE_DIR = '/Volumes/Extreme Pro/sweater_photos'
CREDENTIALS_PATH = 'src/knitwear-app-37e6574c4829.json' 

def stream_images_to_local():
    # 1. Initialize Google Cloud credentials for BigQuery
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    
    # Ensure the base directory exists
    os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

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
    """
    
    print("Extracting photo URLs from BigQuery...")
    df = bq_client.query(query).to_dataframe()
    
    # Group by pattern to manage files as sub-folders
    grouped_patterns = df.groupby('pattern_id')
    total_patterns = len(grouped_patterns)
    
    print(f"Found {total_patterns} unique patterns to process. Starting download to local drive...")

    processed_count = 0
    skipped_count = 0
    downloaded_images_count = 0
    print_interval = 50

    for pattern_id, group in grouped_patterns:
        try:
            # Set up local folder for this specific pattern
            # Note: Removed the "pattern_" prefix to match your build_vectors.py structure
            pattern_dir = os.path.join(LOCAL_SAVE_DIR, str("pattern_" + str(pattern_id)))
            
            # Check if the first image already exists to skip
            first_file_path = os.path.join(pattern_dir, "01.jpg")
            if os.path.exists(first_file_path):
                skipped_count += 1
                continue

            # Create the folder since we need to download
            os.makedirs(pattern_dir, exist_ok=True)

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

                    # Write raw bytes to local disk
                    file_path = os.path.join(pattern_dir, f"{img_num:02d}.jpg")
                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    img_num += 1
                    downloaded_images_count += 1
                    time.sleep(0.1) # Soft rate-limiting to be nice to Ravelry's CDN
                    
                except Exception as e:
                    print(f"Failed on image {img_num} for pattern {pattern_id}: {e}")

        except Exception as e:
            print(f"Error processing pattern {pattern_id}: {e}")
            pass

        processed_count += 1
        
        # Periodic progress updates
        if (processed_count + skipped_count) % print_interval == 0:
            status_text = f"Checked {processed_count + skipped_count} of {total_patterns} patterns (Downloaded: {downloaded_images_count} images, Skipped: {skipped_count} patterns)..."
            print(status_text)

    print("\n--- Pipeline Completed ---")
    print(f"Total patterns processed: {processed_count}")
    print(f"Total patterns skipped: {skipped_count}")
    print(f"Total images downloaded: {downloaded_images_count}")

if __name__ == '__main__':
    stream_images_to_local()
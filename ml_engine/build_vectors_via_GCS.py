import os
import sys
import pickle
import numpy as np
import cv2
from sklearn.cluster import KMeans
from google.cloud import storage

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from feature_extraction import extract_features

# --- Configuration ---
BUCKET_NAME = 'knitwear-pattern-images'
CREDENTIALS_PATH = 'ml_engine/knitwear-app-37e6574c4829.json' # Adjust to your actual key path
n_clusters = 3 

# Filenames
features_file = 'master_features_DINO_yolo_pose_multicentroid.npy'
pattern_ids_file = 'pattern_ids_DINO_yolo_pose_multicentroid.pkl'
pattern_mapping_file = 'pattern_to_centroids_DINO_yolo_pose_multicentroid.pkl'

def build_vectors():
    pattern_to_centroid_indices = {}
    all_centroids = []
    pattern_ids = []
    
    # Initialize GCS Client
    storage_client = storage.Client.from_service_account_json(CREDENTIALS_PATH)
    bucket = storage_client.bucket(BUCKET_NAME)

    # Get unique pattern folders by looking at blob prefixes
    blobs = storage_client.list_blobs(BUCKET_NAME)
    
    # Extract unique pattern IDs from the folder paths (e.g., "pattern_12345/")
    pattern_folders = set()
    for blob in blobs:
        folder_name = blob.name.split('/')[0]
        if folder_name.startswith('pattern_'):
            pattern_folders.add(folder_name)
            
    pattern_folders = sorted(list(pattern_folders))
    print(f"Found {len(pattern_folders)} patterns in GCS bucket.")

    for pattern_folder in pattern_folders:
        pattern_id = pattern_folder.replace('pattern_', '')
        pattern_feature_list = []
        
        # Get all images within this specific pattern's folder
        image_blobs = list(bucket.list_blobs(prefix=f"{pattern_folder}/"))
        
        if not image_blobs:
            continue

        for blob in image_blobs:
            if not blob.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            try:
                # Download image as raw bytes into memory
                image_bytes = blob.download_as_bytes()
                
                # Convert raw bytes to a numpy array for OpenCV
                nparr = np.frombuffer(image_bytes, np.uint8)
                img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # We need to temporarily save it to a local tmp file OR 
                # modify `extract_features` / `extract_and_crop_image` to accept a cv2 image object instead of a path.
                # The easiest zero-refactor method is writing a quick temp file:
                temp_path = "temp_processing_image.jpg"
                cv2.imwrite(temp_path, img_cv2)

                # Pass to your existing DINO script
                _, feature_vector = extract_features(temp_path)

                if feature_vector is not None and isinstance(feature_vector, np.ndarray):
                    pattern_feature_list.append(feature_vector)
                    
                # Clean up the temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                print(f"  Warning: Failed to process {blob.name}: {e}")
                continue

        if not pattern_feature_list:
            print(f"  Skipping {pattern_id}: no valid features extracted")
            continue

        pattern_feature_array = np.array(pattern_feature_list)
        n_samples = len(pattern_feature_array)
        n_centroids = min(n_clusters, n_samples) 
        
        if n_centroids < 2:
            kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
            kmeans.fit(pattern_feature_array)
            centroids = kmeans.cluster_centers_
        else:
            kmeans = KMeans(n_clusters=n_centroids, random_state=42, n_init=10)
            kmeans.fit(pattern_feature_array)
            centroids = kmeans.cluster_centers_
        
        start_idx = len(all_centroids)
        for centroid in centroids:
            all_centroids.append(centroid)
        
        centroid_indices = list(range(start_idx, len(all_centroids)))
        pattern_to_centroid_indices[pattern_id] = centroid_indices
        pattern_ids.append(pattern_id)
        
        print(f"  ✓ Pattern {pattern_id}: {n_samples} images -> {len(centroids)} centroids")

    if not all_centroids:
        print("Error: No valid patterns with features")
        return None, None, None

    all_centroids_array = np.array(all_centroids, dtype='float32')
    
    np.save(features_file, all_centroids_array)
    
    with open(pattern_ids_file, 'wb') as f:
        pickle.dump(pattern_ids, f)
    
    with open(pattern_mapping_file, 'wb') as f:
        pickle.dump(pattern_to_centroid_indices, f)
    
    print(f"\nSaved multi-centroid index:")
    print(f"  Total patterns: {len(pattern_ids)}")
    print(f"  Total centroids: {len(all_centroids)}")

    return all_centroids_array, pattern_ids, pattern_to_centroid_indices
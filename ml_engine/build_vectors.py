# --- Setup ---
import os
import sys
import pickle
import numpy as np
from sklearn.cluster import KMeans

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from feature_extraction import extract_features


feature_dim = 768 # Feature dimension for DINO features
data_directory = '/Volumes/Extreme Pro/sweater_photos'  
n_clusters = 4   # K-means clusters per pattern (3-5 recommended, 4 is good balance)
CHECKPOINT_INTERVAL = 50  # Save progress every 50 patterns
# Filenames
features_file = 'features_DINO_yolo_pose_multicentroid.npy'
pattern_ids_file = 'pattern_ids_DINO_yolo_pose_multicentroid.pkl'
pattern_mapping_file = 'pattern_to_centroids_DINO_yolo_pose_multicentroid.pkl'
# ---

def build_vectors():
    """
    Build multi-centroid feature vectors for each pattern using K-means clustering.
    Includes auto-resume and incremental checkpointing.
    """
    pattern_to_centroid_indices = {}
    all_centroids = []
    pattern_ids = []
    
    # --- NEW: Auto-Resume Logic ---
    if os.path.exists(features_file) and os.path.exists(pattern_ids_file) and os.path.exists(pattern_mapping_file):
        print("Found existing progress! Loading checkpoint...")
        # Load the numpy array and convert back to list for appending
        all_centroids = np.load(features_file).tolist()
        
        with open(pattern_ids_file, 'rb') as f:
            pattern_ids = pickle.load(f)
            
        with open(pattern_mapping_file, 'rb') as f:
            pattern_to_centroid_indices = pickle.load(f)
            
        print(f"Resuming pipeline. {len(pattern_ids)} patterns already processed.")
    else:
        print("No previous checkpoint found. Starting fresh.")
    # ------------------------------
    
    if not os.path.isdir(data_directory):
        print(f"Error: Data directory '{data_directory}' not found")
        return None, None, None

    pattern_folders = sorted([d for d in os.listdir(data_directory) 
                             if os.path.isdir(os.path.join(data_directory, d))])

    processed_since_last_save = 0

    for pattern_id in pattern_folders:
        # --- NEW: Skip already processed patterns ---
        if pattern_id in pattern_to_centroid_indices:
            continue
        # ------------------------------------------

        pattern_folder_path = os.path.join(data_directory, pattern_id)
        pattern_feature_list = []
        
        # Explicitly ignore macOS hidden '._' files
        image_files = [f for f in os.listdir(pattern_folder_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('._')]
                      
        if not image_files:
            print(f"  Skipping {pattern_id}: no images found")
            continue

        # Extract features for all images in this pattern
        for img_name in image_files:
            img_path = os.path.join(pattern_folder_path, img_name)
            try:
                _, feature_vector = extract_features(img_path)

                if feature_vector is not None and isinstance(feature_vector, np.ndarray):
                    pattern_feature_list.append(feature_vector)
            except Exception as e:
                print(f"  Warning: Failed to extract features from {img_name}: {e}")
                continue

        if not pattern_feature_list:
            print(f"  Skipping {pattern_id}: no valid features extracted")
            continue

        pattern_feature_array = np.array(pattern_feature_list)
        
        # Apply K-means clustering on this pattern's features
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
        
        # Store this pattern's centroids
        start_idx = len(all_centroids)
        for centroid in centroids:
            all_centroids.append(centroid)
        
        # Map pattern to its centroid indices
        centroid_indices = list(range(start_idx, len(all_centroids)))
        pattern_to_centroid_indices[pattern_id] = centroid_indices
        pattern_ids.append(pattern_id)
        
        print(f"  ✓ {pattern_id}: {n_samples} images -> {len(centroids)} centroids")

        # --- NEW: Checkpoint Save Logic ---
        processed_since_last_save += 1
        if processed_since_last_save >= CHECKPOINT_INTERVAL:
            print(f"\n--- Reached {CHECKPOINT_INTERVAL} new patterns. Saving checkpoint... ---")
            
            # Save all centroids
            np.save(features_file, np.array(all_centroids, dtype='float32'))
            
            # Save pattern IDs
            with open(pattern_ids_file, 'wb') as f:
                pickle.dump(pattern_ids, f)
            
            # Save pattern-to-centroid mapping
            with open(pattern_mapping_file, 'wb') as f:
                pickle.dump(pattern_to_centroid_indices, f)
                
            processed_since_last_save = 0
            print("--- Checkpoint secured. ---\n")
        # ----------------------------------

    if not all_centroids:
        print("Error: No valid patterns with features")
        return None, None, None

    # Final save to capture anything remaining after the last checkpoint
    all_centroids_array = np.array(all_centroids, dtype='float32')
    np.save(features_file, all_centroids_array)
    
    with open(pattern_ids_file, 'wb') as f:
        pickle.dump(pattern_ids, f)
    
    with open(pattern_mapping_file, 'wb') as f:
        pickle.dump(pattern_to_centroid_indices, f)
    
    print(f"\nExtraction Complete & Saved:")
    print(f"  Total patterns: {len(pattern_ids)}")
    print(f"  Total centroids: {len(all_centroids)}")
    print(f"  Average centroids per pattern: {len(all_centroids) / len(pattern_ids):.2f}")

    return all_centroids_array, pattern_ids, pattern_to_centroid_indices
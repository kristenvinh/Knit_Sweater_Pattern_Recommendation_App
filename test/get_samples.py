import os
import random
import shutil

# --- Configuration ---
SOURCE_FOLDERS = {
    'pullovers': 'Evaluation_Sweaters/pullovers',
    'cardigans': 'Evaluation_Sweaters/cardigans'
}

DEST_ROOT = 'Evaluation_Sweaters_Sampled'
NUM_SAMPLES = 25
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')

def sample_images_from_existing_folders():
    total_copied = 0

    for category, src_dir in SOURCE_FOLDERS.items():
        if not os.path.exists(src_dir):
            print(f"Error: Source directory '{src_dir}' not found.")
            continue

        # Get valid image files (ignoring macOS hidden files and any files marked '_skipped')
        image_files = [
            f for f in os.listdir(src_dir)
            if f.lower().endswith(VALID_EXTENSIONS) 
            and not f.startswith('._') 
            and '_skipped' not in f.lower()
        ]

        # Check if we have enough images to sample
        available_count = len(image_files)
        if available_count < NUM_SAMPLES:
            print(f"Warning: '{src_dir}' only has {available_count} valid images. Selecting all {available_count}.")
            selected_files = image_files
        else:
            selected_files = random.sample(image_files, NUM_SAMPLES)

        # Create destination directory (e.g., Evaluation_Sweaters_Sampled/pullovers)
        dest_dir = os.path.join(DEST_ROOT, category)
        os.makedirs(dest_dir, exist_ok=True)

        print(f"\nSampling {len(selected_files)} images from '{src_dir}' into '{dest_dir}'...")
        for fname in selected_files:
            src_path = os.path.join(src_dir, fname)
            dest_path = os.path.join(dest_dir, fname)
            shutil.copy2(src_path, dest_path)
            total_copied += 1
            print(f"  ✓ Copied: {fname}")

    print(f"\n--- Complete! Copied {total_copied} total images to '{DEST_ROOT}' ---")

if __name__ == "__main__":
    sample_images_from_existing_folders()
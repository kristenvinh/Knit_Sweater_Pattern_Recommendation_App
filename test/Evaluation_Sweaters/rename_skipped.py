import os

# --- Configuration ---
missing_patterns = [
    7311058, 5870, 817885, 858135, 639347, 381119, 13854, 363242, 
    1138136, 817988, 971112, 543344, 473885, 9042, 602276, 844144, 
    479305, 1196042, 1028254, 1119779, 100136, 132943, 1215387, 
    559137, 397061, 1259525, 13579, 681431, 949096, 7292988, 33875
]

# Convert to a set of strings for fast O(1) string matching
missing_patterns_set = {str(pid) for pid in missing_patterns}

test_image_folders = {
    'pullovers': 'Evaluation_Sweaters/pullovers',
    'cardigans': 'Evaluation_Sweaters/cardigans'
}

valid_image_extensions = ('.jpg', '.jpeg', '.png')

def count_already_skipped():
    """Counts files that already have '_skipped' in their filename."""
    counts = {'pullovers': 0, 'cardigans': 0}
    total_already_skipped = 0

    for category, folder_path in test_image_folders.items():
        if not os.path.exists(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_image_extensions):
                if '_skipped' in filename.lower():
                    counts[category] += 1
                    total_already_skipped += 1

    print("\n--- Already Skipped Files ---")
    print(f"Total already skipped: {total_already_skipped}")
    print(f"Pullovers already skipped: {counts['pullovers']}")
    print(f"Cardigans already skipped: {counts['cardigans']}\n")
    
    return total_already_skipped

def rename_and_count_skipped():
    """Identifies remaining un-skipped files from the missing list and renames them."""
    counts = {'pullovers': 0, 'cardigans': 0}
    rename_count = 0

    for category, folder_path in test_image_folders.items():
        if not os.path.exists(folder_path):
            print(f"Directory not found: {folder_path}")
            continue

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_image_extensions):
                # Skip files that are already marked as skipped
                if '_skipped' in filename.lower():
                    continue

                base_name, extension = os.path.splitext(filename)
                
                # Check if the filename matches an ID in the missing list
                if base_name in missing_patterns_set:
                    counts[category] += 1
                    
                    old_path = os.path.join(folder_path, filename)
                    new_filename = f"{base_name}_skipped{extension}"
                    new_path = os.path.join(folder_path, new_filename)
                    
                    try:
                        os.rename(old_path, new_path)
                        print(f"[{category.capitalize()}] Renamed: {filename} -> {new_filename}")
                        rename_count += 1
                    except OSError as e:
                        print(f"Error renaming {filename}: {e}")

    print("\n--- New Renaming Summary ---")
    print(f"Total NEW files renamed today: {rename_count}")
    print(f"Newly Skipped Pullovers: {counts['pullovers']}")
    print(f"Newly Skipped Cardigans: {counts['cardigans']}")

if __name__ == "__main__":
    count_already_skipped()
    rename_and_count_skipped()
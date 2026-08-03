from mage_ai.io.bigquery import BigQuery
from mage_ai.io.config import ConfigFileLoader
from mage_ai.settings.repo import get_repo_path
from os import path
import pandas as pd
import requests
import time
from os import path
from google.cloud import bigquery
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def get_max_id_from_bq():
    """Queries BigQuery for the highest pattern ID using Mage's IO client."""
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    
    query = """
        SELECT MAX(ID) as max_id 
        FROM `knitwear-app.ravelry_data.catalog_data`
    """
    
    try:
        # Load the query result into a DataFrame
        df = BigQuery.with_config(ConfigFileLoader(config_path, config_profile)).load(query)
        
        # Check if the DataFrame is empty or contains nulls
        if not df.empty and pd.notna(df.iloc[0]['max_id']):
            return int(df.iloc[0]['max_id'])
        return 0
    except Exception as e:
        print(f"Failed to query BigQuery via Mage IO. Defaulting to 0. Error: {e}")
        return 0

def fetch_recent_patterns(craft, pc, api_key, api_secret, max_id, max_pages=10):
    """
    Fetches newly created patterns using date filtering and sort=created.
    """
    endpoint = "https://api.ravelry.com/patterns/search.json"
    all_patterns = []
    page = 1
    
    print(f"Searching for new '{craft}' '{pc}' patterns...")

    while True:
        params = {
            "craft": craft,
            "pc": pc,
            "sort": "created", # Sort by recently added
            "page_size": 100,
            "page": page
        }

        try:
            print(f"Fetching page {page}...")
            response = requests.get(endpoint, auth=(api_key, api_secret), params=params)
            response.raise_for_status()
            data = response.json()
            
            patterns_on_page = data.get('patterns', [])
            if not patterns_on_page:
                print("No more patterns found. Ending search.")
                break
                
            # Filter the page in memory to only keep patterns newer than our max_id
            new_patterns = [p for p in patterns_on_page if p.get('id', 0) > max_id]
            
            all_patterns.extend(new_patterns)
            
            # If the length of new_patterns is less than patterns_on_page, we've hit old data
            if len(new_patterns) < len(patterns_on_page):
                print(f"Encountered patterns with IDs <= {max_id}. Stopping early.")
                break
            
            paginator = data.get('paginator', {})
            if paginator.get('last_page') == page:
                break
                
            if max_pages is not None and page >= max_pages:
                print(f"Reached max_pages limit of {max_pages}.")
                break
                
            page += 1
            time.sleep(1) # Respecting Ravelry's rate limits

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break
            
    # Extract the specific catalog fields
    patterns_data = []
    for pattern in all_patterns:
        first_photo_data = pattern.get('first_photo')
        photo_url = first_photo_data.get('medium2_url') if first_photo_data else None

        patterns_data.append({
            'Name': pattern.get('name'),
            'Designer': pattern.get('designer', {}).get('name'),
            'ID': pattern.get('id'),
            'URL': f"https://www.ravelry.com/patterns/library/{pattern.get('permalink')}",
            'Free': pattern.get('free'),
            'Photo': photo_url,
        })

    return pd.DataFrame(patterns_data)


@data_loader
def load_data_from_api(*args, **kwargs):
    """Main execution block for Mage."""
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config = ConfigFileLoader(config_path, config_profile)
    
    api_key = config.get('RAVELRY_API_KEY')
    api_secret = config.get('RAVELRY_API_SECRET')
    
    # 1. Find the highest ID currently in your database
    current_max_id = get_max_id_from_bq()
    print(f"Current Max ID in BigQuery: {current_max_id}")
    
    # 2. Execute the searches
    df_cardigans = fetch_recent_patterns("knitting", "cardigan", api_key, api_secret, current_max_id)
    df_pullovers = fetch_recent_patterns("knitting", "pullover", api_key, api_secret, current_max_id)
    
    # 3. Combine and deduplicate
    df_combined = pd.concat([df_cardigans, df_pullovers]).drop_duplicates(subset=['ID']).reset_index(drop=True)
    
    if df_combined.empty:
        print("No new patterns found today.")
    else:
        print(f"Found {len(df_combined)} new unique patterns to append.")
    
    return df_combined

@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
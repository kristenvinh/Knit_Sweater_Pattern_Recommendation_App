import pandas as pd
import requests
import time
from os import path
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def fetch_patterns(craft, pc, api_key, api_secret, max_pages=200):
    """
    Helper function based on the original search_patterns logic.
    Fetches paginated results from the Ravelry search API.
    """
    endpoint = "https://api.ravelry.com/patterns/search.json"
    all_patterns = []
    page = 1
    
    print(f"Starting pattern search for craft: '{craft}', category: '{pc}'")

    while True:
        params = {
            "craft": craft,
            "pc": pc,
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
                
            all_patterns.extend(patterns_on_page)
            
            paginator = data.get('paginator', {})
            if paginator.get('last_page') == page:
                print("Reached the last page of results.")
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
    """
    Main execution block for Mage.
    """
    # Point Mage exactly to your io_config.yaml file
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config = ConfigFileLoader(config_path, config_profile)
    
    # Extract the Ravelry keys
    api_key = config.get('RAVELRY_API_KEY')
    api_secret = config.get('RAVELRY_API_SECRET')
    
    # Execute the searches for both categories
    df_cardigans = fetch_patterns("knitting", "cardigan", api_key, api_secret, max_pages=25)
    df_pullovers = fetch_patterns("knitting", "pullover", api_key, api_secret, max_pages=25)
    
    # Combine and deduplicate
    df_combined = pd.concat([df_cardigans, df_pullovers]).drop_duplicates(subset=['ID']).reset_index(drop=True)
    
    print(f"Total unique patterns collected: {len(df_combined)}")
    
    # Return the dataframe so the next Mage block can access it in-memory
    return df_combined

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert len(output) > 0, 'The dataframe is empty'
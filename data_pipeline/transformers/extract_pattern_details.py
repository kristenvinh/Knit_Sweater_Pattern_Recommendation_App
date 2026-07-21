import pandas as pd
import requests
import time
from os import path
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def extract_permalinks(attribute_list):
    """Extracts the 'permalink' value from each dictionary in a list."""
    if not isinstance(attribute_list, list):
        return []
    return [item['permalink'] for item in attribute_list if 'permalink' in item]

def get_pattern_details(pattern_id, api_key, api_secret):
    """Fetches nested details for a given pattern ID with rate limiting."""
    # Strict 0.1s rate limit to prevent IP blocking
    time.sleep(0.1) 
    
    details_url = f"https://api.ravelry.com/patterns/{pattern_id}.json"
    
    try:
        response = requests.get(details_url, auth=(api_key, api_secret))
        response.raise_for_status()
        
        details_data = response.json()
        pattern_data = details_data.get('pattern', {})
        
        # Extract the deep attributes
        craft = pattern_data.get('craft', {}).get('name')
        attributes = pattern_data.get('pattern_attributes', [])
        notes = pattern_data.get('notes', '')
        gauge = pattern_data.get('gauge', None)
        gauge_divisor = pattern_data.get('gauge_divisor', None)
        gauge_pattern = pattern_data.get('gauge_pattern', None)
        pattern_type = pattern_data.get('pattern_type', {}).get('permalink')
        yarn_weight = pattern_data.get('yarn_weight', {}).get('name')
        photos = pattern_data.get('photos', [])
        favorites_count = pattern_data.get('favorites_count', None)
        projects_count = pattern_data.get('projects_count', None)

        return {
            'Craft': craft, 
            'Attributes': extract_permalinks(attributes), 
            'Notes': notes,
            'Gauge': gauge, 
            'Gauge Divisor': gauge_divisor, 
            'Gauge Pattern': gauge_pattern, 
            'Pattern Type': pattern_type, 
            'Yarn Weight': yarn_weight, 
            'Photos': photos,
            'Favorites Count': favorites_count,
            'Projects Count': projects_count
        }

    except requests.exceptions.RequestException as e:
        print(f"Could not fetch data for pattern ID {pattern_id}: {e}")
        # Return empty/null schema if a specific pattern lookup fails
        return {
            'Craft': None, 'Attributes': [], 'Gauge': None, 
            'Gauge Divisor': None, 'Gauge Pattern': None, 
            'Pattern Type': None, 'Yarn Weight': None, 'Photos': []
        }

@transformer
def transform(data, *args, **kwargs):
    """
    Executes the detail extraction over the incoming catalog DataFrame.
    """
    # Point Mage exactly to your io_config.yaml file
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config = ConfigFileLoader(config_path, config_profile)
    
    api_key = config.get('RAVELRY_API_KEY')
    api_secret = config.get('RAVELRY_API_SECRET')
    
    total_patterns = len(data)
    print(f"Starting detail extraction for {total_patterns} patterns...")
    
    details_list = []
    
    # Iterate through the DataFrame to pull details for each ID
    for index, row in data.iterrows():
        pattern_id = row['ID']
        
        # Print a progress update every 100 patterns
        if index % 100 == 0 and index > 0:
            print(f"Processed {index} of {total_patterns} patterns...")
            
        details = get_pattern_details(pattern_id, api_key, api_secret)
        details_list.append(details)
        
    # Convert the extracted dictionaries into a DataFrame
    details_df = pd.DataFrame(details_list)
    
    # Horizontally join the new details columns back to the original catalog data
    enriched_data = pd.concat([data.reset_index(drop=True), details_df.reset_index(drop=True)], axis=1)
    
    print("Detail extraction complete!")
    return enriched_data

@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert 'Gauge' in output.columns, 'Detail columns were not joined successfully'
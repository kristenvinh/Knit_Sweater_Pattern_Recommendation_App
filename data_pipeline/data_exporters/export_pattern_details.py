from mage_ai.settings.repo import get_repo_path
from mage_ai.io.bigquery import BigQuery
from mage_ai.io.config import ConfigFileLoader
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_big_query(df: DataFrame, **kwargs) -> None:
    """
    Exports the staging catalog DataFrame to your BigQuery warehouse.
    """
    # UPDATE THIS: Replace with your actual GCP Project ID and Dataset Name
    table_id = 'knitwear-app.ravelry_data.detail_data'
    
    # Point Mage to your io_config.yaml file
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    # Export the data
    BigQuery.with_config(ConfigFileLoader(config_path, config_profile)).export(
        df,
        table_id,
        if_exists='replace',  # Overwrites the staging table on each run
    )

from google.cloud import bigquery

GCP_PROJECT = "knitwear-app"
bq_client = bigquery.Client(project=GCP_PROJECT)

sql = """
    CREATE OR REPLACE TABLE `knitwear-app.ravelry_data.dim_pattern_image_embeddings_Dino3_filtered` AS
    SELECT e.*
    FROM `knitwear-app.ravelry_data.dim_pattern_image_embeddings_Dino3` AS e
    WHERE e.pattern_id IN (
        SELECT ID 
        FROM `knitwear-app.ravelry_data.catalog_data`
    );
"""

# Execute the query
job = bq_client.query(sql)
job.result() # Wait for the job to complete

print("Filtered table created successfully!")
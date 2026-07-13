CREATE OR REPLACE TABLE `knitwear-app-37e6574c4829.ravelry_data.dim_pattern_photos` AS
SELECT
  CAST(raw.ID AS INT64) AS pattern_id,
  JSON_EXTRACT_SCALAR(photo_obj, '$.medium2_url') AS photo_url,
  CAST(JSON_EXTRACT_SCALAR(photo_obj, '$.sort_order') AS INT64) AS sort_order
FROM
  `knitwear-app-37e6574c4829.ravelry_data.final_pattern_attributes` AS raw,
  UNNEST(JSON_EXTRACT_ARRAY(raw.Photos, '$')) AS photo_obj
WHERE
  raw.Photos IS NOT NULL
  AND raw.Photos != '[]';-- Docs: https://docs.mage.ai/guides/sql-blocks

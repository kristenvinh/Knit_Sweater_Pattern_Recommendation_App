CREATE OR REPLACE TABLE `knitwear-app-37e6574c4829.ravelry_data.bridge_pattern_attributes` AS
SELECT
  CAST(raw.ID AS INT64) AS pattern_id,
  -- JSON_EXTRACT_ARRAY leaves double quotes around strings, so we TRIM them off
  TRIM(attr, '"') AS pattern_attribute
FROM
  `knitwear-app-37e6574c4829.ravelry_data.final_pattern_attributes` AS raw,
  UNNEST(JSON_EXTRACT_ARRAY(raw.Attributes, '$')) AS attr
WHERE
  raw.Attributes IS NOT NULL
  AND raw.Attributes != '[]';-- Docs: https://docs.mage.ai/guides/sql-blocks

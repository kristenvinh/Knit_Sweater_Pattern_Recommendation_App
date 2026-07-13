CREATE OR REPLACE TABLE `knitwear-app.ravelry_data.bridge_pattern_attributes` AS
SELECT
  CAST(raw.ID AS INT64) AS pattern_id,
  attr AS pattern_attribute
FROM
  `knitwear-app.ravelry_data.detail_data` AS raw,
  UNNEST(raw.Attributes) AS attr
WHERE
  raw.Attributes IS NOT NULL;

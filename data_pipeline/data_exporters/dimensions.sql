CREATE OR REPLACE TABLE `knitwear-app-37e6574c4829.ravelry_data.dim_patterns` AS
SELECT
  CAST(ID AS INT64) AS pattern_id,
  Name AS pattern_name,
  Designer AS designer_name,
  URL AS ravelry_url,
  Craft AS craft_type,
  Pattern_Type AS pattern_type,
  Yarn_Weight AS yarn_weight,
  CAST(Gauge AS FLOAT64) AS gauge,
  Gauge_Divisor AS gauge_divisor,
  Gauge_Pattern AS gauge_pattern
FROM
  `knitwear-app-37e6574c4829.ravelry_data.final_pattern_attributes`
WHERE
  ID IS NOT NULL;-- Docs: https://docs.mage.ai/guides/sql-blocks

CREATE OR REPLACE TABLE `knitwear-app.ravelry_data.dim_patterns` AS
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
  Gauge_Pattern AS gauge_pattern,
  Notes AS notes,
  Projects_Count AS projects_count,
  Favorites_Count AS favorites_count
FROM
  `knitwear-app.ravelry_data.detail_data`
WHERE
  ID IS NOT NULL;-- Docs: https://docs.mage.ai/guides/sql-blocks

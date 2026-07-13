CREATE OR REPLACE TABLE `knitwear-app.ravelry_data.dim_pattern_photos` AS
SELECT
  CAST(raw.ID AS INT64) AS pattern_id,
  photo_obj.medium2_url AS photo_url,
  CAST(photo_obj.sort_order AS INT64) AS sort_order
FROM
  `knitwear-app.ravelry_data.detail_data` AS raw,
  UNNEST(raw.Photos) AS photo_obj
WHERE
  raw.Photos IS NOT NULL;

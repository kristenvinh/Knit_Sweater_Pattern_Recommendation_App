CREATE EXTERNAL TABLE `knitwear-app.ravelry_data.pattern_images`
WITH CONNECTION `knitwear-app.region.gcs_image_connection`
OPTIONS (
  object_metadata = 'SIMPLE',
  uris = ['gs://knitwear-pattern-images/*']
);-- Docs: https://docs.mage.ai/guides/sql-blocks

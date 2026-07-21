CREATE OR REPLACE TABLE `knitwear-app.ravelry_data.dim_text_embeddings` AS
SELECT 
  pattern_id,
  content AS original_text,
  ml_generate_embedding_result AS text_embedding
FROM ML.GENERATE_EMBEDDING(
  MODEL `knitwear-app.ravelry_data.pattern_text_embedder`,
  (
    -- We alias your enriched_description as "content" because the ML model requires that specific column name
    SELECT 
      ID AS pattern_id, 
      enriched_description AS content 
    FROM `knitwear-app.ravelry_data.v_enriched_pattern_descriptions`
  ),
  STRUCT(TRUE AS flatten_json_output)
);
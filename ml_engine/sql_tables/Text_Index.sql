CREATE VECTOR INDEX pattern_text_index 
ON `knitwear-app.ravelry_data.dim_text_embeddings`(text_embedding)
OPTIONS(
  index_type = 'IVF',
  distance_type = 'COSINE'
);
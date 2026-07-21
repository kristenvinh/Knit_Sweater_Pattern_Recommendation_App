CREATE VECTOR INDEX pattern_image_index 
ON `knitwear-app.ravelry_data.dim_pattern_image_embeddings`(image_embedding)
OPTIONS(
  index_type = 'IVF',
  distance_type = 'COSINE'
);
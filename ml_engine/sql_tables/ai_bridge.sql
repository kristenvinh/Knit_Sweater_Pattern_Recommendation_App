CREATE OR REPLACE MODEL `knitwear-app.ravelry_data.pattern_text_embedder`
REMOTE WITH CONNECTION `knitwear-app.us.vertex_ai_embedder` 
OPTIONS (ENDPOINT = 'text-embedding-004');
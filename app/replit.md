# Multimodal Knitwear Pattern Recommender

A Streamlit app that lets users find Ravelry knitting patterns by uploading a sweater photo, typing a text description, or blending both search modes.

## Stack

- **Frontend/UI**: Streamlit
- **ML model**: Meta DINOv2 (`facebook/dinov2-base`) for image embeddings
- **Database**: Google BigQuery (vector search on image + text embeddings)
- **Pattern data**: Ravelry API

## How to run

The app starts automatically via the **Start application** workflow:

```
streamlit run main.py --server.port 5000 --server.address 0.0.0.0
```

## Required secrets

Set these in Replit Secrets before running:

| Secret | Description |
|--------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Full contents of a Google Cloud service account JSON key (needs BigQuery access to `knitwear-app` project) |
| `RAVELRY_ACCESS_KEY` | Ravelry API access key |
| `RAVELRY_PERSONAL_KEY` | Ravelry personal API key |

## BigQuery resources

The app queries these tables in the `knitwear-app` GCP project:

- `knitwear-app.ravelry_data.dim_pattern_image_embeddings`
- `knitwear-app.ravelry_data.dim_text_embeddings`
- `knitwear-app.ravelry_data.pattern_text_embedder` (BQML embedding model)

import streamlit as st
import pandas as pd
import torch
import os
import json
import tempfile
import numpy as np
from numpy.linalg import norm
from PIL import Image
from transformers import AutoImageProcessor, AutoModel
from google.cloud import bigquery
from google.oauth2 import service_account

# Import the YOLO cropping function from your local file
from crop_images import extract_and_crop_image

# --- Page Config ---
st.set_page_config(page_title="Sweater Recommender", layout="wide")


# --- Service Credentials & Clients ---
@st.cache_resource
def init_clients():
    # 1. Initialize BigQuery Client securely from Replit Secrets
    if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
        creds_dict = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        bq_client = bigquery.Client(
            credentials=credentials, project=credentials.project_id
        )
    else:
        # Fallback if testing locally outside Replit
        bq_client = bigquery.Client(project="knitwear-app")

    # 2. Load Meta's DINOv3 Models
    LOCAL_MODEL_DIR = "./models/dinov3-vitb16"

    # Grab the token from the environment (will be None locally, populated in Replit)
    hf_token = os.environ.get("HF_TOKEN")
    # If hf_token exists, use it. Otherwise, pass True to use your local CLI login.
    auth_token = hf_token if hf_token else True

    # Use the DINOv3 model ID
    MODEL_ID = "facebook/dinov3-vitb16-pretrain-lvd1689m"

    if not os.path.isdir(LOCAL_MODEL_DIR) or not os.listdir(LOCAL_MODEL_DIR):
        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
        processor = AutoImageProcessor.from_pretrained(MODEL_ID, token=auth_token)
        model = AutoModel.from_pretrained(MODEL_ID, token=auth_token)
        processor.save_pretrained(LOCAL_MODEL_DIR)
        model.save_pretrained(LOCAL_MODEL_DIR)
    else:
        processor = AutoImageProcessor.from_pretrained(LOCAL_MODEL_DIR)
        model = AutoModel.from_pretrained(LOCAL_MODEL_DIR)

    return bq_client, processor, model


bq_client, img_processor, dino_model = init_clients()


# --- Helper Functions ---
def extract_image_vector(image_path: str) -> list[float]:
    """Crops via YOLO, passes through DINOv3, and normalizes the vector."""

    # 1. Execute YOLO Segmentation and Pose Cropping
    cropped_img_array = extract_and_crop_image(image_path)

    # 2. Process Image
    inputs = img_processor(images=cropped_img_array, return_tensors="pt")

    # 3. Extract Features
    with torch.no_grad():
        outputs = dino_model(**inputs)
        # Extract the CLS token and convert to numpy array
        feature_vector = outputs.last_hidden_state[:, 0].squeeze().cpu().numpy()

    # 4. Normalize the vector to match the database schema
    normalized_vector = feature_vector / norm(feature_vector)

    return normalized_vector.tolist()


def fetch_pattern_metadata(pattern_ids: list) -> dict:
    """Fetch Name, URL, and Photo for a list of pattern IDs from catalog_data."""
    if not pattern_ids:
        return {}
    ids_str = ", ".join(str(int(pid)) for pid in pattern_ids)
    sql = f"""
    SELECT ID, Name, URL, Photo
    FROM `knitwear-app.ravelry_data.catalog_data`
    WHERE ID IN ({ids_str})
    """
    try:
        rows = bq_client.query(sql).to_dataframe()
        # Key by int so lookups succeed regardless of whether pattern_id is int or float
        return {int(row.ID): row for _, row in rows.iterrows()}
    except Exception as e:
        print(f"catalog_data lookup error: {e}")
        return {}


def image_vector_search(query_image_vec, top_n=10):
    """Executes BigQuery vector search using the image embedding vector."""
    if not query_image_vec:
        return pd.DataFrame()

    img_sql = """
    SELECT base.pattern_id, distance AS image_distance
    FROM VECTOR_SEARCH(
      TABLE `knitwear-app.ravelry_data.dim_pattern_image_embeddings_Dino3_filtered`,
      'image_embedding',
      (SELECT @vec AS image_embedding),
      top_k => @top_k, distance_type => 'COSINE'
    );
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("vec", "FLOAT64", query_image_vec),
            bigquery.ScalarQueryParameter("top_k", "INT64", top_n),
        ]
    )
    return bq_client.query(img_sql, job_config=job_config).to_dataframe()


# --- UI Layout ---
st.title("Knitwear Pattern Recommender App")
st.write(
    "Upload a photo of a sweater to find visually similar knitting patterns from Ravelry."
)
st.write(
    "Photos that are well-lit, clear, and taken straight-on will yield the best recommendations."
)
st.write(
    "This app uses YOLO for sweater detection and Meta's DINOv3 model for image feature extraction, and pulls directly from Ravelry's pattern catalog for recommendations and does NOT generate patterns using AI."
)

uploaded_file = st.file_uploader("Upload a Sweater Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", width=250)

if st.button("Get Pattern Recommendations", type="primary"):
    if not uploaded_file:
        st.error("Please upload a photo first!")
    else:
        with st.spinner("Analyzing image and querying the database..."):
            # Save the uploaded file temporarily to disk for YOLO to read
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Extract feature vector
            img_vec = extract_image_vector(tmp_file_path)
            os.remove(tmp_file_path)

            # Fetch extra candidates so filtering out metadata-less patterns still yields 10
            results_df = image_vector_search(img_vec, top_n=20)

            if results_df.empty:
                st.warning("No matching recommendations were found.")
            else:
                st.subheader("Top 10 Visual Matches")

                # Deduplicate by pattern_id, keeping the closest match
                results_df = results_df.drop_duplicates(subset=["pattern_id"])

                # Fetch metadata for all candidates in one BigQuery call
                pattern_ids = [int(row.pattern_id) for row in results_df.itertuples()]
                metadata = fetch_pattern_metadata(pattern_ids)

                # Drop any result whose pattern_id has no entry in catalog_data,
                # then keep only the top 10 remaining (results are already ranked by distance)
                results_df = results_df[
                    results_df["pattern_id"].apply(lambda pid: int(pid) in metadata)
                ].head(10)

                # Build the dynamic grid layout
                cols = st.columns(5)
                for idx, row in enumerate(results_df.itertuples()):
                    info = metadata.get(int(row.pattern_id))
                    name = (
                        info.Name if info is not None else f"Pattern {row.pattern_id}"
                    )
                    url = info.URL if info is not None else "#"
                    photo = info.Photo if info is not None else None
                    with cols[idx % 5]:
                        if photo:
                            st.image(photo, width="stretch")
                        else:
                            st.image(
                                "https://placehold.co/300x300/e2e8f0/94a3b8?text=No+Image",
                                width="stretch",
                            )
                        st.markdown(f"**[{name}]({url})**")

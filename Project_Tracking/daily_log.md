# Daily Log for Knitwear Recommendation Application

## Week 1

### 7.13

- Had Gemini draft up project planning to take this from my original capstone project to one that uses BigQuery to store data and mage.ai to create a ETL workflow to upload data

- Had Gemini draft up a proposed project structure, ensuring I have better organization than on my previous project.

- Began ETL process using Mage.AI (code was already written in Jupyter Notebooks, used Gemini's help to refactor for use in Mage.AI ETL process):
    - Set up Mage.AI for ETL process using Docker. 
    - Created a data_loader for grabbing initial pattern data from Ravelry.
    - Created a data_exporter to export data to a BigQuery Table.
    - Created a second data_loader to grab pattern details from Ravelry patterns from first download.
    - Created a data_exporter to export the details to BigQuery Table.

### 7.14

- Set up Google Cloud Storage Bucket for images
- Created Python script to download images to the bucket
    - Downloaded images for 100 patterns
    - Created table in BigQuery to correspond to those images
    - Paused process to ensure billing seemed correct tomorrow

### 7.15
- Continued downloading images
- Further documented process in Readme file
- Updated repository file structure document

## Week 2

### 7.19
- Transferred files from original knitwear rec project for feature extraction, vector building and index building and began modifying for use with GCS

### 7.20
- Upgraded YOLO segmentation and pose models from nano to medium variants in hopes of improved accuracy.
- Change feature extraction to use DINOv2 CLS token (first token) instead of mean pooling in hopes of improved accuracy.
- Uploaded vectors to BigQuery.


### 7.21 
- Extracted pattern descriptions as "notes" in Python script in case it's helpful to use them later
- Organized files
- Built text modeling using Vertex AI:
    - Created a feature engineering query that concatenates structured metadata (pattern name, yarn weight, attributes) that would be fed to the LLM.
    - Connected BigQuery and Google's generation embedding model
    - Generated embeddings from the engineered features. 
- Build image vector ANN
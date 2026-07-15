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
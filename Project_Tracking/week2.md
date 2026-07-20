# WEEK 1 DEMO: Knit Sweater Pattern Recommendation Application

---

## What are you building?
I’m building the Knit Sweater Pattern Recommendation Application, which will allow a user to upload a photo they have of a sweater and then get recommendations of knitting patterns on Ravelry that are similar to it.

This idea grew out of searching the Internet on my own for sweater patterns similar to those I'd see in TV shows, movies, and designer websites. I then discovered on Reddit that many other people were asking for "Sweater Dupes" as well, so I decided to build the initial sweater pattern recommender for my capstone for my RIT MS Data Science degree. However, the original process was messy and was mostly based locally on my computer, so I decided I was going to revamp the project with three goals in mind:

1. Improve Data Storage by using BigQuery and Google Cloud Storage (GCS) Bucket
2. Improve sweater recommendation accuracy
3. Build a live, usable application 


### The Process:

1. Download Pattern Data use Mage.AI ETL process from Ravelry API and Store in BigQuery
    - Downloaded basic pattern data (Pattern name, ID, Designer, URL, Photo)
    - Downloaded pattern details (more images, gauge, pattern attributes, yarn weight, etc.)
    - Downloaded images via separate Python script to Google Cloud Storage
2. Create and Load Vectors to BigQuery
    - Crop images using YOLO to just the sweater image if possible
    - Extract features using DINOv2
    - Extract centroids to create a vector representing multiple images
    - Upload vectors to BigQuery

---

## What did you make progress on this week?

- Extracted features, created vectors from image centroids, uploaded those to BigQuery

---

## What challenges did you encounter?

- Accidentally terminated my feature extraction process; learned to put in a checkpoint process that prevents me from losing all my work. 

---

## What’s next?  
- See if there's a way to add new patterns to the database easily. 

### 

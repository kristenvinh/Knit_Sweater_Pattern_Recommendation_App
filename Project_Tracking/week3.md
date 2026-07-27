# WEEK 3 DEMO: Knit Sweater Pattern Recommendation Application

---

## What are you building?
I’m building the Knit Sweater Pattern Recommendation Application, which will allow a user to upload a photo they have of a sweater and then get recommendations of knitting patterns on Ravelry that are similar to it.

This idea grew out of searching the Internet on my own for sweater patterns similar to those I'd see in TV shows, movies, and designer websites. I then discovered on Reddit that many other people were asking for "Sweater Dupes" as well, so I decided to build the initial sweater pattern recommender for my capstone for my RIT MS Data Science degree. However, the original process was messy and was mostly based locally on my computer, so I decided I was going to revamp the project with three goals in mind:

1. Improve Data Storage by using BigQuery and Google Cloud Storage (GCS) Bucket
2. Improve sweater recommendation accuracy via improved models and text search addition
3. Build a live, usable application 


### The Process:

1. Download Pattern Data use Mage.AI ETL process from Ravelry API and Store in BigQuery
    - Downloaded basic pattern data (Pattern name, ID, Designer, URL, Photo)
    - Downloaded pattern details (more images, gauge, pattern attributes, yarn weight, etc.)
    - Downloaded images via separate Python script to Google Cloud Storage
2. Create and Load Image Vectors to BigQuery
    - Crop images using YOLO to just the sweater image if possible
    - Extract features using DINOv2
    - Extract centroids to create a vectors representing multiple images
    - Upload vectors to BigQuery
3. Create and Load Text Vectors to BigQuery
    - Feature-engineered a text description with pattern name, pattern notes, attributes, and yarn weight.
    - Used Vertex AI to convert these descriptions to vectors for search
4. Used Replit and Gemini to create an app that finds the nearest vectors to an image uploaded by a user and text entered by the user, weighted equally. 



---

## What did you make progress on this week?

-
---

## What challenges did you encounter?



---

## What’s next?  

### 

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

---

## What did you make progress on this week?

- Completed step one of the process, downloading images and Ravelry pattern details.

---

## What challenges did you encounter?

- Downloading pattern details and images were taking a long time, so downscaled to 5,000 patterns total, might upscale later

---

## What’s next?  
- Revamp my original feature extraction pipeline so that it works with the BigQuery database and images stored on Google Cloud Storage.

### 

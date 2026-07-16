# Knit Sweater Pattern Recommendation Application
I’m building the Knit Sweater Pattern Recommendation, which will allow a user to upload a photo they have of a sweater and then get recommendations of knitting patterns on Ravelry that are similar to it.

This idea grew out of searching the Internet on my own for sweater patterns similar to those I'd see in TV shows, movies, and designer websites. I then discovered on Reddit that many other people were asking for "Sweater Dupes" as well, so I decided to build the initial sweater pattern recommender for my capstone for my RIT MS Data Science degree. However, the original process was messy and was mostly based locally on my computer, so I decided I was going to revamp the project with three goals in mind:

1. Improve Data Storage by using BigQuery and Google Cloud Storage (GCS) Bucket
2. Improve sweater recommendation accuracy
3. Build a live, usable application 

## Step One: Acquire Data via Ravelry

### Mage.AI ETL Process

This process downloads a list of patterns via the Ravelry API, uploads the list of patterns to Ravelry, downloads those pattern attributes from Ravelry, then uploads the attributes to BigQuery.

It also transforms the data in three specific ways:

- Creates a table called 'bridge_pattern_attributes' which unnests the list of attributes associated with patterns, creating a dedicated row for each attribute and the pattern its associated with.
- Creates a table called 'dim_patterns' that builds the primary look-up table for the catalog of sweater patterns.
- Creates a table called 'dim_pattern_photos'  which unnests the medium2_urls from the photo object for each pattern and stores them as their own row, while creating a column for sort order to maintain the order in which they were listed in the original Ravelry listing. 

![Image of Tree Structure for Mage.AI Pipeline](mageaitree.png)
### Image Downloading Process

The last step in acquiring data from Ravelry was to download images and upload them to Google Cloud Storage in the image_downloading.py file, downloading no more than 5 images for each pattern and storing them by pattern_ID. 
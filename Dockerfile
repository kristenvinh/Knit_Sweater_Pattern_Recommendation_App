# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ingestion script and local modules (like crop_images.py)
COPY . /app/

# Set the command to run your ingestion script
CMD ["python", "ingest_daily_patterns.py"]
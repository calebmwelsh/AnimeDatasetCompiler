FROM python:3.10-slim

WORKDIR /app

# Install dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY main.py fetch_data.py upload_data.py /app/
COPY /data/kaggle/kaggle_dataset_metadata.json /app/data/kaggle/kaggle_dataset_metadata.json
COPY /data/kaggle/kaggle_dataset_description.md /app/data/kaggle/kaggle_dataset_description.md

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/kaggle /root/.kaggle

# Install Python dependencies directly
RUN pip install --no-cache-dir pandas requests tqdm openpyxl kaggle

# Set permissions for Kaggle credentials (will be mounted at runtime)
RUN chmod -R 777 /root/.kaggle

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the script
ENTRYPOINT ["python", "main.py"]

# Default arguments (can be overridden at runtime)
CMD []

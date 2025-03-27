FROM python:3.10-slim AS builder

WORKDIR /app

# Install only the essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies directly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pandas requests tqdm openpyxl kaggle

# Second stage: runtime image
FROM python:3.10-slim

WORKDIR /app

# Copy only the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/kaggle /root/.kaggle

# Copy application files
COPY AnimeDatasetCollector/main.py AnimeDatasetCollector/fetch_data.py AnimeDatasetCollector/upload_data.py ./
COPY AnimeDatasetCollector/data/kaggle/kaggle_dataset_metadata.json ./data/kaggle/
COPY AnimeDatasetCollector/data/kaggle/kaggle_dataset_description.md ./data/kaggle/

# Set proper secure permissions for Kaggle credentials (will be mounted at runtime)
RUN chmod -R 600 /root/.kaggle

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Chicago

# Create a simple wrapper script that can be called by Ofelia
RUN echo '#!/bin/bash\n\
/opt/venv/bin/python /app/main.py "$@"' > /app/run.sh && \
chmod +x /app/run.sh

# Use a passive entrypoint that keeps the container running
ENTRYPOINT ["tail", "-f", "/dev/null"]

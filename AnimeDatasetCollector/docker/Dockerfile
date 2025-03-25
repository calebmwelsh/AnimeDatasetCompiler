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

# Install cron for scheduling
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Create cron job to run the script every Sunday at 2am CST
RUN echo "0 2 * * 0 cd /app && python main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/anime_collector_cron && \
    chmod 0644 /etc/cron.d/anime_collector_cron && \
    crontab /etc/cron.d/anime_collector_cron

# Create a startup script that starts cron and then runs the command
RUN echo '#!/bin/bash\n\
service cron start\n\
echo "Cron service started. Script will run every Sunday at 2am CST."\n\
exec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Chicago

# Use our custom entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to run the script immediately and then keep container running
CMD ["python", "main.py"]

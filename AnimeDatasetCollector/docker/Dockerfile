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

# Install Python dependencies with minimal extras
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Second stage: runtime image
FROM python:3.10-slim

WORKDIR /app

# Copy only the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/kaggle /root/.kaggle

# Copy application files
COPY main.py fetch_data.py upload_data.py ./
COPY data/kaggle/kaggle_dataset_metadata.json ./data/kaggle/
COPY data/kaggle/kaggle_dataset_description.md ./data/kaggle/

# Set permissions for Kaggle credentials (will be mounted at runtime)
RUN chmod -R 777 /root/.kaggle

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the script
ENTRYPOINT ["python", "main.py"]

# Default arguments (can be overridden at runtime)
CMD []

# Docker Setup for AniList Anime Dataset Collector

This document provides instructions for running the AniList Anime Dataset Collector using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- Kaggle API credentials (kaggle.json file)

## Getting Started

### 1. Kaggle API Setup

Before running the container, you need to set up your Kaggle API credentials:

1. Log in to your Kaggle account
2. Go to your account settings (https://www.kaggle.com/settings)
3. Scroll down to the "API" section and click "Create New API Token"
4. This will download a `kaggle.json` file containing your API credentials
5. Place this file in one of these locations:
   - `~/.kaggle/kaggle.json` (Linux/Mac)
   - `C:\Users\<Windows-username>\.kaggle\kaggle.json` (Windows)
   - Or any location, and specify the path using the `KAGGLE_JSON_PATH` environment variable

### 2. Building and Running the Container

#### Option 1: Using Docker Compose (Recommended)

1. Make sure you're in the directory containing the `docker-compose.yml` file
2. Build and run the container:

```bash
# Build the container
docker-compose build

# Run the container in detached mode
docker-compose up -d

# Check logs
docker-compose logs
```

#### Option 2: Using Docker Directly

1. Build the Docker image:

```bash
docker build -t anilist-data-collector .
```

2. Run the container:

```bash
docker run -d \
    -v ~/.kaggle/kaggle.json:/root/.kaggle/kaggle.json:ro \
    -e TZ=America/Chicago \
    --restart unless-stopped \
    anilist-data-collector
```

## Command Line Options

The container accepts the same command-line arguments as the `main.py` script:

- `--test`: Run data fetching in test mode (limited data)
- `--skip-fetch`: Skip data fetching step (use existing data files)
- `--skip-upload`: Skip Kaggle upload step

Examples:

```bash
# Run in test mode
docker-compose run --rm anilist-data-collector python main.py --test

# Skip data fetching, only upload existing data
docker-compose run --rm anilist-data-collector python main.py --skip-fetch

# Skip Kaggle upload, only fetch data
docker-compose run --rm anilist-data-collector python main.py --skip-upload
```

## Scheduled Execution

The container is configured to run the script automatically every Sunday at 2:00 AM CST using cron.

### Customizing the Cron Schedule

To change the schedule when the script runs:

1. Edit the Dockerfile:

```dockerfile
# Find this line:
RUN echo "0 2 * * 0 cd /app && python main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/anime_collector_cron && \
```

2. Modify the cron expression `0 2 * * 0`:
   - `0` - Minute (0-59)
   - `2` - Hour (0-23)
   - `*` - Day of month (1-31)
   - `*` - Month (1-12)
   - `0` - Day of week (0-6, where 0 is Sunday)

Examples:
- `0 2 * * 0` - Every Sunday at 2:00 AM
- `0 4 * * 1` - Every Monday at 4:00 AM
- `0 0 1 * *` - First day of every month at midnight
- `0 12 * * 1-5` - Every weekday at noon

3. Rebuild the container:

```bash
docker-compose build
docker-compose up -d
```

### Checking Cron Logs

To verify the cron job is running properly:

```bash
# View cron logs
docker-compose exec anilist-data-collector cat /var/log/cron.log

# Follow cron logs in real-time
docker-compose exec anilist-data-collector tail -f /var/log/cron.log
```

## Troubleshooting

### Kaggle API Authentication Issues

If you encounter authentication issues with the Kaggle API:

1. Verify that your `kaggle.json` file contains valid credentials
2. Check that the file permissions are set correctly (600 on Linux/Mac)
3. Ensure the file is mounted correctly in the container

### Container Fails to Start

If the container fails to start:

1. Check Docker logs:

```bash
docker-compose logs anilist-data-collector
```

2. Verify that all required files are present in the project directory
3. Ensure you have sufficient disk space for the data collection

### Cron Job Not Running

If the scheduled cron job isn't running:

1. Check if cron service is running:

```bash
docker-compose exec anilist-data-collector service cron status
```

2. Check cron logs:

```bash
docker-compose exec anilist-data-collector grep CRON /var/log/syslog
```

3. Verify the timezone is set correctly:

```bash
docker-compose exec anilist-data-collector date
```

## Docker Image Size Optimization

The Docker image has been optimized to minimize size while maintaining full functionality:

1. Uses multi-stage builds to separate build and runtime environments
2. Installs only essential build dependencies
3. Uses Python virtual environment to manage dependencies
4. Removes unnecessary build artifacts and cache files

These optimizations significantly reduce the Docker image size compared to the previous version.

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

# Run the container with default settings
docker-compose run anilist-data-collector

# Or run with specific options
docker-compose run anilist-data-collector --test
```

#### Option 2: Using Docker Directly

1. Build the Docker image:

```bash
docker build -t anilist-data-collector .
```

2. Run the container:

```bash
docker run -v ~/.kaggle/kaggle.json:/root/.kaggle/kaggle.json:ro \
           -v ./data:/app/data \
           -e TZ=America/Chicago \
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
docker-compose run anilist-data-collector --test

# Skip data fetching, only upload existing data
docker-compose run anilist-data-collector --skip-fetch

# Skip Kaggle upload, only fetch data
docker-compose run anilist-data-collector --skip-upload
```

## Scheduling Container Runs

Since the container doesn't include internal scheduling, you can use your host system's scheduler to run the container at specific times:

### Linux/Mac (using cron)

1. Edit your crontab:

```bash
crontab -e
```

2. Add a line to run the container every Sunday at 2:00 AM CST:

```
0 2 * * 0 cd /path/to/project && docker-compose run --rm anilist-data-collector > /path/to/logfile.log 2>&1
```

### Windows (using Task Scheduler)

1. Create a batch file (e.g., `run_anilist_collector.bat`) with the following content:

```batch
cd /d C:\path\to\project
docker-compose run --rm anilist-data-collector
```

2. Open Task Scheduler and create a new task:
   - Trigger: Weekly, Sundays at 2:00 AM
   - Action: Start a program
   - Program/script: Path to your batch file

## Data Output

After running the container, the collected data will be available in the `./data` directory, which is mounted as a volume in the container.

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

## Updating the Dataset

To update the dataset with the latest anime information:

1. Run the container with the default settings:

```bash
docker-compose run anilist-data-collector
```

This will fetch the latest data from AniList and upload it to Kaggle, creating a new version of the dataset.

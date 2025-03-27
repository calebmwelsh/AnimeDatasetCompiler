# Docker Setup for AniList Anime Dataset Collector with Ofelia Scheduler

This document provides instructions for running the AniList Anime Dataset Collector using Docker with Ofelia for scheduling.

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

### 2. Setting Up Ofelia Scheduler

#### What is Ofelia?

Ofelia is a Docker job scheduler that can run commands, scripts, or Docker containers on a schedule. It's designed specifically for Docker environments and avoids the limitations of using cron inside containers.

#### Creating the Docker Compose File

Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'

services:
  anilist-data-collector:
    image: kdidtech/anilist-data-collector:latest
    container_name: anilist-data-collector
    volumes:
      # Mount kaggle.json credentials file
      - ~/.kaggle/kaggle.json:/root/.kaggle/kaggle.json:ro
      # Optional: Mount a local directory to persist data between runs
      - ./anime_data:/app/data
    environment:
      # Set timezone to CST (America/Chicago)
      - TZ=America/Chicago
    # Container will be managed by Ofelia scheduler
    restart: "no"
    
  scheduler:
    image: mcuadros/ofelia:latest
    container_name: anime-scheduler
    command: daemon --docker
    depends_on:
      - anilist-data-collector
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped
    labels:
      # Schedule the job to run every Sunday at 2am CST
      ofelia.job-exec.anime-job.schedule: "0 2 * * 0"
      ofelia.job-exec.anime-job.command: "/opt/venv/bin/python /app/main.py"
      ofelia.job-exec.anime-job.container: "anilist-data-collector"
      # Optional: Run the job immediately when the scheduler starts
      ofelia.job-run.initial-run.schedule: "@every 10s"
      ofelia.job-run.initial-run.command: "anilist-data-collector"
      ofelia.job-run.initial-run.run-once: "true"
```

#### Starting the Services

Run the following command to start both the data collector and scheduler containers:

```bash
docker-compose up -d
```

This will:
- Start the Ofelia scheduler container
- Configure it to run the anime data collector every Sunday at 2:00 AM CST
- Optionally run the data collector once immediately after startup

### 3. Understanding Ofelia Configuration

#### Job Types

Ofelia supports different job types. In our configuration, we use:

1. **job-exec**: Executes a command inside an existing container
   ```
   ofelia.job-exec.anime-job.schedule: "0 2 * * 0"
   ofelia.job-exec.anime-job.command: "/opt/venv/bin/python /app/main.py"
   ofelia.job-exec.anime-job.container: "anilist-data-collector"
   ```

2. **job-run**: Runs a container (starts and stops it)
   ```
   ofelia.job-run.initial-run.schedule: "@every 10s"
   ofelia.job-run.initial-run.command: "anilist-data-collector"
   ofelia.job-run.initial-run.run-once: "true"
   ```

#### Schedule Syntax

Ofelia uses standard cron syntax for scheduling:

- `0 2 * * 0` - Every Sunday at 2:00 AM
- `0 4 * * 1` - Every Monday at 4:00 AM
- `0 0 1 * *` - First day of every month at midnight
- `0 12 * * 1-5` - Every weekday at noon

Ofelia also supports interval notation:
- `@every 1h30m` - Every 1 hour and 30 minutes
- `@every 1h` - Every hour
- `@daily` - Once a day

### 4. Customizing the Configuration

#### Changing the Schedule

To change when the job runs, modify the `ofelia.job-exec.anime-job.schedule` label in the docker-compose.yml file.

#### Controlling Initial Execution

The configuration includes an optional initial run that executes once when the services start. To disable this, remove or comment out these three lines:

```yaml
# Optional: Run the job immediately when the scheduler starts
ofelia.job-run.initial-run.schedule: "@every 10s"
ofelia.job-run.initial-run.command: "anilist-data-collector"
ofelia.job-run.initial-run.run-once: "true"
```

#### Passing Command-Line Arguments

To pass command-line arguments to the script, modify the command in the job-exec label:

```yaml
# Run in test mode
ofelia.job-exec.anime-job.command: "/opt/venv/bin/python /app/main.py --test"

# Skip data fetching
ofelia.job-exec.anime-job.command: "/opt/venv/bin/python /app/main.py --skip-fetch"

# Skip Kaggle upload
ofelia.job-exec.anime-job.command: "/opt/venv/bin/python /app/main.py --skip-upload"
```

### 5. Monitoring and Logs

#### Viewing Ofelia Logs

To see the scheduler logs and job execution status:

```bash
docker logs anime-scheduler
```

#### Viewing Data Collector Logs

To see the logs from the data collector when it runs:

```bash
docker logs anilist-data-collector
```

#### Checking Job Status

Ofelia provides a simple HTTP API to check job status. By default, it listens on port 8080:

```bash
# Add this to the scheduler service in docker-compose.yml
ports:
  - "8080:8080"
```

Then access http://localhost:8080/jobs to see the status of all jobs.

## Troubleshooting

### Ofelia Not Running Jobs

If Ofelia is not running the scheduled jobs:

1. Check if Ofelia has access to the Docker socket:
   ```bash
   docker exec -it anime-scheduler ls -la /var/run/docker.sock
   ```

2. Verify the container names match exactly:
   ```bash
   docker ps
   ```

3. Check Ofelia logs for errors:
   ```bash
   docker logs anime-scheduler
   ```

### Data Collector Failing

If the data collector job fails:

1. Run the container manually to see the error:
   ```bash
   docker run --rm \
       -v ~/.kaggle/kaggle.json:/root/.kaggle/kaggle.json:ro \
       kdidtech/anilist-data-collector:latest
   ```

2. Check if the Kaggle credentials are mounted correctly:
   ```bash
   docker exec -it anilist-data-collector ls -la /root/.kaggle
   ```

3. Verify the data directory permissions:
   ```bash
   docker exec -it anilist-data-collector ls -la /app/data
   ```

## Advanced Configuration

### Using Environment Variables

You can pass environment variables to the data collector:

```yaml
anilist-data-collector:
  image: kdidtech/anilist-data-collector:latest
  container_name: anilist-data-collector
  volumes:
    - ~/.kaggle/kaggle.json:/root/.kaggle/kaggle.json:ro
  environment:
    - TZ=America/Chicago
    - LOG_LEVEL=DEBUG
```

### Multiple Scheduled Jobs

You can configure multiple jobs with different schedules:

```yaml
labels:
  # Weekly full run
  ofelia.job-exec.weekly-job.schedule: "0 2 * * 0"
  ofelia.job-exec.weekly-job.command: "/opt/venv/bin/python /app/main.py"
  ofelia.job-exec.weekly-job.container: "anilist-data-collector"
  
  # Daily test run
  ofelia.job-exec.daily-test.schedule: "0 4 * * *"
  ofelia.job-exec.daily-test.command: "/opt/venv/bin/python /app/main.py --test"
  ofelia.job-exec.daily-test.container: "anilist-data-collector"
```

### Email Notifications

Ofelia supports email notifications for job execution:

```yaml
scheduler:
  image: mcuadros/ofelia:latest
  command: daemon --docker
  environment:
    - OFELIA_SMTP_HOST=smtp.example.com
    - OFELIA_SMTP_PORT=587
    - OFELIA_SMTP_USER=user
    - OFELIA_SMTP_PASSWORD=password
    - OFELIA_SMTP_FROM=ofelia@example.com
  labels:
    ofelia.job-exec.anime-job.schedule: "0 2 * * 0"
    ofelia.job-exec.anime-job.command: "/opt/venv/bin/python /app/main.py"
    ofelia.job-exec.anime-job.container: "anilist-data-collector"
    ofelia.job-exec.anime-job.email-on-error: "admin@example.com"
```

## Comparison with Other Scheduling Methods

### Advantages of Ofelia over Cron in Containers

1. **Designed for Docker**: Ofelia is specifically designed to work with Docker containers
2. **No PATH issues**: Avoids the common PATH and environment variable issues with cron
3. **Better logging**: Provides detailed logs of job execution
4. **Job monitoring**: Includes a simple HTTP API for monitoring job status
5. **Multiple job types**: Supports executing commands in containers or running containers
6. **Flexible scheduling**: Supports both cron syntax and interval notation

### Advantages of Ofelia over Host Cron

1. **Self-contained**: Everything runs within Docker, no need to set up host cron
2. **Portable**: Works the same across different operating systems
3. **Better integration**: Direct access to Docker containers without shell scripts
4. **Centralized management**: All scheduling configuration is in the docker-compose.yml file
5. **Built-in monitoring**: Includes job status monitoring capabilities
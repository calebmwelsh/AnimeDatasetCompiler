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
    restart: unless-stopped
    
  scheduler:
    image: mcuadros/ofelia:latest
    container_name: anime-data-collection-scheduler
    command: daemon --docker
    depends_on:
      - anilist-data-collector
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      # Set the same timezone as the data collector
      - TZ=America/Chicago
    restart: unless-stopped
    labels:
      # Schedule the job to run every Sunday at 2am CST
      # Ofelia uses 6-field cron format: seconds minutes hours day-of-month month day-of-week
      ofelia.job-exec.anime-data-collection-job.schedule: "0 0 2 * * 0"
      ofelia.job-exec.anime-data-collection-job.command: "/opt/venv/bin/python /app/main.py"
      ofelia.job-exec.anime-data-collection-job.container: "anilist-data-collector"
```

#### Starting the Services

Run the following command to start both the data collector and scheduler containers:

```bash
docker-compose up -d
```

This will:
- Start the Ofelia scheduler container
- Configure it to run the anime data collector every Sunday at 2:00 AM CST

### 3. Understanding Ofelia Configuration

#### Job Types

Ofelia supports different job types. In our configuration, we use:

1. **job-exec**: Executes a command inside an existing container
   ```
   ofelia.job-exec.anime-data-collection-job.schedule: "0 0 2 * * 0"
   ofelia.job-exec.anime-data-collection-job.command: "/opt/venv/bin/python /app/main.py"
   ofelia.job-exec.anime-data-collection-job.container: "anilist-data-collector"
   ```

#### Schedule Syntax

Ofelia uses a 6-field cron syntax for scheduling, which includes seconds:

```
seconds minutes hours day-of-month month day-of-week
```

Examples:
- `0 0 2 * * 0` - Every Sunday at 2:00:00 AM (0 seconds, 0 minutes, 2 hours, any day of month, any month, Sunday)
- `0 0 4 * * 1` - Every Monday at 4:00:00 AM
- `0 0 0 1 * *` - First day of every month at midnight
- `0 0 12 * * 1-5` - Every weekday at noon

Ofelia also supports interval notation:
- `@every 1h30m` - Every 1 hour and 30 minutes
- `@every 1h` - Every hour
- `@daily` - Once a day

### 4. Customizing the Configuration

#### Changing the Schedule

To change when the job runs, modify the `ofelia.job-exec.anime-data-collection-job.schedule` label in the docker-compose.yml file, remembering to use the 6-field format.

#### Passing Command-Line Arguments

To pass command-line arguments to the script, modify the command in the job-exec label:

```yaml
# Run in test mode
ofelia.job-exec.anime-data-collection-job.command: "/opt/venv/bin/python /app/main.py --test"

# Skip data fetching
ofelia.job-exec.anime-data-collection-job.command: "/opt/venv/bin/python /app/main.py --skip-fetch"

# Skip Kaggle upload
ofelia.job-exec.anime-data-collection-job.command: "/opt/venv/bin/python /app/main.py --skip-upload"
```

### 5. Monitoring and Logs

#### Viewing Ofelia Logs

To see the scheduler logs and job execution status:

```bash
docker logs anime-data-collection-scheduler
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
   docker exec -it anime-data-collection-scheduler ls -la /var/run/docker.sock
   ```

2. Verify the container names match exactly:
   ```bash
   docker ps
   ```

3. Check Ofelia logs for errors:
   ```bash
   docker logs anime-data-collection-scheduler
   ```

4. Verify the cron format is correct (remember Ofelia uses 6 fields):
   ```
   seconds minutes hours day-of-month month day-of-week
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
  ofelia.job-exec.weekly-job.schedule: "0 0 2 * * 0"
  ofelia.job-exec.weekly-job.command: "/opt/venv/bin/python /app/main.py"
  ofelia.job-exec.weekly-job.container: "anilist-data-collector"
  
  # Daily test run
  ofelia.job-exec.daily-test.schedule: "0 0 4 * * *"
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
    ofelia.job-exec.anime-data-collection-job.schedule: "0 0 2 * * 0"
    ofelia.job-exec.anime-data-collection-job.command: "/opt/venv/bin/python /app/main.py"
    ofelia.job-exec.anime-data-collection-job.container: "anilist-data-collector"
    ofelia.job-exec.anime-data-collection-job.email-on-error: "admin@example.com"
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

# AniList Anime Dataset Collector

This project fetches comprehensive anime data from AniList using their GraphQL API and uploads it to Kaggle as a dataset. It collects all available attributes for each anime title, including basic information, statistics, characters, staff, studios, and more.

## Project Structure

- `main.py`: Main script that orchestrates the data collection and upload workflow
- `fetch_data.py`: Script that fetches anime data from AniList GraphQL API
- `upload_data.py`: Script that uploads the dataset to Kaggle
- `data/kaggle/kaggle_dataset_metadata.json`: Metadata for the Kaggle dataset
- `data/kaggle/kaggle_dataset_description.md`: Detailed description of the dataset

For a detailed overview of the directory structure, see [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md).

## Features

- Fetches all anime data from AniList using their GraphQL API
- Overcomes the 5,000 anime limitation by using year-based filtering
- Properly handles FuzzyDateInt format used by AniList
- Creates a comprehensive dataset with all available attributes
- Exports data in multiple formats (CSV, Excel, Pickle)
- Uploads the dataset to Kaggle with proper metadata and description

## Requirements

- Python 3.6+
- Kaggle API credentials
- Required Python packages:
  - pandas
  - requests
  - tqdm
  - openpyxl
  - kaggle

## Docker Support

This project includes Docker support for easier deployment and execution. See the [Docker README](docker/docker-readme.md) for detailed instructions on:

- Building and running the container
- Setting up Kaggle API credentials
- Command-line options
- Scheduling container runs
- Troubleshooting common issues

The Docker configuration automatically installs all required dependencies, so you don't need to worry about dependency management.

### Scheduled Execution with Docker

The Docker container is configured to run the script automatically every Sunday at 2:00 AM CST using cron.

#### Customizing the Cron Schedule

To change when the script runs:

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

Common examples:
- `0 2 * * 0` - Every Sunday at 2:00 AM
- `0 4 * * 1` - Every Monday at 4:00 AM
- `0 0 1 * *` - First day of every month at midnight

3. Rebuild and restart the container:

```bash
docker-compose build
docker-compose up -d
```

For more detailed instructions on cron customization and monitoring, see the [Docker README](docker/docker-readme.md).

## Usage

### Manual Execution

1. Clone this repository
2. Set up Kaggle API credentials (see below)
3. Install required dependencies: `pip install -r requirements.txt`
4. Run the main script:

```bash
python main.py
```

### Command Line Options

The main script accepts the following command-line arguments:

- `--test`: Run data fetching in test mode (limited data)
- `--skip-fetch`: Skip data fetching step (use existing data files)
- `--skip-upload`: Skip Kaggle upload step

Examples:

```bash
# Run in test mode
python main.py --test

# Skip data fetching, only upload existing data
python main.py --skip-fetch

# Skip Kaggle upload, only fetch data
python main.py --skip-upload
```

## Kaggle API Setup

Before running the script, you need to set up your Kaggle API credentials:

1. Log in to your Kaggle account
2. Go to your account settings (https://www.kaggle.com/settings)
3. Scroll down to the "API" section and click "Create New API Token"
4. This will download a `kaggle.json` file containing your API credentials
5. Place this file in one of these locations:
   - `~/.kaggle/kaggle.json` (Linux/Mac)
   - `C:\Users\<Windows-username>\.kaggle\kaggle.json` (Windows)

## Dataset Output

After running the script, the following files will be created:

- `data/raw/anilist_anime_data_complete.csv`: Complete anime dataset in CSV format
- `data/raw/anilist_anime_data_complete.xlsx`: Complete anime dataset in Excel format
- `data/raw/anilist_anime_data_complete.pkl`: Complete anime dataset in Python pickle format

These files will also be uploaded to Kaggle as a dataset.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [AniList](https://anilist.co) for providing the GraphQL API
- [Kaggle](https://kaggle.com) for hosting the dataset

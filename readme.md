# AniList Anime Dataset Collector

This project fetches comprehensive anime data from AniList using their GraphQL API and uploads it to Kaggle as a dataset. It collects all available attributes for each anime title, including basic information, statistics, characters, staff, studios, and more.

## Project Structure

- `main.py`: Main script that orchestrates the data collection and upload workflow
- `fetch_data.py`: Script that fetches anime data from AniList GraphQL API
- `upload_data.py`: Script that uploads the dataset to Kaggle
- `data/kaggle/kaggle_dataset_metadata.json`: Metadata for the Kaggle dataset
- `data/kaggle/kaggle_dataset_description.md`: Detailed description of the dataset

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

This project now includes Docker support for easier deployment and execution. See the [Docker README](DOCKER_README.md) for detailed instructions on:

- Building and running the container
- Setting up Kaggle API credentials
- Command-line options
- Scheduling container runs using your host system's scheduler (cron/Task Scheduler)
- Troubleshooting common issues

The Docker configuration automatically installs all required dependencies, so you don't need to worry about dependency management.

## Usage

### Manual Execution

1. Clone this repository
2. Set up Kaggle API credentials (see below)
3. Install required dependencies: `pip install pandas requests tqdm openpyxl kaggle`
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

- `anilist_anime_data_complete.csv`: Complete anime dataset in CSV format
- `anilist_anime_data_complete.xlsx`: Complete anime dataset in Excel format
- `anilist_anime_data_complete.pkl`: Complete anime dataset in Python pickle format

These files will also be uploaded to Kaggle as a dataset.

## Scheduling

For automated data collection, you can now use Docker with your system's scheduler:

- **Linux/Mac**: Use cron to schedule the Docker container to run weekly
- **Windows**: Use Task Scheduler to run the Docker container weekly

See the [Docker README](DOCKER_README.md) for detailed scheduling instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [AniList](https://anilist.co) for providing the GraphQL API
- [Kaggle](https://kaggle.com) for hosting the dataset

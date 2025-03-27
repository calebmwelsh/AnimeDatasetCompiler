# AniList Anime Dataset Collector

This project fetches comprehensive anime data from AniList using their GraphQL API and uploads it to Kaggle as a dataset. It collects all available attributes for each anime title, including basic information, statistics, characters, staff, studios, and more.

## Features

- **Comprehensive Data Collection**: Fetches all anime data from AniList using their GraphQL API
- **API Limitation Workaround**: Overcomes the 5,000 anime limitation by using year-based filtering
- **Data Format Handling**: Properly handles FuzzyDateInt format used by AniList
- **Complete Attribute Set**: Creates a comprehensive dataset with all available attributes
- **Multiple Export Formats**: Exports data in multiple formats (CSV, Excel, Pickle)
- **Automated Kaggle Upload**: Uploads the dataset to Kaggle with proper metadata and description
- **Scheduled Updates**: Supports scheduled execution to keep the dataset up-to-date
- **Docker Support**: Includes Docker configuration for easy deployment and execution

## Dataset Contents

The collected dataset includes the following information for each anime:

- **Basic Information**: ID, title, format, episodes, duration, status, season, year
- **Content Details**: genres, tags, description, source material, rating, content warnings
- **Statistics**: popularity, favorites, average score, trending rank
- **Related Entities**: characters, staff, studios, producers
- **External Links**: official site, streaming platforms, social media
- **Dates**: start date, end date, next airing episode

## Project Structure

- `main.py`: Main script that orchestrates the data collection and upload workflow
- `fetch_data.py`: Script that fetches anime data from AniList GraphQL API
- `upload_data.py`: Script that uploads the dataset to Kaggle
- `data/kaggle/kaggle_dataset_metadata.json`: Metadata for the Kaggle dataset
- `data/kaggle/kaggle_dataset_description.md`: Detailed description of the dataset

For a detailed overview of the directory structure, see [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md).

## Requirements

- Python 3.6+
- Kaggle API credentials
- Required Python packages:
  - pandas
  - requests
  - tqdm
  - openpyxl
  - kaggle

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

## Docker Support

This project includes Docker support for easier deployment and scheduled execution. The Docker configuration:

- Automatically installs all required dependencies
- Supports scheduled execution using Ofelia scheduler
- Provides options for data persistence between runs
- Includes proper timezone handling for scheduled jobs

For detailed Docker setup instructions, including:
- Running the container from Docker Hub
- Setting up scheduled execution with Ofelia
- Customizing the execution schedule
- Troubleshooting common issues

See the [Docker README](docker-readme.md) for complete documentation.

Basic Docker usage:

```bash
# Pull the image
docker pull kdidtech/anilist-data-collector:latest

# Run with Kaggle credentials
docker run --rm \
    -v ~/.kaggle/kaggle.json:/root/.kaggle/kaggle.json:ro \
    kdidtech/anilist-data-collector:latest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [AniList](https://anilist.co) for providing the GraphQL API
- [Kaggle](https://kaggle.com) for hosting the dataset

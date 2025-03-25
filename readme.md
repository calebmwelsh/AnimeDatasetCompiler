# AniList Anime Dataset Creator

A comprehensive solution for creating and maintaining a complete dataset of all anime from AniList.co using their GraphQL API, with options to upload the dataset to Kaggle.

## Overview

This project provides tools to:

1. **Fetch anime data** from AniList using their GraphQL API
2. **Create a structured dataset** with all available anime attributes
3. **Upload the dataset to Kaggle** for sharing and analysis
4. **Run the entire workflow** with a single command

The resulting dataset includes approximately 21,000 anime titles with comprehensive information about each title, including basic details, statistics, characters, staff, studios, and more.

## Components

This project consists of several components:

- **`fetch_data.py`**: Fetches anime data from AniList and creates the dataset
- **`upload_data.py`**: Uploads the dataset to Kaggle
- **`main.py`**: Combines both scripts into a single workflow
- **`data/kaggle/kaggle_dataset_metadata.json`**: Metadata for the Kaggle dataset
- **`data/kaggle/kaggle_dataset_description.md`**: Detailed description of the dataset columns
- **`data/kaggle/kaggle.json`**: Kaggle API credentials

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - pandas
  - requests
  - tqdm
  - openpyxl (for Excel export)
  - kaggle (for Kaggle upload)

### Install Dependencies

```bash
pip install pandas requests tqdm openpyxl kaggle
```

### Kaggle API Setup

To use the Kaggle upload functionality:

1. Create a Kaggle account if you don't have one
2. Go to https://www.kaggle.com/account
3. Scroll down to the "API" section and click "Create New API Token"
4. This will download a `kaggle.json` file with your credentials
5. You have three options for placing your credentials:
   - **Project-specific location**: Place at `data/kaggle/kaggle.json` in your project directory
   - **Standard location (Linux/Mac)**: Place at `~/.kaggle/kaggle.json`
   - **Standard location (Windows)**: Place at `C:\Users\<Windows-username>\.kaggle\kaggle.json`

The script will check these locations in order and use the first one it finds.

## Usage

### Fetching Anime Data

To fetch all anime data from AniList:

```bash
python fetch_data.py
```

Options:
- `--test`: Run in test mode (fetches a limited dataset for testing)

This will create three output files:
- `anilist_anime_data_complete.csv`: CSV format
- `anilist_anime_data_complete.xlsx`: Excel format
- `anilist_anime_data_complete.pkl`: Python pickle format

### Uploading to Kaggle

To upload the dataset to Kaggle:

```bash
python upload_data.py
```

The script will automatically:
- Look for Kaggle credentials in the standard locations or at `data/kaggle/kaggle.json`
- Look for metadata files in the `data/kaggle/` directory:
  - `data/kaggle/kaggle_dataset_metadata.json`
  - `data/kaggle/kaggle_dataset_description.md`

Options:
- `--kaggle-json PATH`: Path to your Kaggle credentials file (if not in standard locations)
- `--metadata PATH`: Custom path to metadata file (default: `data/kaggle/kaggle_dataset_metadata.json`)
- `--description PATH`: Custom path to description file (default: `data/kaggle/kaggle_dataset_description.md`)
- `--new-version`: Create a new version if the dataset already exists

### Complete Workflow

To run the entire process (fetch data and upload to Kaggle):

```bash
python main.py
```

Options:
- **Data Fetching Options:**
  - `--test`: Run data fetching in test mode (limited data)
  - `--skip-fetch`: Skip the data fetching step (use existing data files)

- **Kaggle Upload Options:**
  - `--kaggle-json PATH`: Path to your kaggle.json credentials file (if not in standard locations)
  - `--new-version`: Create a new version if the dataset already exists
  - `--skip-upload`: Skip the Kaggle upload step

## Dataset Structure

The dataset includes a wide range of attributes for each anime:

- **Basic Information**: ID, titles, format, status, dates, episodes, etc.
- **Images**: Cover images, banner images
- **Trailer Information**: Trailer links and thumbnails
- **Tags and Genres**: Categorization and content tags
- **Statistics and Scores**: Popularity, ratings, rankings
- **Characters**: Character information and voice actors
- **Staff**: Production staff and roles
- **Studios**: Animation studios and production companies
- **Airing Information**: Episode schedules and next episodes
- **Recommendations and Reviews**: User recommendations and reviews

For a complete description of all columns, see `data/kaggle/kaggle_dataset_description.md`.

## Working with JSON Columns

Many columns contain JSON data (arrays or objects) to preserve the nested structure of the original API response. To work with these columns in Python:

```python
import pandas as pd
import json

# Load the dataset
df = pd.read_csv('anilist_anime_data_complete.csv')

# Parse a JSON column
df['genres_parsed'] = df['genres'].apply(json.loads)

# Example: Get the first genre for each anime
df['first_genre'] = df['genres_parsed'].apply(lambda x: x[0] if len(x) > 0 else None)
```

## Overcoming API Limitations

The AniList API has a limitation of returning only 5,000 anime entries (100 pages with 50 entries each). This project overcomes this limitation by using year-based filtering to fetch anime in batches:

- Recent years (last 10 years): Fetched individually
- Previous decade: Fetched in 2-year ranges
- Earlier decades: Fetched in 5-year ranges
- Oldest anime: Fetched in a single large range

This approach allows the script to retrieve all ~21,000 anime from AniList.

## Example Use Cases

The resulting dataset can be used for:

1. **Anime Recommendation Systems**: Build recommendation algorithms based on genres, tags, and scores
2. **Trend Analysis**: Analyze popularity and score trends over time or by season
3. **Network Analysis**: Study relationships between studios, staff, and anime productions
4. **Content Analysis**: Examine the distribution of genres, themes, and content types
5. **Seasonal Analysis**: Investigate patterns in anime releases by season and year

## Troubleshooting

### Common Issues

- **API Rate Limiting**: The script includes built-in handling for rate limits, but if you encounter persistent rate limiting, try running with longer intervals between requests
- **Missing Kaggle Credentials**: Ensure your `kaggle.json` file is properly formatted and located in one of the supported locations:
  - Standard location: `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<Windows-username>\.kaggle\kaggle.json` (Windows)
  - Project location: `data/kaggle/kaggle.json`
- **Missing Metadata Files**: Ensure the metadata files exist at:
  - `data/kaggle/kaggle_dataset_metadata.json`
  - `data/kaggle/kaggle_dataset_description.md`
- **File Not Found Errors**: Make sure all script files are in the same directory or provide full paths to files

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Verify your Kaggle credentials are correct
3. Run scripts with the `--test` flag to verify basic functionality

## License

This project is released under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [AniList](https://anilist.co) for providing the GraphQL API
- [Kaggle](https://www.kaggle.com) for hosting datasets

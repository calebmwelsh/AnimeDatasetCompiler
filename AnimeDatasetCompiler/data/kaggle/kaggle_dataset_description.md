# AniList Anime Dataset Description

This document provides a comprehensive description of the anime dataset created using the AniList GraphQL API. The dataset contains detailed information about anime titles available on AniList, including basic information, statistics, characters, staff, studios, and more.

## Dataset Overview

The dataset is created by querying the AniList GraphQL API and collecting all available anime attributes. The data is organized into a structured format with each row representing a unique anime title and columns representing various attributes.

## File Formats

The dataset is available in three formats:
- **CSV** (`anilist_anime_data_complete.csv`): Comma-separated values format, easily importable into most data analysis tools
- **Excel** (`anilist_anime_data_complete.xlsx`): Microsoft Excel format for easy viewing and filtering
- **Pickle** (`anilist_anime_data_complete.pkl`): Python pickle format for efficient loading in Python applications

## Column Descriptions
a
### Basic Information

| Column | Description |
|--------|-------------|
| `id` | Unique identifier for the anime on AniList |
| `idMal` | Unique identifier for the anime on MyAnimeList (if available) |
| `title_romaji` | The romanized title |
| `title_english` | The official English title |
| `title_native` | The title in its native language (usually Japanese) |
| `title_userPreferred` | The title in the user's preferred format |
| `type` | The type of media (ANIME) |
| `format` | The format of the anime (TV, MOVIE, OVA, ONA, SPECIAL, etc.) |
| `status` | Current status (FINISHED, RELEASING, NOT_YET_RELEASED, CANCELLED, HIATUS) |
| `description` | Synopsis or description of the anime |
| `startDate_year` | Year the anime started airing |
| `startDate_month` | Month the anime started airing |
| `startDate_day` | Day the anime started airing |
| `endDate_year` | Year the anime finished airing |
| `endDate_month` | Month the anime finished airing |
| `endDate_day` | Day the anime finished airing |
| `season` | Season the anime aired (WINTER, SPRING, SUMMER, FALL) |
| `seasonYear` | The year the anime aired in its season |
| `seasonInt` | Integer representation of the season |
| `episodes` | Number of episodes |
| `duration` | Average duration of episodes in minutes |
| `chapters` | Number of chapters in the source material (if applicable) |
| `volumes` | Number of volumes in the source material (if applicable) |
| `countryOfOrigin` | Country where the anime originated |
| `isLicensed` | Whether the anime is licensed for release in the US |
| `source` | Source material (MANGA, LIGHT_NOVEL, ORIGINAL, etc.) |
| `hashtag` | Official Twitter hashtag |
| `updatedAt` | Unix timestamp of when the entry was last updated |

### Images

| Column | Description |
|--------|-------------|
| `coverImage_extraLarge` | URL to the extra large cover image |
| `coverImage_large` | URL to the large cover image |
| `coverImage_medium` | URL to the medium cover image |
| `coverImage_color` | Dominant color of the cover image |
| `bannerImage` | URL to the banner image |

### Trailer Information

| Column | Description |
|--------|-------------|
| `trailer_id` | ID of the trailer |
| `trailer_site` | Site hosting the trailer (e.g., YouTube) |
| `trailer_thumbnail` | URL to the trailer thumbnail |

### Tags and Genres

| Column | Description |
|--------|-------------|
| `genres` | List of genres (JSON array) |
| `synonyms` | Alternative titles (JSON array) |
| `tags` | Detailed tags with descriptions and categories (JSON array) |

### Statistics and Scores

| Column | Description |
|--------|-------------|
| `averageScore` | Average score out of 100 |
| `meanScore` | Mean score out of 100 |
| `popularity` | Number of users with the anime on their list |
| `favourites` | Number of users who have favorited the anime |
| `trending` | Current trending rank |
| `rankings` | Various rankings (popularity, score, etc.) with context (JSON array) |

### Status Flags

| Column | Description |
|--------|-------------|
| `isFavourite` | Whether the authenticated user has marked this as a favorite |
| `isAdult` | Whether the anime is marked as adult content |
| `isLocked` | Whether the entry is locked for editing |

### External Information

| Column | Description |
|--------|-------------|
| `siteUrl` | URL to the anime page on AniList |
| `externalLinks` | Links to official sites, streaming platforms, etc. (JSON array) |
| `streamingEpisodes` | Information about streaming episodes (JSON array) |

### Related Media

| Column | Description |
|--------|-------------|
| `relations` | Related anime, manga, etc. with relationship type (JSON array) |

### Characters

| Column | Description |
|--------|-------------|
| `characters` | Character information including roles, names, and voice actors (JSON array) |

### Staff

| Column | Description |
|--------|-------------|
| `staff` | Staff information including roles and names (JSON array) |

### Studios

| Column | Description |
|--------|-------------|
| `studios` | Studio information including whether they are the main production studio (JSON array) |

### Airing Information

| Column | Description |
|--------|-------------|
| `nextAiringEpisode` | Information about the next airing episode (JSON object) |
| `airingSchedule` | Schedule of episode air dates (JSON array) |

### Recommendations and Reviews

| Column | Description |
|--------|-------------|
| `recommendations` | User recommendations for similar anime (JSON array) |
| `reviews` | User reviews with ratings and summaries (JSON array) |

### Statistics

| Column | Description |
|--------|-------------|
| `stats_scoreDistribution` | Distribution of user scores (JSON array) |
| `stats_statusDistribution` | Distribution of user statuses (watching, completed, etc.) (JSON array) |

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

## Notes on Data Completeness

- Not all anime will have values for all columns (e.g., some may not have trailers or external links)
- Some attributes may be null or empty depending on the completeness of the data on AniList
- The dataset includes all anime available on AniList at the time of collection, which should be approximately 21,000 titles

## Example Usage Scenarios

1. **Anime Recommendation Systems**: Use genres, tags, and scores to build recommendation algorithms
2. **Trend Analysis**: Analyze popularity and score trends over time or by season
3. **Network Analysis**: Study relationships between studios, staff, and anime productions
4. **Content Analysis**: Examine the distribution of genres, themes, and content types
5. **Seasonal Analysis**: Investigate patterns in anime releases by season and year

## Data Update Frequency

This dataset represents a snapshot of the AniList database at the time of collection. To get the most current data, you can re-run the script to generate a fresh dataset.

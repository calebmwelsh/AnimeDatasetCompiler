"""
AniList Anime Data Scraper 

This script fetches all anime data from AniList using their GraphQL API
and creates a pandas DataFrame with all available attributes.

This version overcomes the 5,000 anime limitation by using year-based
filtering to retrieve all anime in batches, with proper FuzzyDateInt handling.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('fetch_data')

# AniList GraphQL API endpoint
ANILIST_API = "https://graphql.anilist.co"

# GraphQL query to fetch anime data with all attributes
QUERY = """
query ($page: Int, $perPage: Int, $startDate: FuzzyDateInt, $endDate: FuzzyDateInt) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    media(type: ANIME, startDate_greater: $startDate, startDate_lesser: $endDate) {
      # Basic Info
      id
      idMal
      title {
        romaji
        english
        native
        userPreferred
      }
      type
      format
      status
      description
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      season
      seasonYear
      seasonInt
      episodes
      duration
      chapters
      volumes
      countryOfOrigin
      isLicensed
      source
      hashtag
      trailer {
        id
        site
        thumbnail
      }
      updatedAt
      coverImage {
        extraLarge
        large
        medium
        color
      }
      bannerImage
      
      # Tags and Genres
      genres
      synonyms
      tags {
        id
        name
        description
        category
        rank
        isGeneralSpoiler
        isMediaSpoiler
        isAdult
      }
      
      # Stats and Scores
      averageScore
      meanScore
      popularity
      favourites
      trending
      rankings {
        id
        rank
        type
        format
        year
        season
        allTime
        context
      }
      
      # Status Flags
      isFavourite
      isAdult
      isLocked
      
      # External Info
      siteUrl
      externalLinks {
        id
        url
        site
        type
        language
        color
        icon
        notes
        isDisabled
      }
      streamingEpisodes {
        title
        thumbnail
        url
        site
      }
      
      # Related Media
      relations {
        edges {
          id
          relationType
          node {
            id
            title {
              romaji
              english
              native
            }
            type
            format
            status
          }
        }
      }
      
      # Characters
      characters {
        edges {
          id
          role
          name
          voiceActors {
            id
            name {
              full
              native
            }
            languageV2
            image {
              large
              medium
            }
          }
          node {
            id
            name {
              full
              native
              alternative
            }
            image {
              large
              medium
            }
            description
          }
        }
      }
      
      # Staff
      staff {
        edges {
          id
          role
          node {
            id
            name {
              full
              native
            }
            languageV2
            image {
              large
              medium
            }
          }
        }
      }
      
      # Studios
      studios {
        edges {
          id
          isMain
          node {
            id
            name
            isAnimationStudio
          }
        }
      }
      
      # Airing Info
      nextAiringEpisode {
        id
        airingAt
        timeUntilAiring
        episode
        mediaId
      }
      airingSchedule {
        nodes {
          id
          airingAt
          timeUntilAiring
          episode
          mediaId
        }
      }
      
      # Recommendations
      recommendations {
        edges {
          node {
            id
            rating
            mediaRecommendation {
              id
              title {
                romaji
                english
                native
              }
            }
          }
        }
      }
      
      # Reviews
      reviews {
        edges {
          node {
            id
            summary
            rating
            score
          }
        }
      }
      
      # Stats
      stats {
        scoreDistribution {
          score
          amount
        }
        statusDistribution {
          status
          amount
        }
      }
    }
  }
}
"""

def convert_to_fuzzy_date(year, month=1, day=1):
    """
    Convert year, month, day to FuzzyDateInt format required by AniList API
    
    FuzzyDateInt format: YYYYMMDD as integer
    
    Args:
        year (int): Year
        month (int, optional): Month (1-12). Defaults to 1.
        day (int, optional): Day (1-31). Defaults to 1.
        
    Returns:
        int: Date in FuzzyDateInt format
    """
    return year * 10000 + month * 100 + day

def fetch_anime_page(page, per_page=50, start_year=None, end_year=None):
    """
    Fetch a single page of anime data from AniList GraphQL API
    
    Args:
        page (int): Page number to fetch
        per_page (int): Number of items per page
        start_year (int): Start year for filtering (inclusive)
        end_year (int): End year for filtering (inclusive)
        
    Returns:
        dict: JSON response from AniList API
    """
    # Convert years to FuzzyDateInt format
    start_date = convert_to_fuzzy_date(start_year, 1, 1) if start_year else None
    end_date = convert_to_fuzzy_date(end_year, 12, 31) if end_year else None
    
    variables = {
        'page': page,
        'perPage': per_page,
        'startDate': start_date,
        'endDate': end_date
    }
    
    payload = {
        'query': QUERY,
        'variables': variables
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    
    try:
        response = requests.post(ANILIST_API, json=payload, headers=headers)
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited. Waiting for {retry_after} seconds...")
            time.sleep(retry_after)
            return fetch_anime_page(page, per_page, start_year, end_year)
        
        # Handle other errors
        if response.status_code != 200:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            return None
        
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching anime page: {str(e)}")
        return None

def flatten_anime_data(anime):
    """
    Flatten nested anime data into a dictionary suitable for pandas DataFrame
    
    Args:
        anime (dict): Anime data from AniList API
        
    Returns:
        dict: Flattened anime data
    """
    flattened = {}
    
    # Basic Info
    flattened['id'] = anime.get('id')
    flattened['idMal'] = anime.get('idMal')
    
    # Title
    title = anime.get('title', {})
    flattened['title_romaji'] = title.get('romaji')
    flattened['title_english'] = title.get('english')
    flattened['title_native'] = title.get('native')
    flattened['title_userPreferred'] = title.get('userPreferred')
    
    # Basic attributes
    flattened['type'] = anime.get('type')
    flattened['format'] = anime.get('format')
    flattened['status'] = anime.get('status')
    flattened['description'] = anime.get('description')
    
    # Dates
    start_date = anime.get('startDate', {})
    flattened['startDate_year'] = start_date.get('year')
    flattened['startDate_month'] = start_date.get('month')
    flattened['startDate_day'] = start_date.get('day')
    
    end_date = anime.get('endDate', {})
    flattened['endDate_year'] = end_date.get('year')
    flattened['endDate_month'] = end_date.get('month')
    flattened['endDate_day'] = end_date.get('day')
    
    # Season info
    flattened['season'] = anime.get('season')
    flattened['seasonYear'] = anime.get('seasonYear')
    flattened['seasonInt'] = anime.get('seasonInt')
    
    # Episode info
    flattened['episodes'] = anime.get('episodes')
    flattened['duration'] = anime.get('duration')
    flattened['chapters'] = anime.get('chapters')
    flattened['volumes'] = anime.get('volumes')
    
    # Origin and source
    flattened['countryOfOrigin'] = anime.get('countryOfOrigin')
    flattened['isLicensed'] = anime.get('isLicensed')
    flattened['source'] = anime.get('source')
    flattened['hashtag'] = anime.get('hashtag')
    
    # Trailer - Fix for NoneType error
    trailer = anime.get('trailer') or {}  # Use empty dict if trailer is None
    flattened['trailer_id'] = trailer.get('id')
    flattened['trailer_site'] = trailer.get('site')
    flattened['trailer_thumbnail'] = trailer.get('thumbnail')
    
    # Updated timestamp
    flattened['updatedAt'] = anime.get('updatedAt')
    
    # Images
    cover_image = anime.get('coverImage', {})
    flattened['coverImage_extraLarge'] = cover_image.get('extraLarge')
    flattened['coverImage_large'] = cover_image.get('large')
    flattened['coverImage_medium'] = cover_image.get('medium')
    flattened['coverImage_color'] = cover_image.get('color')
    flattened['bannerImage'] = anime.get('bannerImage')
    
    # Tags and genres
    flattened['genres'] = json.dumps(anime.get('genres', []))
    flattened['synonyms'] = json.dumps(anime.get('synonyms', []))
    
    # Convert tags to JSON
    tags = anime.get('tags', [])
    flattened['tags'] = json.dumps(tags)
    
    # Stats and scores
    flattened['averageScore'] = anime.get('averageScore')
    flattened['meanScore'] = anime.get('meanScore')
    flattened['popularity'] = anime.get('popularity')
    flattened['favourites'] = anime.get('favourites')
    flattened['trending'] = anime.get('trending')
    
    # Rankings
    rankings = anime.get('rankings', [])
    flattened['rankings'] = json.dumps(rankings)
    
    # Status flags
    flattened['isFavourite'] = anime.get('isFavourite')
    flattened['isAdult'] = anime.get('isAdult')
    flattened['isLocked'] = anime.get('isLocked')
    
    # External info
    flattened['siteUrl'] = anime.get('siteUrl')
    
    # External links
    external_links = anime.get('externalLinks', [])
    flattened['externalLinks'] = json.dumps(external_links)
    
    # Streaming episodes
    streaming_episodes = anime.get('streamingEpisodes', [])
    flattened['streamingEpisodes'] = json.dumps(streaming_episodes)
    
    # Relations
    relations = anime.get('relations', {}).get('edges', [])
    flattened['relations'] = json.dumps(relations)
    
    # Characters
    characters = anime.get('characters', {}).get('edges', [])
    flattened['characters'] = json.dumps(characters)
    
    # Staff
    staff = anime.get('staff', {}).get('edges', [])
    flattened['staff'] = json.dumps(staff)
    
    # Studios
    studios = anime.get('studios', {}).get('edges', [])
    flattened['studios'] = json.dumps(studios)
    
    # Airing info
    next_airing_episode = anime.get('nextAiringEpisode', {})
    flattened['nextAiringEpisode'] = json.dumps(next_airing_episode) if next_airing_episode else None
    
    airing_schedule = anime.get('airingSchedule', {}).get('nodes', [])
    flattened['airingSchedule'] = json.dumps(airing_schedule)
    
    # Recommendations
    recommendations = anime.get('recommendations', {}).get('edges', [])
    flattened['recommendations'] = json.dumps(recommendations)
    
    # Reviews
    reviews = anime.get('reviews', {}).get('edges', [])
    flattened['reviews'] = json.dumps(reviews)
    
    # Stats
    stats = anime.get('stats', {})
    score_distribution = stats.get('scoreDistribution', [])
    status_distribution = stats.get('statusDistribution', [])
    flattened['stats_scoreDistribution'] = json.dumps(score_distribution)
    flattened['stats_statusDistribution'] = json.dumps(status_distribution)
    
    return flattened

def fetch_all_anime(test_mode=False):
    """
    Fetch all anime from AniList API using year-based filtering to overcome the 5,000 item limitation
    
    Args:
        test_mode (bool): Whether to run in test mode (limited data)
        
    Returns:
        pandas.DataFrame: DataFrame containing all anime data
    """
    # Define year ranges to fetch anime in batches
    # This helps overcome the 5,000 item limitation of the AniList API
    if test_mode:
        # In test mode, just fetch a small sample
        year_ranges = [(2020, 2020)]
        logger.info("Running in TEST MODE - only fetching anime from 2020")
    else:
        # Define year ranges to fetch anime in batches
        # Adjust these ranges based on the number of anime in each period
        # Earlier years can have wider ranges as there are fewer anime
        year_ranges = [
            (1940, 1965),  # Very early anime (few entries)
            (1966, 1970), (1971, 1975), (1976, 1980),  # Older anime
            (1981, 1985), (1986, 1990), (1991, 1995), (1996, 2000),  # Classic anime
            (2001, 2005), (2006, 2007), (2008, 2009),  # More anime per year
            (2010, 2011), (2012, 2013), (2014, 2015),  # Modern anime (many entries)
            (2016, 2016), (2017, 2017), (2018, 2018),  # Recent anime (many entries per year)
            (2019, 2019), (2020, 2020), (2021, 2021),  # Very recent anime
            (2022, 2022), (2023, 2023), (2024, 2024),  # Current anime
            (2025, 2025)  # Upcoming anime
        ]
    
    all_anime = []
    
    # Create temp directory for batch files
    temp_dir = Path("temp_anime_data")
    temp_dir.mkdir(exist_ok=True)
    
    # Fetch anime for each year range
    for start_year, end_year in year_ranges:
        logger.info(f"Fetching anime from {start_year} to {end_year}...")
        
        anime_batch = []
        page = 1
        has_next_page = True
        
        # Fetch all pages for this year range
        with tqdm(desc=f"{start_year}-{end_year}", unit="page") as pbar:
            while has_next_page:
                # Fetch a page of anime
                response = fetch_anime_page(page, per_page=50, start_year=start_year, end_year=end_year)
                
                if not response or 'data' not in response:
                    logger.error(f"Failed to fetch page {page} for years {start_year}-{end_year}")
                    break
                
                # Extract anime data from response
                page_info = response['data']['Page']['pageInfo']
                media_list = response['data']['Page']['media']
                
                # Process each anime in this page
                for anime in media_list:
                    # Flatten nested data for easier DataFrame creation
                    flattened_anime = flatten_anime_data(anime)
                    anime_batch.append(flattened_anime)
                
                # Update progress
                pbar.update(1)
                pbar.set_postfix({"anime": len(anime_batch), "page": page})
                
                # Check if there are more pages
                has_next_page = page_info['hasNextPage']
                page += 1
                
                # In test mode, only fetch a few pages
                if test_mode and page > 2:
                    logger.info("Test mode: stopping after 2 pages")
                    break
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
        
        if anime_batch:
            # Save this batch to a temporary file
            batch_df = pd.DataFrame(anime_batch)
            temp_file = os.path.join(temp_dir, f"anime_{start_year}_{end_year}.pkl")
            batch_df.to_pickle(temp_file)
            logger.info(f"Saved {len(anime_batch)} anime to {temp_file}")
            
            all_anime.extend(anime_batch)
    
    # Create DataFrame from all collected anime
    df = pd.DataFrame(all_anime)
    
    # Remove duplicates based on id
    if not df.empty:
        df = df.drop_duplicates(subset=['id'])
        logger.info(f"After removing duplicates: {len(df)} unique anime entries")
    
    return df

def main():
    """Main function to fetch all anime and save to CSV"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AniList Anime Data Scraper')
    parser.add_argument('--test', action='store_true', help='Run in test mode (fetch only a few pages)')
    args = parser.parse_args()
    
    logger.info("Starting AniList anime data scraper...")
    
    # Fetch all anime data
    df = fetch_all_anime(test_mode=args.test)
    
    if df.empty:
        logger.error("Failed to fetch anime data")
        return
      
    # Create data dir
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    if not raw_dir.exists():
        raw_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {raw_dir}")
    else:
        logger.info(f"Directory already exists: {raw_dir}")
        
    # Save to CSV
    csv_filename = raw_dir / "anilist_anime_data_complete.csv"
    df.to_csv(csv_filename, index=True)
    logger.info(f"Saved {len(df)} anime records to {csv_filename}")
    
    # Save to Excel (optional)
    try:
        excel_filename = raw_dir / "anilist_anime_data_complete.xlsx"
        df.to_excel(excel_filename, index=True)
        logger.info(f"Saved {len(df)} anime records to {excel_filename}")
    except Exception as e:
        logger.error(f"Warning: Could not save to Excel format: {e}")
    
    # Save to pickle for easier reloading (optional)
    pickle_filename = raw_dir / "anilist_anime_data_complete.pkl"
    df.to_pickle(pickle_filename)
    logger.info(f"Saved {len(df)} anime records to {pickle_filename}")
    
    logger.info("Done!")

if __name__ == "__main__":
    main()

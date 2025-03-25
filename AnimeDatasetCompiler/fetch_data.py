"""
AniList Anime Data Scraper 

This script fetches all anime data from AniList using their GraphQL API
and creates a pandas DataFrame with all available attributes.

This version overcomes the 5,000 anime limitation by using year-based
filtering to retrieve all anime in batches, with proper FuzzyDateInt handling.
"""

import argparse
import json
import os
import time
from datetime import datetime

import pandas as pd
import requests
from tqdm import tqdm

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
    
    response = requests.post(ANILIST_API, json=payload, headers=headers)
    
    # Handle rate limiting
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited. Waiting for {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_anime_page(page, per_page, start_year, end_year)
    
    # Handle other errors
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

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
    
    # Episodes and duration
    flattened['episodes'] = anime.get('episodes')
    flattened['duration'] = anime.get('duration')
    flattened['chapters'] = anime.get('chapters')
    flattened['volumes'] = anime.get('volumes')
    
    # Origin and licensing
    flattened['countryOfOrigin'] = anime.get('countryOfOrigin')
    flattened['isLicensed'] = anime.get('isLicensed')
    flattened['source'] = anime.get('source')
    flattened['hashtag'] = anime.get('hashtag')
    
    # Trailer
    trailer = anime.get('trailer', {})
    flattened['trailer_id'] = trailer.get('id') if trailer else None
    flattened['trailer_site'] = trailer.get('site') if trailer else None
    flattened['trailer_thumbnail'] = trailer.get('thumbnail') if trailer else None
    
    # Updated timestamp
    flattened['updatedAt'] = anime.get('updatedAt')
    
    # Images
    cover_image = anime.get('coverImage', {})
    flattened['coverImage_extraLarge'] = cover_image.get('extraLarge')
    flattened['coverImage_large'] = cover_image.get('large')
    flattened['coverImage_medium'] = cover_image.get('medium')
    flattened['coverImage_color'] = cover_image.get('color')
    flattened['bannerImage'] = anime.get('bannerImage')
    
    # Tags and Genres
    flattened['genres'] = json.dumps(anime.get('genres', []))
    flattened['synonyms'] = json.dumps(anime.get('synonyms', []))
    
    # Convert tags to JSON string
    tags = anime.get('tags', [])
    flattened['tags'] = json.dumps([{
        'id': tag.get('id'),
        'name': tag.get('name'),
        'description': tag.get('description'),
        'category': tag.get('category'),
        'rank': tag.get('rank'),
        'isGeneralSpoiler': tag.get('isGeneralSpoiler'),
        'isMediaSpoiler': tag.get('isMediaSpoiler'),
        'isAdult': tag.get('isAdult')
    } for tag in tags])
    
    # Stats and Scores
    flattened['averageScore'] = anime.get('averageScore')
    flattened['meanScore'] = anime.get('meanScore')
    flattened['popularity'] = anime.get('popularity')
    flattened['favourites'] = anime.get('favourites')
    flattened['trending'] = anime.get('trending')
    
    # Rankings
    rankings = anime.get('rankings', [])
    flattened['rankings'] = json.dumps([{
        'id': rank.get('id'),
        'rank': rank.get('rank'),
        'type': rank.get('type'),
        'format': rank.get('format'),
        'year': rank.get('year'),
        'season': rank.get('season'),
        'allTime': rank.get('allTime'),
        'context': rank.get('context')
    } for rank in rankings])
    
    # Status Flags
    flattened['isFavourite'] = anime.get('isFavourite')
    flattened['isAdult'] = anime.get('isAdult')
    flattened['isLocked'] = anime.get('isLocked')
    
    # External Info
    flattened['siteUrl'] = anime.get('siteUrl')
    
    # External Links
    external_links = anime.get('externalLinks', [])
    flattened['externalLinks'] = json.dumps([{
        'id': link.get('id'),
        'url': link.get('url'),
        'site': link.get('site'),
        'type': link.get('type'),
        'language': link.get('language'),
        'color': link.get('color'),
        'icon': link.get('icon'),
        'notes': link.get('notes'),
        'isDisabled': link.get('isDisabled')
    } for link in external_links])
    
    # Streaming Episodes
    streaming_episodes = anime.get('streamingEpisodes', [])
    flattened['streamingEpisodes'] = json.dumps([{
        'title': ep.get('title'),
        'thumbnail': ep.get('thumbnail'),
        'url': ep.get('url'),
        'site': ep.get('site')
    } for ep in streaming_episodes])
    
    # Related Media
    relations = anime.get('relations', {}).get('edges', [])
    flattened['relations'] = json.dumps([{
        'id': rel.get('id'),
        'relationType': rel.get('relationType'),
        'node': {
            'id': rel.get('node', {}).get('id'),
            'title': rel.get('node', {}).get('title'),
            'type': rel.get('node', {}).get('type'),
            'format': rel.get('node', {}).get('format'),
            'status': rel.get('node', {}).get('status')
        }
    } for rel in relations])
    
    # Characters
    characters = anime.get('characters', {}).get('edges', [])
    flattened['characters'] = json.dumps([{
        'id': char.get('id'),
        'role': char.get('role'),
        'name': char.get('name'),
        'voiceActors': char.get('voiceActors'),
        'node': {
            'id': char.get('node', {}).get('id'),
            'name': char.get('node', {}).get('name'),
            'image': char.get('node', {}).get('image'),
            'description': char.get('node', {}).get('description')
        }
    } for char in characters])
    
    # Staff
    staff = anime.get('staff', {}).get('edges', [])
    flattened['staff'] = json.dumps([{
        'id': s.get('id'),
        'role': s.get('role'),
        'node': {
            'id': s.get('node', {}).get('id'),
            'name': s.get('node', {}).get('name'),
            'languageV2': s.get('node', {}).get('languageV2'),
            'image': s.get('node', {}).get('image')
        }
    } for s in staff])
    
    # Studios
    studios = anime.get('studios', {}).get('edges', [])
    flattened['studios'] = json.dumps([{
        'id': studio.get('id'),
        'isMain': studio.get('isMain'),
        'node': {
            'id': studio.get('node', {}).get('id'),
            'name': studio.get('node', {}).get('name'),
            'isAnimationStudio': studio.get('node', {}).get('isAnimationStudio')
        }
    } for studio in studios])
    
    # Airing Info
    next_airing = anime.get('nextAiringEpisode', {})
    flattened['nextAiringEpisode'] = json.dumps(next_airing) if next_airing else None
    
    airing_schedule = anime.get('airingSchedule', {}).get('nodes', [])
    flattened['airingSchedule'] = json.dumps(airing_schedule)
    
    # Recommendations
    recommendations = anime.get('recommendations', {}).get('edges', [])
    flattened['recommendations'] = json.dumps([{
        'node': {
            'id': rec.get('node', {}).get('id'),
            'rating': rec.get('node', {}).get('rating'),
            'mediaRecommendation': rec.get('node', {}).get('mediaRecommendation')
        }
    } for rec in recommendations])
    
    # Reviews
    reviews = anime.get('reviews', {}).get('edges', [])
    flattened['reviews'] = json.dumps([{
        'node': {
            'id': rev.get('node', {}).get('id'),
            'summary': rev.get('node', {}).get('summary'),
            'rating': rev.get('node', {}).get('rating'),
            'score': rev.get('node', {}).get('score')
        }
    } for rev in reviews])
    
    # Stats
    stats = anime.get('stats', {})
    flattened['stats_scoreDistribution'] = json.dumps(stats.get('scoreDistribution', []))
    flattened['stats_statusDistribution'] = json.dumps(stats.get('statusDistribution', []))
    
    return flattened

def fetch_anime_by_year_range(start_year, end_year, test_mode=False):
    """
    Fetch anime data for a specific year range
    
    Args:
        start_year (int): Start year for filtering (inclusive)
        end_year (int): End year for filtering (inclusive)
        test_mode (bool): If True, only fetch a small sample of anime for testing
        
    Returns:
        list: List of flattened anime data dictionaries
    """
    all_anime = []
    page = 1
    per_page = 50  # Maximum allowed by AniList API
    
    # Get total count from first page
    first_page = fetch_anime_page(page, per_page, start_year, end_year)
    if not first_page or 'data' not in first_page:
        print(f"Failed to fetch first page for years {start_year}-{end_year}")
        return []
    
    total_pages = first_page['data']['Page']['pageInfo']['lastPage']
    total_anime = first_page['data']['Page']['pageInfo']['total']
    
    print(f"Found {total_anime} anime from {start_year} to {end_year} across {total_pages} pages")
    
    # Limit pages in test mode
    if test_mode:
        total_pages = min(2, total_pages)
        print(f"Test mode: Limiting to {total_pages} pages")
    
    # Process first page
    anime_list = first_page['data']['Page']['media']
    for anime in anime_list:
        all_anime.append(flatten_anime_data(anime))
    
    # Process remaining pages
    for page in tqdm(range(2, total_pages + 1), desc=f"Fetching anime ({start_year}-{end_year})"):
        response = fetch_anime_page(page, per_page, start_year, end_year)
        
        if not response or 'data' not in response:
            print(f"Failed to fetch page {page} for years {start_year}-{end_year}")
            continue
        
        anime_list = response['data']['Page']['media']
        for anime in anime_list:
            all_anime.append(flatten_anime_data(anime))
        
        # Respect rate limits - sleep between requests
        time.sleep(1)
    
    return all_anime

def fetch_all_anime(test_mode=False):
    """
    Fetch all anime data from AniList API using year-based filtering
    
    Args:
        test_mode (bool): If True, only fetch a small sample of anime for testing
        
    Returns:
        pandas.DataFrame: DataFrame containing all anime data
    """
    all_anime = []
    
    # Define year ranges to fetch
    # Anime history spans from ~1940s to present
    current_year = datetime.now().year
    
    # Create year ranges with smaller intervals for recent years (more anime)
    # and larger intervals for older years (fewer anime)
    year_ranges = []
    
    # Recent years (individual years)
    for year in range(current_year, current_year - 10, -1):
        year_ranges.append((year, year))
    
    # 2-year ranges for the decade before that
    for year in range(current_year - 10, current_year - 20, -2):
        year_ranges.append((year - 1, year))
    
    # 5-year ranges for earlier decades
    for year in range(current_year - 20, 1940, -5):
        year_ranges.append((year - 4, year))
    
    # Add the earliest range
    year_ranges.append((1900, current_year - 25))
    
    # Limit year ranges in test mode
    if test_mode:
        year_ranges = year_ranges[:3]  # Just use the 3 most recent ranges
        print(f"Test mode: Limiting to {len(year_ranges)} year ranges")
    
    # Create a directory for temporary files
    temp_dir = "temp_anime_data"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Fetch anime for each year range
    for i, (start_year, end_year) in enumerate(year_ranges):
        print(f"Processing year range {i+1}/{len(year_ranges)}: {start_year}-{end_year}")
        
        anime_batch = fetch_anime_by_year_range(start_year, end_year, test_mode)
        
        if anime_batch:
            # Save this batch to a temporary file
            batch_df = pd.DataFrame(anime_batch)
            temp_file = os.path.join(temp_dir, f"anime_{start_year}_{end_year}.pkl")
            batch_df.to_pickle(temp_file)
            print(f"Saved {len(anime_batch)} anime to {temp_file}")
            
            all_anime.extend(anime_batch)
    
    # Create DataFrame from all collected anime
    df = pd.DataFrame(all_anime)
    
    # Remove duplicates based on id
    if not df.empty:
        df = df.drop_duplicates(subset=['id'])
        print(f"After removing duplicates: {len(df)} unique anime entries")
    
    return df

def main():
    """Main function to fetch all anime and save to CSV"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AniList Anime Data Scraper')
    parser.add_argument('--test', action='store_true', help='Run in test mode (fetch only a few pages)')
    args = parser.parse_args()
    
    print("Starting AniList anime data scraper...")
    
    # Fetch all anime data
    df = fetch_all_anime(test_mode=args.test)
    
    if df.empty:
        print("Failed to fetch anime data")
        return
    
    # Save to CSV
    csv_filename = "anilist_anime_data_complete.csv"
    df.to_csv(csv_filename, index=True)
    print(f"Saved {len(df)} anime records to {csv_filename}")
    
    # Save to Excel (optional)
    try:
        excel_filename = "anilist_anime_data_complete.xlsx"
        df.to_excel(excel_filename, index=True)
        print(f"Saved {len(df)} anime records to {excel_filename}")
    except Exception as e:
        print(f"Warning: Could not save to Excel format: {e}")
    
    # Save to pickle for easier reloading (optional)
    pickle_filename = "anilist_anime_data_complete.pkl"
    df.to_pickle(pickle_filename)
    print(f"Saved {len(df)} anime records to {pickle_filename}")
    
    print("Done!")

main()

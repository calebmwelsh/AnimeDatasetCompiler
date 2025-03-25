"""
Kaggle Dataset Upload Script for AniList Anime Dataset

This script uploads the AniList anime dataset files to Kaggle using the Kaggle API.
It requires a valid Kaggle API token to be configured.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# Now import kaggle after credentials are set up
from kaggle.api.kaggle_api_extended import KaggleApi


# Ensure Kaggle credentials are properly set up before importing kaggle
def setup_kaggle_credentials(kaggle_json_path=None):
    """
    Set up Kaggle API credentials from a JSON file
    
    Args:
        kaggle_json_path (str, optional): Path to kaggle.json file with API credentials.
            If not provided, will look for credentials in the standard location:
            - Linux/Mac: ~/.kaggle/kaggle.json
            - Windows: C:\\Users\\<Windows-username>\\.kaggle\\kaggle.json
    
    Returns:
        bool: True if credentials were successfully set up, False otherwise
    """
    # Define standard Kaggle credential locations
    if os.name == 'nt':  # Windows
        standard_kaggle_dir = os.path.join(os.path.expanduser('~'), '.kaggle')
    else:  # Linux, Mac, etc.
        standard_kaggle_dir = os.path.join(os.path.expanduser('~'), '.kaggle')
    
    standard_kaggle_json = os.path.join(standard_kaggle_dir, 'kaggle.json')
    
    # Check if credentials already exist in the standard location
    if os.path.exists(standard_kaggle_json):
        print(f"Using existing Kaggle credentials at {standard_kaggle_json}")
        return True
    
    # If a specific path was provided, use that
    if kaggle_json_path:
        if not os.path.exists(kaggle_json_path):
            print(f"Error: Kaggle credentials not found at {kaggle_json_path}")
            return False
            
        source_path = kaggle_json_path
        print(f"Using Kaggle credentials from: {kaggle_json_path}")
    else:
        print("Error: Kaggle credentials not found.")
        print("Please provide a kaggle.json file with the correct credentials.")
        return False
    
    # Create the standard directory if it doesn't exist
    os.makedirs(standard_kaggle_dir, exist_ok=True)
    
    # Copy the credentials file to the standard location
    print(f"Copying Kaggle credentials from {source_path} to {standard_kaggle_json}")
    shutil.copy(source_path, standard_kaggle_json)
    
    # Set permissions to 600 (required by Kaggle API) - skip on Windows
    if os.name != 'nt':  # Skip on Windows
        os.chmod(standard_kaggle_json, 0o600)
    
    return True


def validate_files(files):
    """
    Validate that all required files exist
    
    Args:
        files (list): List of file paths to validate
    
    Returns:
        bool: True if all files exist, False otherwise
    """
    missing_files = []
    for file_path in files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Error: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def upload_dataset(metadata_path, description_path, dataset_dir):
    """
    Upload dataset to Kaggle
    
    Args:
        metadata_path (str): Path to dataset-metadata.json file
        dataset_dir (str): Directory containing the dataset files
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Initialize the Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # Load metadata to get dataset ID
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        dataset_id = metadata.get('id')
        if not dataset_id:
            print("Error: Dataset ID not found in metadata file")
            return False
        
    
        # Check if dataset already exists
        try:
            existing_dataset = api.dataset_list_files(dataset_id)
            dataset_exists = True
        except:
            dataset_exists = False
        
        # Create dataset folder structure
        os.makedirs(dataset_dir, exist_ok=True)
        
        metadata_dest = os.path.join(dataset_dir, 'dataset-metadata.json')

        # Load and inject dataset description into metadata
        with open(description_path, "r", encoding="utf-8") as desc_file:
            description_content = desc_file.read()

        metadata["description"] = description_content

        with open(metadata_dest, "w", encoding="utf-8") as meta_file:
            json.dump(metadata, meta_file, indent=2)

        if dataset_exists:
            print(f"Creating new version of existing dataset {dataset_id}")
            api.dataset_create_version(dataset_dir, version_notes="Updated dataset", quiet=False)
        else:
            print(f"Creating new dataset {dataset_id}")
            api.dataset_create_new(dataset_dir, quiet=False)
        
        print(f"Dataset successfully uploaded to Kaggle: https://www.kaggle.com/datasets/{dataset_id}")
        return True
    
    except Exception as e:
        print(f"Error uploading dataset to Kaggle: {str(e)}")
        return False

def main():
    """Main function to handle command line arguments and upload dataset"""
    parser = argparse.ArgumentParser(description='Upload AniList Anime Dataset to Kaggle')
    parser.add_argument('--metadata', default='data/kaggle/kaggle_dataset_metadata.json', 
                        help='Path to dataset metadata JSON file (default: data/kaggle/kaggle_dataset_metadata.json)')
    parser.add_argument('--csv', default='data/raw/anilist_anime_data_complete.csv',
                        help='Path to CSV dataset file (default: data/raw/anilist_anime_data_complete.csv)')
    parser.add_argument('--excel', default='data/raw/anilist_anime_data_complete.xlsx',
                        help='Path to Excel dataset file (default: data/raw/anilist_anime_data_complete.xlsx)')
    parser.add_argument('--pickle', default='data/raw/anilist_anime_data_complete.pkl',
                        help='Path to pickle dataset file (default: data/raw/anilist_anime_data_complete.pkl)')
    parser.add_argument('--fetch_data', default='fetch_data.py',
                        help='Path to python data fetching file (default: fetch_data.py)')
    parser.add_argument('--description', default='data/kaggle/kaggle_dataset_description.md',
                        help='Path to dataset description markdown file (default: data/kaggle/kaggle_dataset_description.md)')
    args = parser.parse_args()
    
    # Set up Kaggle credentials
    if not setup_kaggle_credentials():
        return 1
    
    # Validate that all required files exist
    required_files = [
        args.metadata,
        args.csv,
        args.excel,
        args.pickle,
        args.fetch_data,
        args.description
    ]
    
    if not validate_files(required_files):
        return 1
    
    # Create a temporary directory for the dataset
    dataset_dir = 'kaggle_upload'
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Copy all files to the dataset directory
    shutil.copy(args.csv, os.path.join(dataset_dir, os.path.basename(args.csv)))
    shutil.copy(args.excel, os.path.join(dataset_dir, os.path.basename(args.excel)))
    shutil.copy(args.pickle, os.path.join(dataset_dir, os.path.basename(args.pickle)))
    shutil.copy(args.fetch_data, os.path.join(dataset_dir, os.path.basename(args.fetch_data)))
    
    # Copy the description file with the correct name for Kaggle
    description_dest = os.path.join(dataset_dir, 'kaggle_dataset_description.md')
    shutil.copy(args.description, description_dest)
    
    # Upload the dataset
    success = upload_dataset(args.metadata, args.description, dataset_dir)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

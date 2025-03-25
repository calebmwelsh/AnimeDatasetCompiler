"""
AniList Anime Dataset - Main Script

This script combines the data fetching from AniList and uploading to Kaggle
into a single workflow. It first fetches all anime data from AniList using their
GraphQL API, then uploads the resulting dataset to Kaggle.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(command, description):
    """
    Run a shell command and handle errors
    
    Args:
        command (list): Command to run as a list of arguments
        description (str): Description of the command for output
        
    Returns:
        bool: True if command succeeded, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"STEP: {description}")
    print(f"{'='*80}")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True)
        print(f"Command completed successfully with exit code {result.returncode}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def fetch_anilist_data(test_mode=False):
    """
    Fetch anime data from AniList
    
    Args:
        test_mode (bool): Whether to run in test mode (limited data)
        
    Returns:
        bool: True if data fetching succeeded, False otherwise
    """
    command = ["python", "fetch_data.py"]
    if test_mode:
        command.append("--test")
    
    return run_command(command, "Fetching anime data from AniList")

def upload_to_kaggle():
    """
    Upload dataset to Kaggle
    
    Returns:
        bool: True if upload succeeded, False otherwise
    """
    command = ["python", "upload_data.py"]
    return run_command(command, "Uploading dataset to Kaggle")

def main():
    """Main function to handle command line arguments and run the workflow"""
    parser = argparse.ArgumentParser(
        description='AniList Anime Dataset - Fetch data and upload to Kaggle')
    
    # Data fetching options
    parser.add_argument('--test', action='store_true',
                        help='Run data fetching in test mode (limited data)')
    
    # Workflow options
    parser.add_argument('--skip-fetch', action='store_true',
                        help='Skip data fetching step (use existing data files)')
    parser.add_argument('--skip-upload', action='store_true',
                        help='Skip Kaggle upload step')
    
    args = parser.parse_args()
    
    # Check if required scripts exist
    required_files = [
        "fetch_data.py",
        "upload_data.py",
        "data/kaggle/kaggle_dataset_metadata.json",
        "data/kaggle/kaggle_dataset_description.md",
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Error: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        return 1
    
    # Step 1: Fetch data from AniList (unless skipped)
    if not args.skip_fetch:
        if not fetch_anilist_data(args.test):
            print("Error: Data fetching failed. Aborting workflow.")
            return 1
        
        # Check if data files were created
        data_files = [
            "data/raw/anilist_anime_data_complete.csv",
            "data/raw/anilist_anime_data_complete.xlsx",
            "data/raw/anilist_anime_data_complete.pkl"
        ]
        
        missing_data = []
        for file in data_files:
            if not os.path.exists(file):
                missing_data.append(file)
        
        if missing_data:
            print("Error: The following data files were not created:")
            for file in missing_data:
                print(f"  - {file}")
            return 1
    else:
        print("\nSkipping data fetching step as requested.")
    
    # Step 2: Upload to Kaggle (unless skipped)
    if not args.skip_upload:
        if not upload_to_kaggle():
            print("Error: Kaggle upload failed.")
            return 1
    else:
        print("\nSkipping Kaggle upload step as requested.")
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*80)
    
    if args.skip_fetch:
        print("- Data fetching was skipped")
    else:
        print("- Data was successfully fetched from AniList")
    
    if args.skip_upload:
        print("- Kaggle upload was skipped")
    else:
        print("- Data was successfully uploaded to Kaggle")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

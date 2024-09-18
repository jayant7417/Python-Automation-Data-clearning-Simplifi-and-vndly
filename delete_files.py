import glob
import os
from pathlib import Path

def delete_files(folder_path):
    # Define all the paths
    paths = [
        Path(folder_path).joinpath('job board'),
        Path(folder_path).joinpath('merged'),
        Path(folder_path).joinpath('result').joinpath('simplifi'),
        Path(folder_path).joinpath('result').joinpath('vndly'),
        Path(folder_path).joinpath('vms').joinpath('simplifi'),
        Path(folder_path).joinpath('vms').joinpath('vndly').joinpath('dna'),
        Path(folder_path).joinpath('vms').joinpath('vndly').joinpath('lah')
    ]
    
    # Iterate through each path
    for path in paths:
        # Get a list of all files in the current directory
        files = glob.glob(os.path.join(path, '*'))
        
        # Delete each file
        for file in files:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")
"""
    Simple script to delete specified folders 
"""

import os
import shutil

def remove_folders(root_dir: str, folders_to_remove: list = ["__pycache__", "logs"]):
    """
    Removes folders from the specified root directory and its subdirectories.
    by default it will remove __pycache__ and logs folders
    """  
    # Folders to delete
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for folder in folders_to_remove:
            if folder in dirnames:
                folder_path = os.path.join(dirpath, folder)
                try:
                    shutil.rmtree(folder_path)
                    print(f"Deleted: {folder_path}")
                except Exception as e:
                    print(f"Failed to delete {folder_path}: {e}")

if __name__ == "__main__":
    root_folder = os.getcwd()  # Current folder
    remove_folders(root_folder)

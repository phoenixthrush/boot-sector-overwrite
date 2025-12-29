#!/usr/bin/env python3
"""
Clean build artifacts and temporary files.

This script removes all generated files to start fresh.
"""

import os
import shutil
from pathlib import Path


def clean_artifacts():
    """Remove build artifacts and temporary files."""
    
    # Directories to remove
    dirs_to_clean = [
        'dist',
        '__pycache__',
        'src/__pycache__',
        'src/common/__pycache__',
        'src/variants/__pycache__',
        'src/tools/__pycache__',
        'src/variants/custom_message/__pycache__',
        'src/variants/empty/__pycache__',
        'src/variants/memz/__pycache__',
    ]
    
    # Files to remove
    files_to_remove = [
        '*.pyc',
        '*.pyo',
        '*.o',
        '*.obj',
        '*.exe',
        '*.bin',
    ]
    
    print(" Cleaning build artifacts...")
    
    # Remove directories
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🗑️  Removing directory: {dir_path}")
            shutil.rmtree(dir_path)
    
    # Remove files matching patterns
    for pattern in files_to_remove:
        for file_path in Path('.').rglob(pattern):
            if file_path.is_file():
                print(f"🗑️  Removing file: {file_path}")
                file_path.unlink()
    
    print(" Clean completed!")


if __name__ == "__main__":
    clean_artifacts()
#!/usr/bin/env python3
"""
Quick test script to verify project structure.
"""

import sys
from pathlib import Path

def check_structure():
    """Check if project structure is correct."""
    required_dirs = [
        'src',
        'src/common', 
        'src/variants',
        'src/variants/custom_message',
        'src/variants/empty',
        'src/variants/memz',
        'src/tools',
        'dist',
        'docs',
        'tests'
    ]
    
    required_files = [
        'build.py',
        'test.py', 
        'README.md',
        'requirements.txt',
        '.gitignore'
    ]
    
    print("🔍 Checking project structure...")
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
    else:
        print("✅ All directories present")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
    else:
        print("✅ All files present")
    
    if not missing_dirs and not missing_files:
        print("🎉 Project structure is correct!")
        return True
    else:
        return False

if __name__ == "__main__":
    check_structure()
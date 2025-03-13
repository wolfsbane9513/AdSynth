"""
File cleanup utility for managing temporary JSON files.
"""

import os
import glob
import time
from datetime import datetime, timedelta

def cleanup_temp_files(directory: str = ".", max_age_hours: int = 24, file_pattern: str = "*.json") -> None:
    """
    Clean up temporary files that are older than the specified age.
    
    Args:
        directory (str): Directory to clean up
        max_age_hours (int): Maximum age of files in hours
        file_pattern (str): Pattern to match files for cleanup
    """
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    # Find all matching files
    pattern = os.path.join(directory, file_pattern)
    for filepath in glob.glob(pattern):
        try:
            # Skip if file is still being written to
            if os.path.basename(filepath) == "package.json":
                continue
                
            # Check file age
            file_time = os.path.getmtime(filepath)
            age_seconds = current_time - file_time
            
            if age_seconds > max_age_seconds:
                os.remove(filepath)
                print(f"Removed old temporary file: {filepath}")
                
        except Exception as e:
            print(f"Error cleaning up file {filepath}: {e}")

def schedule_cleanup(interval_hours: int = 24) -> None:
    """
    Schedule periodic cleanup of temporary files.
    
    Args:
        interval_hours (int): Interval between cleanups in hours
    """
    while True:
        cleanup_temp_files()
        time.sleep(interval_hours * 3600) 
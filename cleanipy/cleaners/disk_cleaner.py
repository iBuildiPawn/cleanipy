"""
Disk cleaning functionality.
"""
import os
import shutil
from typing import List, Dict, Callable
from pathlib import Path

from send2trash import send2trash

from cleanipy.utils.file_utils import get_file_size, is_file_older_than
from cleanipy.utils.size_utils import format_size


def clean_directory(directory: str, callback: Callable = None) -> Dict[str, any]:
    """
    Clean a directory by removing all files and subdirectories.
    
    Args:
        directory: Directory to clean
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "directory": directory,
        "total_size_bytes": 0,
        "total_count": 0,
        "success": False,
        "error": None
    }
    
    try:
        # Calculate total size before cleaning
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                try:
                    file_path = os.path.join(dirpath, filename)
                    if not os.path.islink(file_path):
                        size = get_file_size(file_path)
                        result["total_size_bytes"] += size
                        result["total_count"] += 1
                except (PermissionError, FileNotFoundError):
                    continue
        
        # Clean the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                
                if callback:
                    callback(item_path)
            except (PermissionError, FileNotFoundError, OSError) as e:
                # Skip items that can't be removed
                continue
        
        result["success"] = True
    except (PermissionError, FileNotFoundError, OSError) as e:
        result["success"] = False
        result["error"] = str(e)
    
    # Add formatted size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result


def clean_old_files(directory: str, min_age_days: int = 30, callback: Callable = None) -> Dict[str, any]:
    """
    Clean old files in a directory.
    
    Args:
        directory: Directory to clean
        min_age_days: Minimum age of files in days to remove
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "directory": directory,
        "total_size_bytes": 0,
        "total_count": 0,
        "success": True,
        "error": None
    }
    
    try:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                try:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.islink(file_path):
                        continue
                    
                    # Check if file is old enough
                    if is_file_older_than(file_path, min_age_days):
                        # Get file size before removing
                        size = get_file_size(file_path)
                        
                        # Remove the file
                        try:
                            send2trash(file_path)
                            result["total_size_bytes"] += size
                            result["total_count"] += 1
                            
                            if callback:
                                callback(file_path)
                        except Exception:
                            # Try regular delete if send2trash fails
                            try:
                                os.remove(file_path)
                                result["total_size_bytes"] += size
                                result["total_count"] += 1
                                
                                if callback:
                                    callback(file_path)
                            except (PermissionError, FileNotFoundError, OSError):
                                # Skip files that can't be removed
                                continue
                except (PermissionError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue
    except (PermissionError, FileNotFoundError, OSError) as e:
        result["success"] = False
        result["error"] = str(e)
    
    # Add formatted size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result


def clean_large_files(directory: str, min_size_bytes: int = 100 * 1024 * 1024, 
                     file_paths: List[str] = None, callback: Callable = None) -> Dict[str, any]:
    """
    Clean large files in a directory or specific files.
    
    Args:
        directory: Directory to clean (ignored if file_paths is provided)
        min_size_bytes: Minimum file size in bytes to remove
        file_paths: Specific file paths to remove (if provided, directory and min_size are ignored)
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "success": True,
        "error": None
    }
    
    try:
        # If specific file paths are provided, clean those
        if file_paths:
            for file_path in file_paths:
                try:
                    if os.path.isfile(file_path) and not os.path.islink(file_path):
                        # Get file size before removing
                        size = get_file_size(file_path)
                        
                        # Remove the file
                        try:
                            send2trash(file_path)
                            result["total_size_bytes"] += size
                            result["total_count"] += 1
                            
                            if callback:
                                callback(file_path)
                        except Exception:
                            # Try regular delete if send2trash fails
                            try:
                                os.remove(file_path)
                                result["total_size_bytes"] += size
                                result["total_count"] += 1
                                
                                if callback:
                                    callback(file_path)
                            except (PermissionError, FileNotFoundError, OSError):
                                # Skip files that can't be removed
                                continue
                except (PermissionError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue
        # Otherwise, find and clean large files in the directory
        else:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    try:
                        file_path = os.path.join(dirpath, filename)
                        if os.path.islink(file_path):
                            continue
                        
                        # Check if file is large enough
                        size = get_file_size(file_path)
                        if size >= min_size_bytes:
                            # Remove the file
                            try:
                                send2trash(file_path)
                                result["total_size_bytes"] += size
                                result["total_count"] += 1
                                
                                if callback:
                                    callback(file_path)
                            except Exception:
                                # Try regular delete if send2trash fails
                                try:
                                    os.remove(file_path)
                                    result["total_size_bytes"] += size
                                    result["total_count"] += 1
                                    
                                    if callback:
                                        callback(file_path)
                                except (PermissionError, FileNotFoundError, OSError):
                                    # Skip files that can't be removed
                                    continue
                    except (PermissionError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
    except (PermissionError, FileNotFoundError, OSError) as e:
        result["success"] = False
        result["error"] = str(e)
    
    # Add formatted size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result

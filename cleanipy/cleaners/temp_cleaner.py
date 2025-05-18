"""
Temporary file cleaning functionality.
"""
import os
import platform
import subprocess
from typing import List, Dict, Callable

from cleanipy.analyzers.temp_analyzer import (
    get_system_temp_dirs,
    get_browser_cache_dirs,
    get_package_cache_dirs
)
from cleanipy.cleaners.disk_cleaner import clean_directory, clean_old_files


def clean_system_temp_files(min_age_days: int = 7, callback: Callable = None) -> Dict[str, any]:
    """
    Clean system temporary files.
    
    Args:
        min_age_days: Minimum age of files in days to remove
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "details": []
    }
    
    # Get system temp directories
    temp_dirs = get_system_temp_dirs()
    
    # Clean each directory
    for temp_dir in temp_dirs:
        # Clean old files instead of entire directory to avoid removing important files
        clean_result = clean_old_files(temp_dir, min_age_days, callback)
        
        result["total_size_bytes"] += clean_result["total_size_bytes"]
        result["total_count"] += clean_result["total_count"]
        result["details"].append(clean_result)
    
    # Add formatted total size
    from cleanipy.utils.size_utils import format_size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result


def clean_browser_caches(callback: Callable = None) -> Dict[str, any]:
    """
    Clean browser cache files.
    
    Args:
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "details": []
    }
    
    # Get browser cache directories
    cache_dirs = get_browser_cache_dirs()
    
    # Clean each directory
    for cache_dir in cache_dirs:
        # For browser caches, we can safely clean old files
        clean_result = clean_old_files(cache_dir, 1, callback)
        
        result["total_size_bytes"] += clean_result["total_size_bytes"]
        result["total_count"] += clean_result["total_count"]
        result["details"].append(clean_result)
    
    # Add formatted total size
    from cleanipy.utils.size_utils import format_size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result


def clean_package_caches(callback: Callable = None) -> Dict[str, any]:
    """
    Clean package manager cache files.
    
    Args:
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "details": []
    }
    
    # Get package cache directories
    cache_dirs = get_package_cache_dirs()
    
    # Clean each directory
    for cache_dir in cache_dirs:
        # For package caches, we need to be careful
        # Use OS-specific commands for some package managers
        system = platform.system()
        
        if system == "Linux":
            # For apt
            if "apt" in cache_dir:
                try:
                    # Try to use apt-get clean
                    subprocess.run(["sudo", "apt-get", "clean"], check=False)
                    # Calculate cleaned size (approximate)
                    clean_result = {
                        "directory": cache_dir,
                        "success": True,
                        "total_size": "Unknown (used apt-get clean)",
                        "total_count": 0
                    }
                except Exception:
                    # Fall back to regular cleaning
                    clean_result = clean_directory(cache_dir, callback)
            # For pacman
            elif "pacman" in cache_dir:
                try:
                    # Try to use pacman -Sc
                    subprocess.run(["sudo", "pacman", "-Sc", "--noconfirm"], check=False)
                    # Calculate cleaned size (approximate)
                    clean_result = {
                        "directory": cache_dir,
                        "success": True,
                        "total_size": "Unknown (used pacman -Sc)",
                        "total_count": 0
                    }
                except Exception:
                    # Fall back to regular cleaning
                    clean_result = clean_directory(cache_dir, callback)
            # For yum
            elif "yum" in cache_dir:
                try:
                    # Try to use yum clean
                    subprocess.run(["sudo", "yum", "clean", "all"], check=False)
                    # Calculate cleaned size (approximate)
                    clean_result = {
                        "directory": cache_dir,
                        "success": True,
                        "total_size": "Unknown (used yum clean all)",
                        "total_count": 0
                    }
                except Exception:
                    # Fall back to regular cleaning
                    clean_result = clean_directory(cache_dir, callback)
            else:
                # For other caches, clean the directory
                clean_result = clean_directory(cache_dir, callback)
        elif system == "Darwin" and "Homebrew" in cache_dir:
            # For Homebrew on macOS
            try:
                # Try to use brew cleanup
                subprocess.run(["brew", "cleanup"], check=False)
                # Calculate cleaned size (approximate)
                clean_result = {
                    "directory": cache_dir,
                    "success": True,
                    "total_size": "Unknown (used brew cleanup)",
                    "total_count": 0
                }
            except Exception:
                # Fall back to regular cleaning
                clean_result = clean_directory(cache_dir, callback)
        else:
            # For other caches, clean the directory
            clean_result = clean_directory(cache_dir, callback)
        
        # Add to result if size is known
        if isinstance(clean_result.get("total_size_bytes"), int):
            result["total_size_bytes"] += clean_result["total_size_bytes"]
        if isinstance(clean_result.get("total_count"), int):
            result["total_count"] += clean_result["total_count"]
        
        result["details"].append(clean_result)
    
    # Add formatted total size
    from cleanipy.utils.size_utils import format_size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result

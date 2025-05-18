"""
Temporary file analysis functionality.
"""
import os
import tempfile
import platform
from pathlib import Path
from typing import List, Dict, Set, Generator

from cleanipy.utils.file_utils import get_file_size, is_file_older_than
from cleanipy.utils.size_utils import format_size


def get_system_temp_dirs() -> List[str]:
    """
    Get system temporary directories.
    
    Returns:
        List of temporary directory paths
    """
    temp_dirs = []
    
    # Add Python's tempfile.gettempdir()
    temp_dirs.append(tempfile.gettempdir())
    
    # Add OS-specific temp directories
    system = platform.system()
    if system == "Windows":
        # Windows temp directories
        temp_dirs.extend([
            os.path.expandvars("%TEMP%"),
            os.path.expandvars("%TMP%"),
            os.path.join(os.path.expandvars("%WINDIR%"), "Temp")
        ])
    elif system == "Darwin":
        # macOS temp directories
        temp_dirs.extend([
            "/tmp",
            "/var/tmp",
            os.path.expanduser("~/Library/Caches")
        ])
    elif system == "Linux":
        # Linux temp directories
        temp_dirs.extend([
            "/tmp",
            "/var/tmp",
            "/var/cache"
        ])
    
    # Remove duplicates and non-existent directories
    temp_dirs = list(set(temp_dirs))
    temp_dirs = [d for d in temp_dirs if os.path.exists(d)]
    
    return temp_dirs


def get_browser_cache_dirs() -> List[str]:
    """
    Get browser cache directories.
    
    Returns:
        List of browser cache directory paths
    """
    cache_dirs = []
    home = os.path.expanduser("~")
    system = platform.system()
    
    if system == "Windows":
        # Windows browser cache paths
        cache_dirs.extend([
            os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache"),
            os.path.join(home, "AppData", "Local", "Mozilla", "Firefox", "Profiles"),
            os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache")
        ])
    elif system == "Darwin":
        # macOS browser cache paths
        cache_dirs.extend([
            os.path.join(home, "Library", "Caches", "Google", "Chrome"),
            os.path.join(home, "Library", "Caches", "Firefox"),
            os.path.join(home, "Library", "Caches", "com.apple.Safari")
        ])
    elif system == "Linux":
        # Linux browser cache paths
        cache_dirs.extend([
            os.path.join(home, ".cache", "google-chrome"),
            os.path.join(home, ".cache", "mozilla", "firefox"),
            os.path.join(home, ".cache", "chromium")
        ])
    
    # Remove non-existent directories
    cache_dirs = [d for d in cache_dirs if os.path.exists(d)]
    
    return cache_dirs


def get_package_cache_dirs() -> List[str]:
    """
    Get package manager cache directories.
    
    Returns:
        List of package manager cache directory paths
    """
    cache_dirs = []
    home = os.path.expanduser("~")
    system = platform.system()
    
    if system == "Windows":
        # Windows package manager cache paths
        cache_dirs.extend([
            os.path.join(home, "AppData", "Local", "pip", "Cache"),
            os.path.join(home, "AppData", "Local", "Temp", "chocolatey")
        ])
    elif system == "Darwin":
        # macOS package manager cache paths
        cache_dirs.extend([
            os.path.join(home, "Library", "Caches", "pip"),
            os.path.join(home, "Library", "Caches", "Homebrew")
        ])
    elif system == "Linux":
        # Linux package manager cache paths
        cache_dirs.extend([
            "/var/cache/apt/archives",
            "/var/cache/pacman/pkg",
            "/var/cache/yum",
            os.path.join(home, ".cache", "pip")
        ])
    
    # Remove non-existent directories
    cache_dirs = [d for d in cache_dirs if os.path.exists(d)]
    
    return cache_dirs


def analyze_temp_files(directory: str, min_age_days: int = 7) -> Dict[str, any]:
    """
    Analyze temporary files in a directory.
    
    Args:
        directory: Directory to analyze
        min_age_days: Minimum age of files in days to consider for cleaning
        
    Returns:
        Dictionary with analysis results
    """
    result = {
        "directory": directory,
        "total_size_bytes": 0,
        "total_count": 0,
        "old_files_size_bytes": 0,
        "old_files_count": 0,
        "old_files": []
    }
    
    try:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                try:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.islink(file_path):
                        continue
                    
                    # Get file size
                    size = get_file_size(file_path)
                    result["total_size_bytes"] += size
                    result["total_count"] += 1
                    
                    # Check if file is old enough
                    if is_file_older_than(file_path, min_age_days):
                        result["old_files_size_bytes"] += size
                        result["old_files_count"] += 1
                        
                        # Add to old files list (limit to avoid excessive memory usage)
                        if len(result["old_files"]) < 1000:
                            result["old_files"].append({
                                "path": file_path,
                                "size_bytes": size,
                                "size": format_size(size)
                            })
                except (PermissionError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue
    except (PermissionError, FileNotFoundError):
        # Return empty result if the directory can't be accessed
        pass
    
    # Add formatted sizes
    result["total_size"] = format_size(result["total_size_bytes"])
    result["old_files_size"] = format_size(result["old_files_size_bytes"])
    
    return result

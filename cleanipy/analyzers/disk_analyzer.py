"""
Disk space analysis functionality.
"""
import os
import psutil
from typing import List, Dict, Tuple, Generator
from pathlib import Path

from cleanipy.utils.file_utils import get_directory_size, get_file_size
from cleanipy.utils.size_utils import format_size


def get_disk_usage() -> List[Dict[str, str]]:
    """
    Get disk usage information for all mounted partitions.
    
    Returns:
        List of dictionaries with disk usage information
    """
    disk_info = []
    
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total": format_size(usage.total),
                "used": format_size(usage.used),
                "free": format_size(usage.free),
                "percent": f"{usage.percent}%"
            })
        except (PermissionError, FileNotFoundError):
            # Skip partitions that can't be accessed
            continue
    
    return disk_info


def get_directory_tree_size(directory: str, depth: int = 1) -> List[Dict[str, str]]:
    """
    Get the size of subdirectories in the given directory up to a certain depth.
    
    Args:
        directory: Directory to analyze
        depth: Maximum depth to traverse
        
    Returns:
        List of dictionaries with directory information
    """
    result = []
    
    try:
        # Get immediate subdirectories
        subdirs = [os.path.join(directory, d) for d in os.listdir(directory) 
                  if os.path.isdir(os.path.join(directory, d))]
        
        # Calculate size for each subdirectory
        for subdir in subdirs:
            try:
                size = get_directory_size(subdir)
                result.append({
                    "path": subdir,
                    "size_bytes": size,
                    "size": format_size(size)
                })
                
                # Recursively get subdirectory sizes if depth allows
                if depth > 1:
                    subresult = get_directory_tree_size(subdir, depth - 1)
                    for item in subresult:
                        # Adjust the path to show the hierarchy
                        item["path"] = os.path.join(os.path.basename(subdir), os.path.basename(item["path"]))
                        result.append(item)
            except (PermissionError, FileNotFoundError):
                # Skip directories that can't be accessed
                continue
    except (PermissionError, FileNotFoundError):
        # Return empty list if the directory can't be accessed
        pass
    
    return result


def find_large_files(directory: str, min_size_bytes: int = 100 * 1024 * 1024) -> List[Dict[str, str]]:
    """
    Find files larger than the specified size.
    
    Args:
        directory: Directory to search in
        min_size_bytes: Minimum file size in bytes (default: 100 MB)
        
    Returns:
        List of dictionaries with file information
    """
    large_files = []
    
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            try:
                file_path = os.path.join(dirpath, filename)
                if os.path.islink(file_path):
                    continue
                    
                size = get_file_size(file_path)
                if size >= min_size_bytes:
                    large_files.append({
                        "path": file_path,
                        "size_bytes": size,
                        "size": format_size(size)
                    })
            except (PermissionError, FileNotFoundError):
                # Skip files that can't be accessed
                continue
    
    # Sort by size (largest first)
    large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
    
    return large_files


def get_file_types_summary(directory: str) -> Dict[str, Dict[str, str]]:
    """
    Get a summary of file types and their total sizes.
    
    Args:
        directory: Directory to analyze
        
    Returns:
        Dictionary with file type information
    """
    file_types = {}
    
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            try:
                file_path = os.path.join(dirpath, filename)
                if os.path.islink(file_path):
                    continue
                
                # Get file extension (lowercase)
                _, ext = os.path.splitext(filename)
                ext = ext.lower() if ext else "no extension"
                
                # Get file size
                size = get_file_size(file_path)
                
                # Update file type statistics
                if ext not in file_types:
                    file_types[ext] = {
                        "count": 0,
                        "total_size_bytes": 0
                    }
                
                file_types[ext]["count"] += 1
                file_types[ext]["total_size_bytes"] += size
            except (PermissionError, FileNotFoundError):
                # Skip files that can't be accessed
                continue
    
    # Add formatted size
    for ext in file_types:
        file_types[ext]["total_size"] = format_size(file_types[ext]["total_size_bytes"])
    
    return file_types

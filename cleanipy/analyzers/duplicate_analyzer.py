"""
Duplicate file analysis functionality.
"""
import os
from collections import defaultdict
from typing import List, Dict, Set, Generator, Tuple

from cleanipy.utils.file_utils import get_file_size, get_file_hash
from cleanipy.utils.size_utils import format_size


def find_duplicate_files_by_size(directory: str, min_size: int = 1024) -> Dict[int, List[str]]:
    """
    Find potential duplicate files by size.
    
    Args:
        directory: Directory to search in
        min_size: Minimum file size to consider (to avoid small files)
        
    Returns:
        Dictionary with file sizes as keys and lists of file paths as values
    """
    size_dict = defaultdict(list)
    
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            try:
                file_path = os.path.join(dirpath, filename)
                if os.path.islink(file_path):
                    continue
                
                # Get file size
                size = get_file_size(file_path)
                
                # Only consider files larger than min_size
                if size >= min_size:
                    size_dict[size].append(file_path)
            except (PermissionError, FileNotFoundError):
                # Skip files that can't be accessed
                continue
    
    # Filter out sizes with only one file (no duplicates)
    return {size: files for size, files in size_dict.items() if len(files) > 1}


def find_duplicate_files_by_content(directory: str, min_size: int = 1024) -> Dict[str, List[Dict[str, any]]]:
    """
    Find duplicate files by content (using hash).
    
    Args:
        directory: Directory to search in
        min_size: Minimum file size to consider (to avoid small files)
        
    Returns:
        Dictionary with file hashes as keys and lists of file information as values
    """
    # First, find potential duplicates by size
    size_dict = find_duplicate_files_by_size(directory, min_size)
    
    # Then, check content hash for files of the same size
    hash_dict = defaultdict(list)
    
    for size, files in size_dict.items():
        for file_path in files:
            try:
                # Calculate file hash
                file_hash = get_file_hash(file_path)
                
                if file_hash:  # Skip if hash calculation failed
                    hash_dict[file_hash].append({
                        "path": file_path,
                        "size_bytes": size,
                        "size": format_size(size)
                    })
            except (PermissionError, FileNotFoundError):
                # Skip files that can't be accessed
                continue
    
    # Filter out hashes with only one file (no duplicates)
    return {hash_val: files for hash_val, files in hash_dict.items() if len(files) > 1}


def analyze_duplicate_files(directory: str, min_size: int = 1024) -> Dict[str, any]:
    """
    Analyze duplicate files in a directory.
    
    Args:
        directory: Directory to analyze
        min_size: Minimum file size to consider (to avoid small files)
        
    Returns:
        Dictionary with analysis results
    """
    # Find duplicate files
    duplicates = find_duplicate_files_by_content(directory, min_size)
    
    # Calculate statistics
    total_duplicate_sets = len(duplicates)
    total_duplicate_files = sum(len(files) - 1 for files in duplicates.values())
    total_wasted_space = sum((len(files) - 1) * files[0]["size_bytes"] for files in duplicates.values())
    
    # Prepare result
    result = {
        "directory": directory,
        "total_duplicate_sets": total_duplicate_sets,
        "total_duplicate_files": total_duplicate_files,
        "total_wasted_space_bytes": total_wasted_space,
        "total_wasted_space": format_size(total_wasted_space),
        "duplicates": duplicates
    }
    
    return result


def get_duplicate_sets(directory: str, min_size: int = 1024, limit: int = 10) -> List[Dict[str, any]]:
    """
    Get sets of duplicate files, sorted by wasted space.
    
    Args:
        directory: Directory to analyze
        min_size: Minimum file size to consider
        limit: Maximum number of duplicate sets to return
        
    Returns:
        List of dictionaries with duplicate file information
    """
    # Find duplicate files
    duplicates = find_duplicate_files_by_content(directory, min_size)
    
    # Convert to list and calculate wasted space for each set
    duplicate_sets = []
    for hash_val, files in duplicates.items():
        wasted_space = (len(files) - 1) * files[0]["size_bytes"]
        duplicate_sets.append({
            "hash": hash_val,
            "files": files,
            "count": len(files),
            "wasted_space_bytes": wasted_space,
            "wasted_space": format_size(wasted_space),
            "file_size": files[0]["size"]
        })
    
    # Sort by wasted space (largest first)
    duplicate_sets.sort(key=lambda x: x["wasted_space_bytes"], reverse=True)
    
    # Limit the number of sets
    return duplicate_sets[:limit]

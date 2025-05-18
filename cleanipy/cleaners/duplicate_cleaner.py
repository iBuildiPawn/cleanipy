"""
Duplicate file cleaning functionality.
"""
import os
import shutil
from typing import List, Dict, Callable

from send2trash import send2trash

from cleanipy.analyzers.duplicate_analyzer import find_duplicate_files_by_content
from cleanipy.utils.size_utils import format_size


def clean_duplicate_files(directory: str, duplicates: Dict[str, List[Dict[str, any]]] = None, 
                         keep_newest: bool = True, callback: Callable = None) -> Dict[str, any]:
    """
    Clean duplicate files in a directory.
    
    Args:
        directory: Directory to clean
        duplicates: Dictionary of duplicate files (if None, will be calculated)
        keep_newest: Whether to keep the newest file in each duplicate set
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with cleaning results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "details": []
    }
    
    # Find duplicate files if not provided
    if duplicates is None:
        duplicates = find_duplicate_files_by_content(directory)
    
    # Clean each set of duplicates
    for hash_val, files in duplicates.items():
        # Sort files by modification time (newest first)
        files_sorted = sorted(files, key=lambda x: os.path.getmtime(x["path"]), reverse=True)
        
        # Keep the first file (newest or oldest based on keep_newest)
        files_to_remove = files_sorted[1:] if keep_newest else files_sorted[:-1]
        
        # Remove duplicate files
        for file_info in files_to_remove:
            file_path = file_info["path"]
            try:
                # Try to use send2trash for safety
                send2trash(file_path)
                result["total_size_bytes"] += file_info["size_bytes"]
                result["total_count"] += 1
                
                # Add to details
                result["details"].append({
                    "path": file_path,
                    "size_bytes": file_info["size_bytes"],
                    "size": file_info["size"],
                    "success": True
                })
                
                if callback:
                    callback(file_path)
            except Exception:
                # Try regular delete if send2trash fails
                try:
                    os.remove(file_path)
                    result["total_size_bytes"] += file_info["size_bytes"]
                    result["total_count"] += 1
                    
                    # Add to details
                    result["details"].append({
                        "path": file_path,
                        "size_bytes": file_info["size_bytes"],
                        "size": file_info["size"],
                        "success": True
                    })
                    
                    if callback:
                        callback(file_path)
                except (PermissionError, FileNotFoundError, OSError) as e:
                    # Add to details with error
                    result["details"].append({
                        "path": file_path,
                        "size_bytes": file_info["size_bytes"],
                        "size": file_info["size"],
                        "success": False,
                        "error": str(e)
                    })
    
    # Add formatted total size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result


def replace_duplicates_with_hardlinks(directory: str, duplicates: Dict[str, List[Dict[str, any]]] = None,
                                     keep_newest: bool = True, callback: Callable = None) -> Dict[str, any]:
    """
    Replace duplicate files with hard links to save space.
    
    Args:
        directory: Directory to process
        duplicates: Dictionary of duplicate files (if None, will be calculated)
        keep_newest: Whether to keep the newest file as the source for hard links
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "details": []
    }
    
    # Find duplicate files if not provided
    if duplicates is None:
        duplicates = find_duplicate_files_by_content(directory)
    
    # Process each set of duplicates
    for hash_val, files in duplicates.items():
        # Sort files by modification time (newest first)
        files_sorted = sorted(files, key=lambda x: os.path.getmtime(x["path"]), reverse=True)
        
        # Use the first file as the source (newest or oldest based on keep_newest)
        source_file = files_sorted[0]["path"] if keep_newest else files_sorted[-1]["path"]
        
        # Replace duplicates with hard links
        files_to_link = files_sorted[1:] if keep_newest else files_sorted[:-1]
        
        for file_info in files_to_link:
            target_file = file_info["path"]
            try:
                # Remove the target file
                os.remove(target_file)
                
                # Create a hard link
                os.link(source_file, target_file)
                
                result["total_size_bytes"] += file_info["size_bytes"]
                result["total_count"] += 1
                
                # Add to details
                result["details"].append({
                    "source": source_file,
                    "target": target_file,
                    "size_bytes": file_info["size_bytes"],
                    "size": file_info["size"],
                    "success": True
                })
                
                if callback:
                    callback(target_file)
            except (PermissionError, FileNotFoundError, OSError) as e:
                # Add to details with error
                result["details"].append({
                    "source": source_file,
                    "target": target_file,
                    "size_bytes": file_info["size_bytes"],
                    "size": file_info["size"],
                    "success": False,
                    "error": str(e)
                })
    
    # Add formatted total size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result


def replace_duplicates_with_symlinks(directory: str, duplicates: Dict[str, List[Dict[str, any]]] = None,
                                    keep_newest: bool = True, callback: Callable = None) -> Dict[str, any]:
    """
    Replace duplicate files with symbolic links to save space.
    
    Args:
        directory: Directory to process
        duplicates: Dictionary of duplicate files (if None, will be calculated)
        keep_newest: Whether to keep the newest file as the source for symbolic links
        callback: Optional callback function to report progress
        
    Returns:
        Dictionary with results
    """
    result = {
        "total_size_bytes": 0,
        "total_count": 0,
        "details": []
    }
    
    # Find duplicate files if not provided
    if duplicates is None:
        duplicates = find_duplicate_files_by_content(directory)
    
    # Process each set of duplicates
    for hash_val, files in duplicates.items():
        # Sort files by modification time (newest first)
        files_sorted = sorted(files, key=lambda x: os.path.getmtime(x["path"]), reverse=True)
        
        # Use the first file as the source (newest or oldest based on keep_newest)
        source_file = files_sorted[0]["path"] if keep_newest else files_sorted[-1]["path"]
        
        # Replace duplicates with symbolic links
        files_to_link = files_sorted[1:] if keep_newest else files_sorted[:-1]
        
        for file_info in files_to_link:
            target_file = file_info["path"]
            try:
                # Remove the target file
                os.remove(target_file)
                
                # Create a symbolic link
                os.symlink(os.path.abspath(source_file), target_file)
                
                result["total_size_bytes"] += file_info["size_bytes"]
                result["total_count"] += 1
                
                # Add to details
                result["details"].append({
                    "source": source_file,
                    "target": target_file,
                    "size_bytes": file_info["size_bytes"],
                    "size": file_info["size"],
                    "success": True
                })
                
                if callback:
                    callback(target_file)
            except (PermissionError, FileNotFoundError, OSError) as e:
                # Add to details with error
                result["details"].append({
                    "source": source_file,
                    "target": target_file,
                    "size_bytes": file_info["size_bytes"],
                    "size": file_info["size"],
                    "success": False,
                    "error": str(e)
                })
    
    # Add formatted total size
    result["total_size"] = format_size(result["total_size_bytes"])
    
    return result

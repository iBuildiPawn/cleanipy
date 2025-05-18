"""
Utility functions for file operations.
"""
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Generator, Tuple


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        Size of the file in bytes
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, PermissionError):
        return 0


def get_directory_size(directory: str) -> int:
    """
    Calculate the total size of a directory in bytes.

    Args:
        directory: Path to the directory

    Returns:
        Total size in bytes
    """
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if not os.path.islink(file_path):
                    total_size += get_file_size(file_path)
    except (PermissionError, FileNotFoundError):
        pass

    return total_size


def get_file_hash(file_path: str, block_size: int = 65536) -> str:
    """
    Calculate the SHA-256 hash of a file.

    Args:
        file_path: Path to the file
        block_size: Size of blocks to read

    Returns:
        SHA-256 hash as a hexadecimal string
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            buf = file.read(block_size)
            while buf:
                hasher.update(buf)
                buf = file.read(block_size)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError):
        return ""


def find_files_by_extension(directory: str, extensions: List[str]) -> Generator[str, None, None]:
    """
    Find all files with specific extensions in a directory and its subdirectories.

    Args:
        directory: Directory to search in
        extensions: List of file extensions to look for (e.g., ['.txt', '.log'])

    Yields:
        Paths to files with matching extensions
    """
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                yield os.path.join(dirpath, filename)


def find_files_by_pattern(directory: str, pattern: str) -> Generator[str, None, None]:
    """
    Find all files matching a glob pattern in a directory and its subdirectories.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match (e.g., '*.log')

    Yields:
        Paths to files matching the pattern
    """
    return Path(directory).rglob(pattern)


def is_file_older_than(file_path: str, days: int) -> bool:
    """
    Check if a file is older than a specified number of days.

    Args:
        file_path: Path to the file
        days: Number of days

    Returns:
        True if the file is older than the specified number of days
    """
    try:
        file_time = os.path.getmtime(file_path)
        import time
        current_time = time.time()
        # If days is 0, all files are considered newer
        if days <= 0:
            return False
        return (current_time - file_time) > (days * 86400)  # 86400 seconds in a day
    except (FileNotFoundError, PermissionError):
        return False

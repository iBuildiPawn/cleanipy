"""
Utility functions for handling file sizes and conversions.
"""
from typing import Tuple


def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.23 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    # Define size units and their respective thresholds
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    
    # Calculate the appropriate unit
    import math
    unit_index = min(5, math.floor(math.log(size_bytes, 1024)))
    size_value = size_bytes / (1024 ** unit_index)
    
    # Format the output
    if unit_index == 0:
        # For bytes, show as integer
        return f"{int(size_value)} {units[unit_index]}"
    else:
        # For larger units, show with 2 decimal places
        return f"{size_value:.2f} {units[unit_index]}"


def parse_size(size_str: str) -> int:
    """
    Parse a human-readable size string to bytes.
    
    Args:
        size_str: Human-readable size string (e.g., "1.23 MB")
        
    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()
    
    # Define size units and their respective multipliers
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
        "PB": 1024 ** 5
    }
    
    # Extract the numeric part and the unit
    import re
    match = re.match(r"^([\d.]+)\s*([A-Z]+)$", size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    value, unit = match.groups()
    
    # Convert to bytes
    if unit not in units:
        raise ValueError(f"Unknown unit: {unit}")
    
    return int(float(value) * units[unit])


def get_size_distribution(sizes: list) -> dict:
    """
    Calculate the distribution of sizes.
    
    Args:
        sizes: List of sizes in bytes
        
    Returns:
        Dictionary with size ranges as keys and counts as values
    """
    ranges = {
        "< 1 KB": 0,
        "1 KB - 1 MB": 0,
        "1 MB - 10 MB": 0,
        "10 MB - 100 MB": 0,
        "100 MB - 1 GB": 0,
        "> 1 GB": 0
    }
    
    for size in sizes:
        if size < 1024:
            ranges["< 1 KB"] += 1
        elif size < 1024 ** 2:
            ranges["1 KB - 1 MB"] += 1
        elif size < 10 * 1024 ** 2:
            ranges["1 MB - 10 MB"] += 1
        elif size < 100 * 1024 ** 2:
            ranges["10 MB - 100 MB"] += 1
        elif size < 1024 ** 3:
            ranges["100 MB - 1 GB"] += 1
        else:
            ranges["> 1 GB"] += 1
    
    return ranges

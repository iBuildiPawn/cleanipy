"""
CleanIPy - A terminal application to clean and free up storage space.
"""
import os
import sys
import click
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from cleanipy.utils.ui import (
    print_header, print_subheader, print_success, print_warning,
    print_error, print_info, confirm_action, display_menu,
    create_table, display_table, create_progress_bar
)
from cleanipy.utils.size_utils import format_size

from cleanipy.analyzers.disk_analyzer import (
    get_disk_usage, get_directory_tree_size, find_large_files, get_file_types_summary
)
from cleanipy.analyzers.temp_analyzer import (
    get_system_temp_dirs, get_browser_cache_dirs, get_package_cache_dirs,
    analyze_temp_files as analyze_temp_directory
)
from cleanipy.analyzers.duplicate_analyzer import (
    analyze_duplicate_files, get_duplicate_sets
)

from cleanipy.cleaners.disk_cleaner import (
    clean_directory, clean_old_files, clean_large_files
)
from cleanipy.cleaners.temp_cleaner import (
    clean_system_temp_files, clean_browser_caches, clean_package_caches
)
from cleanipy.cleaners.duplicate_cleaner import (
    clean_duplicate_files, replace_duplicates_with_hardlinks, replace_duplicates_with_symlinks
)


# Create a console instance
console = Console()


def show_disk_usage():
    """Show disk usage information."""
    print_header("Disk Usage Information")

    # Get disk usage
    disk_info = get_disk_usage()

    # Create table
    table = create_table("Disk Usage", ["Device", "Mount Point", "Filesystem", "Total", "Used", "Free", "Usage"])

    # Add rows
    for disk in disk_info:
        table.add_row(
            disk["device"],
            disk["mountpoint"],
            disk["filesystem"],
            disk["total"],
            disk["used"],
            disk["free"],
            disk["percent"]
        )

    # Display table
    display_table(table)


def analyze_directory():
    """Analyze a directory for disk usage."""
    print_header("Directory Analysis")

    # Get directory to analyze
    directory = click.prompt("Enter directory path to analyze", default=os.path.expanduser("~"))

    if not os.path.exists(directory):
        print_error(f"Directory '{directory}' does not exist.")
        return

    # Create progress bar
    with create_progress_bar() as progress:
        task = progress.add_task("Analyzing directory...", total=None)

        # Get directory tree size
        progress.update(task, description="Analyzing directory sizes...")
        dir_sizes = get_directory_tree_size(directory, depth=1)

        # Find large files
        progress.update(task, description="Finding large files...")
        large_files = find_large_files(directory)

        # Get file types summary
        progress.update(task, description="Analyzing file types...")
        file_types = get_file_types_summary(directory)

    # Directory Size Analysis
    print_subheader("Directory Size Analysis")

    # Sort by size (largest first)
    dir_sizes.sort(key=lambda x: x["size_bytes"], reverse=True)

    # Create table
    table = create_table("Directory Sizes", ["Path", "Size"])

    # Add rows (limit to top 20)
    for dir_info in dir_sizes[:20]:
        table.add_row(
            dir_info["path"],
            dir_info["size"]
        )

    # Display table
    display_table(table)

    # Large Files Analysis
    print_subheader("Large Files Analysis")

    # Create table
    table = create_table("Large Files", ["Path", "Size"])

    # Add rows (limit to top 20)
    for file_info in large_files[:20]:
        table.add_row(
            file_info["path"],
            file_info["size"]
        )

    # Display table
    display_table(table)

    # File Types Analysis
    print_subheader("File Types Analysis")

    # Sort by total size (largest first)
    file_types_sorted = sorted(file_types.items(), key=lambda x: x[1]["total_size_bytes"], reverse=True)

    # Create table
    table = create_table("File Types", ["Extension", "Count", "Total Size"])

    # Add rows (limit to top 20)
    for ext, info in file_types_sorted[:20]:
        table.add_row(
            ext,
            str(info["count"]),
            info["total_size"]
        )

    # Display table
    display_table(table)


def analyze_temp_files():
    """Analyze temporary files."""
    print_header("Temporary Files Analysis")

    # Create progress bar
    with create_progress_bar() as progress:
        task = progress.add_task("Analyzing temporary files...", total=None)

        # Get system temp directories
        progress.update(task, description="Analyzing system temp directories...")
        temp_dirs = get_system_temp_dirs()

        # Get browser cache directories
        progress.update(task, description="Analyzing browser caches...")
        browser_cache_dirs = get_browser_cache_dirs()

        # Get package cache directories
        progress.update(task, description="Analyzing package caches...")
        package_cache_dirs = get_package_cache_dirs()

        # Initialize counters
        total_size_bytes = 0
        total_old_size_bytes = 0

        # Analyze system temp directories
        system_temp_results = []
        for temp_dir in temp_dirs:
            progress.update(task, description=f"Analyzing: {os.path.basename(temp_dir)}")
            result = analyze_temp_directory(temp_dir)
            system_temp_results.append((temp_dir, result))
            total_size_bytes += result["total_size_bytes"]
            total_old_size_bytes += result["old_files_size_bytes"]

        # Analyze browser cache directories
        browser_cache_results = []
        for cache_dir in browser_cache_dirs:
            progress.update(task, description=f"Analyzing: {os.path.basename(cache_dir)}")
            result = analyze_temp_directory(cache_dir)
            browser_cache_results.append((cache_dir, result))
            total_size_bytes += result["total_size_bytes"]
            total_old_size_bytes += result["old_files_size_bytes"]

        # Analyze package cache directories
        package_cache_results = []
        for cache_dir in package_cache_dirs:
            progress.update(task, description=f"Analyzing: {os.path.basename(cache_dir)}")
            result = analyze_temp_directory(cache_dir)
            package_cache_results.append((cache_dir, result))
            total_size_bytes += result["total_size_bytes"]
            total_old_size_bytes += result["old_files_size_bytes"]

    # Display system temp directories
    print_subheader("System Temporary Directories")
    table = create_table("System Temp Directories", ["Directory", "Total Size", "Cleanable Size"])
    for temp_dir, result in system_temp_results:
        table.add_row(
            temp_dir,
            result["total_size"],
            result["old_files_size"]
        )
    display_table(table)

    # Display browser cache directories
    print_subheader("Browser Cache Directories")
    table = create_table("Browser Caches", ["Directory", "Total Size", "Cleanable Size"])
    for cache_dir, result in browser_cache_results:
        table.add_row(
            cache_dir,
            result["total_size"],
            result["old_files_size"]
        )
    display_table(table)

    # Display package cache directories
    print_subheader("Package Cache Directories")
    table = create_table("Package Caches", ["Directory", "Total Size", "Cleanable Size"])
    for cache_dir, result in package_cache_results:
        table.add_row(
            cache_dir,
            result["total_size"],
            result["old_files_size"]
        )
    display_table(table)

    # Show summary
    print_subheader("Summary")
    print_info(f"Total temporary files size: {format_size(total_size_bytes)}")
    print_info(f"Total cleanable size: {format_size(total_old_size_bytes)}")


def analyze_duplicates():
    """Analyze duplicate files."""
    print_header("Duplicate Files Analysis")

    # Get directory to analyze
    directory = click.prompt("Enter directory path to analyze", default=os.path.expanduser("~"))

    if not os.path.exists(directory):
        print_error(f"Directory '{directory}' does not exist.")
        return

    # Create progress bar for analysis
    with create_progress_bar() as progress:
        task = progress.add_task("Analyzing duplicate files...", total=None)

        # Analyze duplicate files
        result = analyze_duplicate_files(directory)

        # Get duplicate sets
        progress.update(task, description="Finding duplicate sets...")
        duplicate_sets = get_duplicate_sets(directory)

    # Show summary
    print_subheader("Summary")
    print_info(f"Total duplicate sets: {result['total_duplicate_sets']}")
    print_info(f"Total duplicate files: {result['total_duplicate_files']}")
    print_info(f"Total wasted space: {result['total_wasted_space']}")

    # Show duplicate sets
    print_subheader("Duplicate Sets")

    # Show each duplicate set
    for i, dup_set in enumerate(duplicate_sets, 1):
        print_subheader(f"Duplicate Set {i}")
        print_info(f"File size: {dup_set['file_size']}")
        print_info(f"Number of duplicates: {dup_set['count']}")
        print_info(f"Wasted space: {dup_set['wasted_space']}")

        # Create table
        table = create_table("Files", ["Path", "Size"])

        # Add rows
        for file_info in dup_set["files"]:
            table.add_row(
                file_info["path"],
                file_info["size"]
            )

        # Display table
        display_table(table)


def clean_temp_files():
    """Clean temporary files."""
    print_header("Clean Temporary Files")

    options = [
        "Clean system temporary files",
        "Clean browser caches",
        "Clean package manager caches",
        "Clean all temporary files",
        "Back to main menu"
    ]

    choice = display_menu("Select cleaning option:", options)

    if choice == 4:  # Back to main menu
        return

    # Confirm action
    if not confirm_action("Are you sure you want to clean these files?", default=False):
        print_info("Operation cancelled.")
        return

    # Create progress bar
    with create_progress_bar() as progress:
        task = progress.add_task("Cleaning files...", total=None)

        # Define callback for progress updates
        def update_progress(file_path):
            progress.update(task, description=f"Cleaning: {os.path.basename(file_path)}")

        # Clean based on choice
        system_result = None
        browser_result = None
        package_result = None

        if choice == 0 or choice == 3:  # System temp files or All
            progress.update(task, description="Cleaning system temporary files...")
            system_result = clean_system_temp_files(callback=update_progress)

        if choice == 1 or choice == 3:  # Browser caches or All
            progress.update(task, description="Cleaning browser caches...")
            browser_result = clean_browser_caches(callback=update_progress)

        if choice == 2 or choice == 3:  # Package caches or All
            progress.update(task, description="Cleaning package caches...")
            package_result = clean_package_caches(callback=update_progress)

    # Display results
    if system_result:
        print_success(f"Cleaned {system_result['total_count']} system temporary files ({system_result['total_size']})")

    if browser_result:
        print_success(f"Cleaned {browser_result['total_count']} browser cache files ({browser_result['total_size']})")

    if package_result:
        print_success(f"Cleaned {package_result['total_count']} package cache files ({package_result['total_size']})")

    print_success("Temporary files cleaning completed!")


def clean_large_files_menu():
    """Clean large files menu option."""
    print_header("Clean Large Files")

    # Get directory to analyze
    directory = click.prompt("Enter directory path to analyze", default=os.path.expanduser("~"))

    if not os.path.exists(directory):
        print_error(f"Directory '{directory}' does not exist.")
        return

    # Get minimum file size
    min_size_str = click.prompt("Enter minimum file size to consider (e.g., 100MB)", default="100MB")

    try:
        from cleanipy.utils.size_utils import parse_size
        min_size_bytes = parse_size(min_size_str)
    except ValueError:
        print_error(f"Invalid size format: {min_size_str}")
        return

    # Create progress bar for finding files
    with create_progress_bar() as progress:
        task = progress.add_task("Finding large files...", total=None)

        # Find large files
        large_files = find_large_files(directory, min_size_bytes)

    if not large_files:
        print_info(f"No files larger than {min_size_str} found.")
        return

    # Create table
    table = create_table("Large Files", ["#", "Path", "Size"])

    # Add rows
    for i, file_info in enumerate(large_files, 1):
        table.add_row(
            str(i),
            file_info["path"],
            file_info["size"]
        )

    # Display table
    display_table(table)

    # Ask which files to clean
    print_info("Enter the numbers of files to clean (comma-separated), 'all' to clean all, or 'cancel' to cancel:")
    choice = input("> ").strip().lower()

    if choice == "cancel":
        print_info("Operation cancelled.")
        return

    # Determine files to clean
    files_to_clean = []
    if choice == "all":
        files_to_clean = [file_info["path"] for file_info in large_files]
    else:
        try:
            indices = [int(idx.strip()) - 1 for idx in choice.split(",")]
            files_to_clean = [large_files[idx]["path"] for idx in indices if 0 <= idx < len(large_files)]
        except (ValueError, IndexError):
            print_error("Invalid input.")
            return

    if not files_to_clean:
        print_info("No files selected for cleaning.")
        return

    # Confirm action
    if not confirm_action(f"Are you sure you want to clean {len(files_to_clean)} files?", default=False):
        print_info("Operation cancelled.")
        return

    # Create a new progress bar for cleaning files
    with create_progress_bar() as progress:
        task = progress.add_task("Cleaning large files...", total=None)

        # Define callback for progress updates
        def update_progress(file_path):
            progress.update(task, description=f"Cleaning: {os.path.basename(file_path)}")

        # Clean files
        result = clean_large_files(directory, file_paths=files_to_clean, callback=update_progress)

    print_success(f"Cleaned {result['total_count']} files ({result['total_size']})")


def clean_duplicates():
    """Clean duplicate files."""
    print_header("Clean Duplicate Files")

    # Get directory to analyze
    directory = click.prompt("Enter directory path to analyze", default=os.path.expanduser("~"))

    if not os.path.exists(directory):
        print_error(f"Directory '{directory}' does not exist.")
        return

    # Create progress bar for analysis
    with create_progress_bar() as progress:
        task = progress.add_task("Analyzing duplicate files...", total=None)

        # Analyze duplicate files
        result = analyze_duplicate_files(directory)

    if result["total_duplicate_sets"] == 0:
        print_info("No duplicate files found.")
        return

    # Show summary
    print_subheader("Summary")
    print_info(f"Total duplicate sets: {result['total_duplicate_sets']}")
    print_info(f"Total duplicate files: {result['total_duplicate_files']}")
    print_info(f"Total wasted space: {result['total_wasted_space']}")

    # Ask for cleaning method
    options = [
        "Delete duplicate files (keep newest)",
        "Delete duplicate files (keep oldest)",
        "Replace with hard links",
        "Replace with symbolic links",
        "Cancel"
    ]

    choice = display_menu("Select cleaning method:", options)

    if choice == 4:  # Cancel
        print_info("Operation cancelled.")
        return

    # Confirm action
    if not confirm_action("Are you sure you want to clean duplicate files?", default=False):
        print_info("Operation cancelled.")
        return

    # Create a new progress bar for cleaning
    with create_progress_bar() as progress:
        task = progress.add_task("Processing duplicate files...", total=None)

        # Define callback for progress updates
        def update_progress(file_path):
            progress.update(task, description=f"Processing: {os.path.basename(file_path)}")

        # Clean based on choice
        if choice == 0:  # Delete (keep newest)
            progress.update(task, description="Cleaning duplicate files (keeping newest)...")
            clean_result = clean_duplicate_files(directory, result["duplicates"], keep_newest=True, callback=update_progress)
        elif choice == 1:  # Delete (keep oldest)
            progress.update(task, description="Cleaning duplicate files (keeping oldest)...")
            clean_result = clean_duplicate_files(directory, result["duplicates"], keep_newest=False, callback=update_progress)
        elif choice == 2:  # Hard links
            progress.update(task, description="Replacing with hard links...")
            clean_result = replace_duplicates_with_hardlinks(directory, result["duplicates"], callback=update_progress)
        elif choice == 3:  # Symbolic links
            progress.update(task, description="Replacing with symbolic links...")
            clean_result = replace_duplicates_with_symlinks(directory, result["duplicates"], callback=update_progress)

    print_success(f"Processed {clean_result['total_count']} files ({clean_result['total_size']})")


def main():
    """Main function."""
    while True:
        print_header("CleanIPy - Storage Cleaning Utility")

        options = [
            "Show disk usage",
            "Analyze directory",
            "Analyze temporary files",
            "Analyze duplicate files",
            "Clean temporary files",
            "Clean large files",
            "Clean duplicate files",
            "Exit"
        ]

        choice = display_menu("Main Menu", options)

        if choice == 0:
            show_disk_usage()
        elif choice == 1:
            analyze_directory()
        elif choice == 2:
            analyze_temp_files()
        elif choice == 3:
            analyze_duplicates()
        elif choice == 4:
            clean_temp_files()
        elif choice == 5:
            clean_large_files_menu()
        elif choice == 6:
            clean_duplicates()
        elif choice == 7:
            print_info("Exiting CleanIPy. Goodbye!")
            sys.exit(0)

        # Pause before returning to menu
        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

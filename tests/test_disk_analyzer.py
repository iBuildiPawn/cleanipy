"""
Tests for disk analyzer functions.
"""
import os
import tempfile
import unittest
from pathlib import Path

from cleanipy.analyzers.disk_analyzer import (
    get_disk_usage, get_directory_tree_size, find_large_files, get_file_types_summary
)


class TestDiskAnalyzer(unittest.TestCase):
    """Test disk analyzer functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Create some test files of different sizes and types
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_test_files(self):
        """Create test files of different sizes and types."""
        # Create a directory structure
        self.dirs = {
            "dir1": os.path.join(self.test_dir, "dir1"),
            "dir2": os.path.join(self.test_dir, "dir2"),
            "subdir1": os.path.join(self.test_dir, "dir1", "subdir1"),
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Create files of different sizes and types
        self.files = {
            "small_txt": {
                "path": os.path.join(self.dirs["dir1"], "small.txt"),
                "size": 1024,  # 1 KB
                "content": "A" * 1024
            },
            "medium_txt": {
                "path": os.path.join(self.dirs["dir1"], "medium.txt"),
                "size": 10 * 1024,  # 10 KB
                "content": "B" * (10 * 1024)
            },
            "large_txt": {
                "path": os.path.join(self.dirs["dir2"], "large.txt"),
                "size": 100 * 1024,  # 100 KB
                "content": "C" * (100 * 1024)
            },
            "small_log": {
                "path": os.path.join(self.dirs["dir2"], "small.log"),
                "size": 2 * 1024,  # 2 KB
                "content": "D" * (2 * 1024)
            },
            "medium_log": {
                "path": os.path.join(self.dirs["subdir1"], "medium.log"),
                "size": 20 * 1024,  # 20 KB
                "content": "E" * (20 * 1024)
            }
        }
        
        # Write the files
        for file_info in self.files.values():
            with open(file_info["path"], "w") as f:
                f.write(file_info["content"])

    def test_get_disk_usage(self):
        """Test get_disk_usage function."""
        # This function uses psutil to get disk usage, so we just check if it returns data
        disk_info = get_disk_usage()
        self.assertIsInstance(disk_info, list)
        
        # There should be at least one disk
        self.assertGreater(len(disk_info), 0)
        
        # Check if the first disk has the expected keys
        first_disk = disk_info[0]
        expected_keys = ["device", "mountpoint", "filesystem", "total", "used", "free", "percent"]
        for key in expected_keys:
            self.assertIn(key, first_disk)

    def test_get_directory_tree_size(self):
        """Test get_directory_tree_size function."""
        # Get directory tree size with depth 1
        dir_sizes = get_directory_tree_size(self.test_dir, depth=1)
        self.assertIsInstance(dir_sizes, list)
        
        # There should be 2 directories at depth 1
        self.assertEqual(len(dir_sizes), 2)
        
        # Check if the directories have the expected keys
        for dir_info in dir_sizes:
            self.assertIn("path", dir_info)
            self.assertIn("size_bytes", dir_info)
            self.assertIn("size", dir_info)
        
        # Get directory tree size with depth 2
        dir_sizes = get_directory_tree_size(self.test_dir, depth=2)
        
        # There should be more directories at depth 2
        self.assertGreater(len(dir_sizes), 2)
        
        # Test with non-existent directory
        dir_sizes = get_directory_tree_size(os.path.join(self.test_dir, "nonexistent"))
        self.assertEqual(len(dir_sizes), 0)

    def test_find_large_files(self):
        """Test find_large_files function."""
        # Find files larger than 50 KB
        large_files = find_large_files(self.test_dir, min_size_bytes=50 * 1024)
        self.assertIsInstance(large_files, list)
        
        # There should be 1 file larger than 50 KB
        self.assertEqual(len(large_files), 1)
        
        # Check if the file has the expected keys
        large_file = large_files[0]
        self.assertIn("path", large_file)
        self.assertIn("size_bytes", large_file)
        self.assertIn("size", large_file)
        
        # The file should be the large.txt file
        self.assertEqual(os.path.basename(large_file["path"]), "large.txt")
        
        # Find files larger than 5 KB
        large_files = find_large_files(self.test_dir, min_size_bytes=5 * 1024)
        
        # There should be 3 files larger than 5 KB
        self.assertEqual(len(large_files), 3)
        
        # Find files larger than 1 MB (there should be none)
        large_files = find_large_files(self.test_dir, min_size_bytes=1024 * 1024)
        self.assertEqual(len(large_files), 0)

    def test_get_file_types_summary(self):
        """Test get_file_types_summary function."""
        # Get file types summary
        file_types = get_file_types_summary(self.test_dir)
        self.assertIsInstance(file_types, dict)
        
        # There should be 2 file types: .txt and .log
        self.assertEqual(len(file_types), 2)
        
        # Check if the file types have the expected keys
        for ext, info in file_types.items():
            self.assertIn("count", info)
            self.assertIn("total_size_bytes", info)
            self.assertIn("total_size", info)
        
        # Check .txt files
        self.assertIn(".txt", file_types)
        self.assertEqual(file_types[".txt"]["count"], 3)
        
        # Check .log files
        self.assertIn(".log", file_types)
        self.assertEqual(file_types[".log"]["count"], 2)
        
        # Total size of .txt files should be greater than .log files
        self.assertGreater(
            file_types[".txt"]["total_size_bytes"],
            file_types[".log"]["total_size_bytes"]
        )


if __name__ == "__main__":
    unittest.main()

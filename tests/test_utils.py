"""
Tests for utility functions.
"""
import os
import tempfile
import unittest
from pathlib import Path

from cleanipy.utils.file_utils import (
    get_file_size, get_directory_size, get_file_hash,
    find_files_by_extension, find_files_by_pattern, is_file_older_than
)
from cleanipy.utils.size_utils import (
    format_size, parse_size, get_size_distribution
)


class TestFileUtils(unittest.TestCase):
    """Test file utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Create some test files
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content {i}" * 100)  # Write some content
            self.test_files.append(file_path)

        # Create a subdirectory with files
        self.sub_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.sub_dir, exist_ok=True)
        for i in range(2):
            file_path = os.path.join(self.sub_dir, f"sub_file_{i}.log")
            with open(file_path, "w") as f:
                f.write(f"Subdir content {i}" * 50)
            self.test_files.append(file_path)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_get_file_size(self):
        """Test get_file_size function."""
        # Test with existing file
        size = get_file_size(self.test_files[0])
        self.assertGreater(size, 0)

        # Test with non-existent file
        size = get_file_size(os.path.join(self.test_dir, "nonexistent.txt"))
        self.assertEqual(size, 0)

    def test_get_directory_size(self):
        """Test get_directory_size function."""
        # Test with existing directory
        size = get_directory_size(self.test_dir)
        self.assertGreater(size, 0)

        # Test with subdirectory
        size_subdir = get_directory_size(self.sub_dir)
        self.assertGreater(size_subdir, 0)
        self.assertLess(size_subdir, size)  # Subdirectory should be smaller

        # Test with non-existent directory
        size = get_directory_size(os.path.join(self.test_dir, "nonexistent"))
        self.assertEqual(size, 0)

    def test_get_file_hash(self):
        """Test get_file_hash function."""
        # Test with existing file
        hash1 = get_file_hash(self.test_files[0])
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA-256 hash is 64 characters

        # Create a duplicate file
        dup_file = os.path.join(self.test_dir, "duplicate.txt")
        with open(self.test_files[0], "rb") as src, open(dup_file, "wb") as dst:
            dst.write(src.read())

        # Hash should be the same for identical content
        hash2 = get_file_hash(dup_file)
        self.assertEqual(hash1, hash2)

        # Test with non-existent file
        hash3 = get_file_hash(os.path.join(self.test_dir, "nonexistent.txt"))
        self.assertEqual(hash3, "")

    def test_find_files_by_extension(self):
        """Test find_files_by_extension function."""
        # Find .txt files
        txt_files = list(find_files_by_extension(self.test_dir, [".txt"]))
        self.assertEqual(len(txt_files), 3)

        # Find .log files
        log_files = list(find_files_by_extension(self.test_dir, [".log"]))
        self.assertEqual(len(log_files), 2)

        # Find both .txt and .log files
        all_files = list(find_files_by_extension(self.test_dir, [".txt", ".log"]))
        self.assertEqual(len(all_files), 5)

    def test_find_files_by_pattern(self):
        """Test find_files_by_pattern function."""
        # Find files matching pattern
        pattern_files = list(find_files_by_pattern(self.test_dir, "*.txt"))
        self.assertEqual(len(pattern_files), 3)

        # Find files in subdirectory
        subdir_files = list(find_files_by_pattern(self.test_dir, "sub*.log"))
        self.assertEqual(len(subdir_files), 2)

    def test_is_file_older_than(self):
        """Test is_file_older_than function."""
        # All files are new, so they shouldn't be older than 30 days
        for file_path in self.test_files:
            self.assertFalse(is_file_older_than(file_path, 30))

        # Files should be newer than 0 days
        for file_path in self.test_files:
            self.assertFalse(is_file_older_than(file_path, 0))

        # Test with non-existent file
        self.assertFalse(is_file_older_than(os.path.join(self.test_dir, "nonexistent.txt"), 30))


class TestSizeUtils(unittest.TestCase):
    """Test size utility functions."""

    def test_format_size(self):
        """Test format_size function."""
        # Test with various sizes
        self.assertEqual(format_size(0), "0 B")
        self.assertEqual(format_size(1023), "1023 B")
        self.assertEqual(format_size(1024), "1.00 KB")
        self.assertEqual(format_size(1024 * 1024), "1.00 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024), "1.00 GB")
        self.assertEqual(format_size(1024 * 1024 * 1024 * 1024), "1.00 TB")

    def test_parse_size(self):
        """Test parse_size function."""
        # Test with various size strings
        self.assertEqual(parse_size("0 B"), 0)
        self.assertEqual(parse_size("1023 B"), 1023)
        self.assertEqual(parse_size("1 KB"), 1024)
        self.assertEqual(parse_size("1.5 KB"), 1536)
        self.assertEqual(parse_size("1 MB"), 1024 * 1024)
        self.assertEqual(parse_size("1 GB"), 1024 * 1024 * 1024)
        self.assertEqual(parse_size("1 TB"), 1024 * 1024 * 1024 * 1024)

        # Test with invalid format
        with self.assertRaises(ValueError):
            parse_size("invalid")

        # Test with unknown unit
        with self.assertRaises(ValueError):
            parse_size("1 XB")

    def test_get_size_distribution(self):
        """Test get_size_distribution function."""
        # Create a list of file sizes
        sizes = [
            500,                    # < 1 KB
            1500,                   # 1 KB - 1 MB
            2 * 1024 * 1024,        # 1 MB - 10 MB
            50 * 1024 * 1024,       # 10 MB - 100 MB
            500 * 1024 * 1024,      # 100 MB - 1 GB
            2 * 1024 * 1024 * 1024  # > 1 GB
        ]

        # Get distribution
        distribution = get_size_distribution(sizes)

        # Check counts
        self.assertEqual(distribution["< 1 KB"], 1)
        self.assertEqual(distribution["1 KB - 1 MB"], 1)
        self.assertEqual(distribution["1 MB - 10 MB"], 1)
        self.assertEqual(distribution["10 MB - 100 MB"], 1)
        self.assertEqual(distribution["100 MB - 1 GB"], 1)
        self.assertEqual(distribution["> 1 GB"], 1)


if __name__ == "__main__":
    unittest.main()

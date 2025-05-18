"""
Tests for duplicate file cleaner functions.
"""
import os
import tempfile
import unittest
import time
from unittest.mock import MagicMock, patch
import send2trash

from cleanipy.cleaners.duplicate_cleaner import (
    clean_duplicate_files, replace_duplicates_with_hardlinks, replace_duplicates_with_symlinks
)


class TestDuplicateCleaner(unittest.TestCase):
    """Test duplicate file cleaner functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Create test files with duplicates
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_test_files(self):
        """Create test files with duplicates."""
        # Create directories
        self.dirs = {
            "dir1": os.path.join(self.test_dir, "dir1"),
            "dir2": os.path.join(self.test_dir, "dir2"),
        }

        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

        # Create duplicate files (same content, different names)
        self.duplicate_sets = {}

        # First duplicate set
        self.duplicate_sets["set1"] = []
        for i in range(3):
            file_path = os.path.join(self.dirs["dir1"], f"dup1_{i}.txt")
            with open(file_path, "w") as f:
                f.write("Duplicate content 1" * 100)
            self.duplicate_sets["set1"].append(file_path)
            # Add a small delay to ensure different timestamps
            time.sleep(0.1)

        # Second duplicate set
        self.duplicate_sets["set2"] = []
        for i in range(2):
            file_path = os.path.join(self.dirs["dir2"], f"dup2_{i}.txt")
            with open(file_path, "w") as f:
                f.write("Duplicate content 2" * 200)
            self.duplicate_sets["set2"].append(file_path)
            # Add a small delay to ensure different timestamps
            time.sleep(0.1)

    def create_mock_duplicates(self):
        """Create a mock duplicates dictionary for testing."""
        # Create a mock duplicates dictionary that matches the format
        # returned by find_duplicate_files_by_content
        duplicates = {}

        # First duplicate set
        hash1 = "hash1"
        duplicates[hash1] = []
        for file_path in self.duplicate_sets["set1"]:
            size = os.path.getsize(file_path)
            duplicates[hash1].append({
                "path": file_path,
                "size_bytes": size,
                "size": f"{size} bytes"
            })

        # Second duplicate set
        hash2 = "hash2"
        duplicates[hash2] = []
        for file_path in self.duplicate_sets["set2"]:
            size = os.path.getsize(file_path)
            duplicates[hash2].append({
                "path": file_path,
                "size_bytes": size,
                "size": f"{size} bytes"
            })

        return duplicates

    @patch('os.path.getmtime')
    def test_clean_duplicate_files(self, mock_getmtime):
        """Test clean_duplicate_files function."""
        # Mock getmtime to avoid file not found errors
        mock_getmtime.return_value = time.time()

        # Create a mock duplicates dictionary
        duplicates = self.create_mock_duplicates()

        # Create a callback mock
        callback_mock = MagicMock()

        # Mock the send2trash function to avoid actually deleting files
        with patch('send2trash.send2trash'):
            # Clean duplicate files (keep newest)
            result = clean_duplicate_files(
                self.test_dir,
                duplicates=duplicates,
                keep_newest=True,
                callback=callback_mock
            )
            self.assertIsInstance(result, dict)

            # Check if the result has the expected keys
            expected_keys = [
                "total_size_bytes", "total_count", "details", "total_size"
            ]
            for key in expected_keys:
                self.assertIn(key, result)

            # The callback should have been called for each file
            self.assertGreater(callback_mock.call_count, 0)

            # Reset mocks
            callback_mock.reset_mock()

            # Clean duplicate files (keep oldest)
            result = clean_duplicate_files(
                self.test_dir,
                duplicates=duplicates,
                keep_newest=False,
                callback=callback_mock
            )

            # The callback should have been called for each file
            self.assertGreater(callback_mock.call_count, 0)

    def test_replace_duplicates_with_hardlinks(self):
        """Test replace_duplicates_with_hardlinks function."""
        # Create a mock duplicates dictionary
        duplicates = self.create_mock_duplicates()

        # Create a callback mock
        callback_mock = MagicMock()

        # Replace duplicates with hard links (keep newest)
        result = replace_duplicates_with_hardlinks(
            self.test_dir,
            duplicates=duplicates,
            keep_newest=True,
            callback=callback_mock
        )
        self.assertIsInstance(result, dict)

        # Check if the result has the expected keys
        expected_keys = [
            "total_size_bytes", "total_count", "details", "total_size"
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # There should be 3 files processed (2 from set1 and 1 from set2)
        self.assertEqual(result["total_count"], 3)

        # The callback should have been called 3 times
        self.assertEqual(callback_mock.call_count, 3)

        # All files should still exist
        for file_path in self.duplicate_sets["set1"]:
            self.assertTrue(os.path.exists(file_path))
        for file_path in self.duplicate_sets["set2"]:
            self.assertTrue(os.path.exists(file_path))

        # The content of all files in each set should be the same
        with open(self.duplicate_sets["set1"][0], "r") as f:
            content1 = f.read()
        for file_path in self.duplicate_sets["set1"][1:]:
            with open(file_path, "r") as f:
                self.assertEqual(f.read(), content1)

        with open(self.duplicate_sets["set2"][0], "r") as f:
            content2 = f.read()
        for file_path in self.duplicate_sets["set2"][1:]:
            with open(file_path, "r") as f:
                self.assertEqual(f.read(), content2)

    @unittest.skipIf(os.name == "nt", "Symbolic links not fully supported on Windows")
    def test_replace_duplicates_with_symlinks(self):
        """Test replace_duplicates_with_symlinks function."""
        # Create a mock duplicates dictionary
        duplicates = self.create_mock_duplicates()

        # Create a callback mock
        callback_mock = MagicMock()

        # Replace duplicates with symbolic links (keep newest)
        result = replace_duplicates_with_symlinks(
            self.test_dir,
            duplicates=duplicates,
            keep_newest=True,
            callback=callback_mock
        )
        self.assertIsInstance(result, dict)

        # Check if the result has the expected keys
        expected_keys = [
            "total_size_bytes", "total_count", "details", "total_size"
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # There should be 3 files processed (2 from set1 and 1 from set2)
        self.assertEqual(result["total_count"], 3)

        # The callback should have been called 3 times
        self.assertEqual(callback_mock.call_count, 3)

        # All files should still exist
        for file_path in self.duplicate_sets["set1"]:
            self.assertTrue(os.path.exists(file_path))
        for file_path in self.duplicate_sets["set2"]:
            self.assertTrue(os.path.exists(file_path))

        # The duplicates should be symbolic links
        for file_path in self.duplicate_sets["set1"][:-1]:
            self.assertTrue(os.path.islink(file_path))
        for file_path in self.duplicate_sets["set2"][:-1]:
            self.assertTrue(os.path.islink(file_path))

        # The newest files should not be symbolic links
        self.assertFalse(os.path.islink(self.duplicate_sets["set1"][-1]))
        self.assertFalse(os.path.islink(self.duplicate_sets["set2"][-1]))

        # The content of all files in each set should be the same
        with open(self.duplicate_sets["set1"][0], "r") as f:
            content1 = f.read()
        for file_path in self.duplicate_sets["set1"][1:]:
            with open(file_path, "r") as f:
                self.assertEqual(f.read(), content1)

        with open(self.duplicate_sets["set2"][0], "r") as f:
            content2 = f.read()
        for file_path in self.duplicate_sets["set2"][1:]:
            with open(file_path, "r") as f:
                self.assertEqual(f.read(), content2)


if __name__ == "__main__":
    unittest.main()

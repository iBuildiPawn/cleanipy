"""
Tests for disk cleaner functions.
"""
import os
import tempfile
import unittest
import time
import send2trash
from unittest.mock import MagicMock, patch

from cleanipy.cleaners.disk_cleaner import (
    clean_directory, clean_old_files, clean_large_files
)


class TestDiskCleaner(unittest.TestCase):
    """Test disk cleaner functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Create test files
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_test_files(self):
        """Create test files."""
        # Create directories
        self.dirs = {
            "clean_dir": os.path.join(self.test_dir, "clean_dir"),
            "old_files_dir": os.path.join(self.test_dir, "old_files_dir"),
            "large_files_dir": os.path.join(self.test_dir, "large_files_dir"),
        }

        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

        # Create files in clean_dir
        self.clean_dir_files = []
        for i in range(5):
            file_path = os.path.join(self.dirs["clean_dir"], f"file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}" * 100)
            self.clean_dir_files.append(file_path)

        # Create files in old_files_dir (we can't easily create old files,
        # so we'll just create regular files and mock the age check)
        self.old_files_dir_files = []
        for i in range(5):
            file_path = os.path.join(self.dirs["old_files_dir"], f"file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}" * 100)
            self.old_files_dir_files.append(file_path)

        # Create files in large_files_dir
        self.large_files_dir_files = {
            "small": os.path.join(self.dirs["large_files_dir"], "small.txt"),
            "medium": os.path.join(self.dirs["large_files_dir"], "medium.txt"),
            "large": os.path.join(self.dirs["large_files_dir"], "large.txt"),
        }

        with open(self.large_files_dir_files["small"], "w") as f:
            f.write("S" * 1024)  # 1 KB

        with open(self.large_files_dir_files["medium"], "w") as f:
            f.write("M" * (10 * 1024))  # 10 KB

        with open(self.large_files_dir_files["large"], "w") as f:
            f.write("L" * (100 * 1024))  # 100 KB

    def test_clean_directory(self):
        """Test clean_directory function."""
        # Create a callback mock
        callback_mock = MagicMock()

        # Clean the directory
        result = clean_directory(self.dirs["clean_dir"], callback=callback_mock)
        self.assertIsInstance(result, dict)

        # Check if the result has the expected keys
        expected_keys = [
            "directory", "total_size_bytes", "total_count",
            "success", "error", "total_size"
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # The directory should be the clean_dir
        self.assertEqual(result["directory"], self.dirs["clean_dir"])

        # The operation should be successful
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])

        # There should be 5 files cleaned
        self.assertEqual(result["total_count"], 5)

        # The directory should be empty now
        self.assertEqual(len(os.listdir(self.dirs["clean_dir"])), 0)

        # The callback should have been called 5 times
        self.assertEqual(callback_mock.call_count, 5)

        # Test with non-existent directory
        result = clean_directory(os.path.join(self.test_dir, "nonexistent"))
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    @patch('cleanipy.utils.file_utils.is_file_older_than')
    @patch('send2trash.send2trash')
    def test_clean_old_files(self, mock_send2trash, mock_is_file_older_than):
        """Test clean_old_files function."""
        # Mock is_file_older_than to always return True
        mock_is_file_older_than.return_value = True

        # Create a callback mock
        callback_mock = MagicMock()

        # Clean old files
        result = clean_old_files(self.dirs["old_files_dir"], min_age_days=30, callback=callback_mock)
        self.assertIsInstance(result, dict)

        # Check if the result has the expected keys
        expected_keys = [
            "directory", "total_size_bytes", "total_count",
            "success", "error", "total_size"
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # The directory should be the old_files_dir
        self.assertEqual(result["directory"], self.dirs["old_files_dir"])

        # The operation should be successful
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])

        # Test with non-existent directory
        result = clean_old_files(os.path.join(self.test_dir, "nonexistent"))
        self.assertTrue(result["success"])  # Still true because no error occurred
        self.assertIsNone(result["error"])
        self.assertEqual(result["total_count"], 0)

    def test_clean_large_files(self):
        """Test clean_large_files function."""
        # Create a callback mock
        callback_mock = MagicMock()

        # Clean files larger than 50 KB
        result = clean_large_files(self.dirs["large_files_dir"], min_size_bytes=50 * 1024, callback=callback_mock)
        self.assertIsInstance(result, dict)

        # Check if the result has the expected keys
        expected_keys = [
            "total_size_bytes", "total_count",
            "success", "error", "total_size"
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # The operation should be successful
        self.assertTrue(result["success"])
        self.assertIsNone(result["error"])

        # There should be 1 file cleaned (the large file)
        self.assertEqual(result["total_count"], 1)

        # The large file should be gone
        self.assertFalse(os.path.exists(self.large_files_dir_files["large"]))

        # The small and medium files should still exist
        self.assertTrue(os.path.exists(self.large_files_dir_files["small"]))
        self.assertTrue(os.path.exists(self.large_files_dir_files["medium"]))

        # The callback should have been called once
        self.assertEqual(callback_mock.call_count, 1)

        # Test with specific file paths
        callback_mock.reset_mock()
        result = clean_large_files(
            self.dirs["large_files_dir"],
            file_paths=[self.large_files_dir_files["medium"]],
            callback=callback_mock
        )

        # There should be 1 file cleaned (the medium file)
        self.assertEqual(result["total_count"], 1)

        # The medium file should be gone
        self.assertFalse(os.path.exists(self.large_files_dir_files["medium"]))

        # The small file should still exist
        self.assertTrue(os.path.exists(self.large_files_dir_files["small"]))

        # The callback should have been called once
        self.assertEqual(callback_mock.call_count, 1)

        # Test with non-existent directory
        result = clean_large_files(os.path.join(self.test_dir, "nonexistent"))
        self.assertTrue(result["success"])  # Still true because no error occurred
        self.assertIsNone(result["error"])
        self.assertEqual(result["total_count"], 0)


if __name__ == "__main__":
    unittest.main()

"""
Tests for temporary file analyzer functions.
"""
import os
import tempfile
import unittest
import platform
from datetime import datetime, timedelta

from cleanipy.analyzers.temp_analyzer import (
    get_system_temp_dirs, get_browser_cache_dirs, get_package_cache_dirs, analyze_temp_files
)


class TestTempAnalyzer(unittest.TestCase):
    """Test temporary file analyzer functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory to simulate a temp directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # Create some test files with different ages
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_test_files(self):
        """Create test files with different ages."""
        # Create files with current timestamp
        self.new_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"new_file_{i}.tmp")
            with open(file_path, "w") as f:
                f.write(f"New content {i}" * 100)
            self.new_files.append(file_path)
        
        # We can't easily create files with old timestamps in a reliable way
        # for testing, so we'll just create files and check if the analyzer
        # correctly identifies them as new

    def test_get_system_temp_dirs(self):
        """Test get_system_temp_dirs function."""
        # Get system temp directories
        temp_dirs = get_system_temp_dirs()
        self.assertIsInstance(temp_dirs, list)
        
        # There should be at least one temp directory
        self.assertGreater(len(temp_dirs), 0)
        
        # The Python temp directory should be in the list
        python_temp = tempfile.gettempdir()
        self.assertIn(python_temp, temp_dirs)
        
        # Check OS-specific temp directories
        system = platform.system()
        if system == "Windows":
            # Windows should have %TEMP% directory
            self.assertIn(os.path.expandvars("%TEMP%"), temp_dirs)
        elif system == "Darwin":
            # macOS should have /tmp
            self.assertIn("/tmp", temp_dirs)
        elif system == "Linux":
            # Linux should have /tmp
            self.assertIn("/tmp", temp_dirs)

    def test_get_browser_cache_dirs(self):
        """Test get_browser_cache_dirs function."""
        # Get browser cache directories
        cache_dirs = get_browser_cache_dirs()
        self.assertIsInstance(cache_dirs, list)
        
        # The result may be empty if no browsers are installed
        # or if the cache directories don't exist
        # So we just check if the function runs without errors

    def test_get_package_cache_dirs(self):
        """Test get_package_cache_dirs function."""
        # Get package cache directories
        cache_dirs = get_package_cache_dirs()
        self.assertIsInstance(cache_dirs, list)
        
        # The result may be empty if no package managers are installed
        # or if the cache directories don't exist
        # So we just check if the function runs without errors

    def test_analyze_temp_files(self):
        """Test analyze_temp_files function."""
        # Analyze the test directory
        result = analyze_temp_files(self.test_dir)
        self.assertIsInstance(result, dict)
        
        # Check if the result has the expected keys
        expected_keys = [
            "directory", "total_size_bytes", "total_count",
            "old_files_size_bytes", "old_files_count", "old_files",
            "total_size", "old_files_size"
        ]
        for key in expected_keys:
            self.assertIn(key, result)
        
        # The directory should be the test directory
        self.assertEqual(result["directory"], self.test_dir)
        
        # There should be 3 files in total
        self.assertEqual(result["total_count"], 3)
        
        # All files are new, so there should be 0 old files
        self.assertEqual(result["old_files_count"], 0)
        self.assertEqual(len(result["old_files"]), 0)
        
        # Test with non-existent directory
        result = analyze_temp_files(os.path.join(self.test_dir, "nonexistent"))
        self.assertEqual(result["total_count"], 0)
        self.assertEqual(result["old_files_count"], 0)


if __name__ == "__main__":
    unittest.main()

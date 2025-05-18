"""
Tests for duplicate file analyzer functions.
"""
import os
import tempfile
import unittest
import time

from cleanipy.analyzers.duplicate_analyzer import (
    find_duplicate_files_by_size, find_duplicate_files_by_content,
    analyze_duplicate_files, get_duplicate_sets
)


class TestDuplicateAnalyzer(unittest.TestCase):
    """Test duplicate file analyzer functions."""

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
        
        # Create unique files
        self.unique_files = {
            "unique1": {
                "path": os.path.join(self.dirs["dir1"], "unique1.txt"),
                "content": "Unique content 1" * 100
            },
            "unique2": {
                "path": os.path.join(self.dirs["dir2"], "unique2.txt"),
                "content": "Unique content 2" * 100
            }
        }
        
        # Create duplicate files (same content, different names)
        self.duplicate_sets = {
            "set1": [
                {
                    "path": os.path.join(self.dirs["dir1"], "dup1_1.txt"),
                    "content": "Duplicate content 1" * 100
                },
                {
                    "path": os.path.join(self.dirs["dir2"], "dup1_2.txt"),
                    "content": "Duplicate content 1" * 100
                }
            ],
            "set2": [
                {
                    "path": os.path.join(self.dirs["dir1"], "dup2_1.txt"),
                    "content": "Duplicate content 2" * 200
                },
                {
                    "path": os.path.join(self.dirs["dir2"], "dup2_2.txt"),
                    "content": "Duplicate content 2" * 200
                },
                {
                    "path": os.path.join(self.dirs["dir1"], "dup2_3.txt"),
                    "content": "Duplicate content 2" * 200
                }
            ]
        }
        
        # Create files with same size but different content
        self.same_size_files = {
            "size1_1": {
                "path": os.path.join(self.dirs["dir1"], "size1_1.txt"),
                "content": "A" * 1024
            },
            "size1_2": {
                "path": os.path.join(self.dirs["dir2"], "size1_2.txt"),
                "content": "B" * 1024
            }
        }
        
        # Write all files
        for file_info in self.unique_files.values():
            with open(file_info["path"], "w") as f:
                f.write(file_info["content"])
        
        for dup_set in self.duplicate_sets.values():
            for file_info in dup_set:
                with open(file_info["path"], "w") as f:
                    f.write(file_info["content"])
        
        for file_info in self.same_size_files.values():
            with open(file_info["path"], "w") as f:
                f.write(file_info["content"])
        
        # Add a small delay between file creations to ensure different timestamps
        time.sleep(0.1)

    def test_find_duplicate_files_by_size(self):
        """Test find_duplicate_files_by_size function."""
        # Find duplicate files by size
        size_dict = find_duplicate_files_by_size(self.test_dir)
        self.assertIsInstance(size_dict, dict)
        
        # There should be at least 2 sets of files with the same size
        self.assertGreaterEqual(len(size_dict), 2)
        
        # Check if the same_size_files are detected
        same_size_paths = [file_info["path"] for file_info in self.same_size_files.values()]
        found = False
        for size, files in size_dict.items():
            if set(files) == set(same_size_paths):
                found = True
                break
        self.assertTrue(found, "Same size files not detected correctly")
        
        # Check if the duplicate_sets are detected
        for dup_set in self.duplicate_sets.values():
            dup_paths = [file_info["path"] for file_info in dup_set]
            found = False
            for size, files in size_dict.items():
                if set(dup_paths).issubset(set(files)):
                    found = True
                    break
            self.assertTrue(found, "Duplicate files not detected correctly by size")
        
        # Test with minimum size filter
        large_size = len(self.duplicate_sets["set2"][0]["content"]) - 1
        size_dict = find_duplicate_files_by_size(self.test_dir, min_size=large_size)
        
        # Only the larger duplicate set should be detected
        self.assertGreaterEqual(len(size_dict), 1)
        
        # The smaller duplicate set should not be detected
        small_dup_paths = [file_info["path"] for file_info in self.duplicate_sets["set1"]]
        for size, files in size_dict.items():
            self.assertFalse(set(small_dup_paths).issubset(set(files)),
                            "Small duplicate files should not be detected with size filter")

    def test_find_duplicate_files_by_content(self):
        """Test find_duplicate_files_by_content function."""
        # Find duplicate files by content
        hash_dict = find_duplicate_files_by_content(self.test_dir)
        self.assertIsInstance(hash_dict, dict)
        
        # There should be 2 sets of duplicate files
        self.assertEqual(len(hash_dict), 2)
        
        # Check if the duplicate_sets are detected
        for dup_set in self.duplicate_sets.values():
            dup_paths = [file_info["path"] for file_info in dup_set]
            found = False
            for hash_val, files in hash_dict.items():
                file_paths = [file_info["path"] for file_info in files]
                if set(dup_paths) == set(file_paths):
                    found = True
                    break
            self.assertTrue(found, "Duplicate files not detected correctly by content")
        
        # The same_size_files should not be detected as duplicates
        same_size_paths = [file_info["path"] for file_info in self.same_size_files.values()]
        for hash_val, files in hash_dict.items():
            file_paths = [file_info["path"] for file_info in files]
            self.assertFalse(set(same_size_paths) == set(file_paths),
                            "Same size files incorrectly detected as duplicates")

    def test_analyze_duplicate_files(self):
        """Test analyze_duplicate_files function."""
        # Analyze duplicate files
        result = analyze_duplicate_files(self.test_dir)
        self.assertIsInstance(result, dict)
        
        # Check if the result has the expected keys
        expected_keys = [
            "directory", "total_duplicate_sets", "total_duplicate_files",
            "total_wasted_space_bytes", "total_wasted_space", "duplicates"
        ]
        for key in expected_keys:
            self.assertIn(key, result)
        
        # The directory should be the test directory
        self.assertEqual(result["directory"], self.test_dir)
        
        # There should be 2 duplicate sets
        self.assertEqual(result["total_duplicate_sets"], 2)
        
        # There should be 3 duplicate files (2 from set1 - 1 and 3 from set2 - 1)
        self.assertEqual(result["total_duplicate_files"], 3)
        
        # Test with minimum size filter
        large_size = len(self.duplicate_sets["set2"][0]["content"]) - 1
        result = analyze_duplicate_files(self.test_dir, min_size=large_size)
        
        # Only the larger duplicate set should be detected
        self.assertEqual(result["total_duplicate_sets"], 1)
        self.assertEqual(result["total_duplicate_files"], 2)

    def test_get_duplicate_sets(self):
        """Test get_duplicate_sets function."""
        # Get duplicate sets
        dup_sets = get_duplicate_sets(self.test_dir)
        self.assertIsInstance(dup_sets, list)
        
        # There should be 2 duplicate sets
        self.assertEqual(len(dup_sets), 2)
        
        # Check if the duplicate sets have the expected keys
        for dup_set in dup_sets:
            expected_keys = [
                "hash", "files", "count", "wasted_space_bytes",
                "wasted_space", "file_size"
            ]
            for key in expected_keys:
                self.assertIn(key, dup_set)
        
        # The larger duplicate set should be first (sorted by wasted space)
        self.assertGreater(dup_sets[0]["count"], dup_sets[1]["count"])
        
        # Test with limit
        dup_sets = get_duplicate_sets(self.test_dir, limit=1)
        self.assertEqual(len(dup_sets), 1)
        
        # Test with minimum size filter
        large_size = len(self.duplicate_sets["set2"][0]["content"]) - 1
        dup_sets = get_duplicate_sets(self.test_dir, min_size=large_size)
        self.assertEqual(len(dup_sets), 1)


if __name__ == "__main__":
    unittest.main()

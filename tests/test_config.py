import os
import sys
import unittest

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import PROJECT_ROOT, VECTORSTORE_PATH

class TestConfig(unittest.TestCase):
    def test_project_root_exists(self):
        """Verify PROJECT_ROOT is a valid path."""
        self.assertTrue(os.path.exists(PROJECT_ROOT), "PROJECT_ROOT should ensure the path exists")

    def test_paths_structure(self):
        """Verify vectorstore path structure is logical."""
        expected_suffix = os.path.join("vectorstore", "db_faiss")
        self.assertTrue(VECTORSTORE_PATH.endswith(expected_suffix), "VECTORSTORE_PATH should point to db_faiss")

if __name__ == '__main__':
    unittest.main()

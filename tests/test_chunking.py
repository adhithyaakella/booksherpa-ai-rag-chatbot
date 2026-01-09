import unittest
from langchain_core.documents import Document
import sys
import os

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingest import enrich_metadata

class TestChunking(unittest.TestCase):
    def test_chapter_recognition(self):
        """Test if chapters are correctly detected in chunk text."""
        
        # Sample chunks
        chunks = [
            Document(page_content="Chapter 1: The Beginning\nThis is the start.", metadata={}),
            Document(page_content="Some intro text...\nChapter 2: The Middle", metadata={}),
            Document(page_content="Just random text with no chapter.", metadata={})
        ]
        
        enriched = enrich_metadata(chunks)
        
        # Check Chapter 1 (Regex captures 'Chapter 1')
        self.assertEqual(enriched[0].metadata["chapter"], "Chapter 1", "Should detect Chapter 1")
        
        # Check Chapter 2
        self.assertEqual(enriched[1].metadata["chapter"], "Chapter 2", "Should detect Chapter 2")
        
        # Check Default (Should match the default value in enrich_metadata)
        # Note: function uses 'current_chapter' logic, so it maintains state of previous chunks if strictly sequential,
        # but here we pass a list. The function iterates.
        # For chunk 2, it defaults to "General / Introduction" ONLY if it hasn't seen a chapter yet.
        # But wait, enrich_metadata iterates linearly.
        # Chunk 0 sets current="Chapter 1".
        # Chunk 1 sets current="Chapter 2".
        # Chunk 2 has no match, so it should keep "Chapter 2".
        
        self.assertEqual(enriched[2].metadata["chapter"], "Chapter 2", "Should inherit previous chapter")

if __name__ == '__main__':
    unittest.main()

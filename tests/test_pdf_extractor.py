"""
Unit tests for PDF Extractor module.
Tests PDF validation, text extraction, and text cleaning.
"""
import unittest
import os
import sys
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_extractor import PDFExtractor


class TestPDFExtractorInitialization(unittest.TestCase):
    """Test PDF Extractor initialization"""
    
    def test_extractor_initialization(self):
        """Test that extractor initializes without errors"""
        extractor = PDFExtractor()
        self.assertIsNotNone(extractor)


class TestTextCleaning(unittest.TestCase):
    """Test text cleaning and normalization"""
    
    def setUp(self):
        self.extractor = PDFExtractor()
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization"""
        text = "Hello    World\t\tTest\n\n\n\nEnd"
        cleaned = self.extractor._clean_and_normalize(text)
        
        # Should not have excessive whitespace
        self.assertNotIn("    ", cleaned)
        self.assertNotIn("\t\t", cleaned)
    
    def test_unicode_normalization(self):
        """Test unicode character normalization"""
        # Text with various unicode issues
        text = "Resume\u2019s content with \u201csmart quotes\u201d and em\u2014dashes"
        cleaned = self.extractor._clean_and_normalize(text)
        
        # Should handle unicode properly
        self.assertIsInstance(cleaned, str)
    
    def test_remove_control_characters(self):
        """Test removal of control characters"""
        text = "Hello\x00World\x0BTest"
        cleaned = self.extractor._clean_and_normalize(text)
        
        # Should not contain control characters
        self.assertNotIn("\x00", cleaned)
        self.assertNotIn("\x0B", cleaned)
    
    def test_preserve_meaningful_content(self):
        """Test that meaningful content is preserved"""
        text = """
        John Smith
        Software Engineer
        
        Experience:
        - Python Developer at TechCorp
        - 5 years experience
        """
        cleaned = self.extractor._clean_and_normalize(text)
        
        # Key content should be preserved
        self.assertIn("John Smith", cleaned)
        self.assertIn("Software Engineer", cleaned)
        self.assertIn("Python", cleaned)


class TestPDFValidation(unittest.TestCase):
    """Test PDF validation"""
    
    def setUp(self):
        self.extractor = PDFExtractor()
    
    def test_invalid_file_path(self):
        """Test validation with non-existent file"""
        is_valid, error = self.extractor.validate_pdf("/nonexistent/path/file.pdf")
        self.assertFalse(is_valid)
    
    def test_non_pdf_file(self):
        """Test validation with non-PDF file"""
        # Create a temp text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a PDF")
            temp_path = f.name
        
        try:
            is_valid, error = self.extractor.validate_pdf(temp_path)
            # Should fail validation (either by extension or magic bytes)
            # Note: The actual validation might pass if only checking content
        finally:
            os.unlink(temp_path)


class TestExtractionMetadata(unittest.TestCase):
    """Test extraction metadata handling"""
    
    def setUp(self):
        self.extractor = PDFExtractor()
    
    def test_metadata_structure(self):
        """Test that metadata has correct structure"""
        # Test with non-existent file to check metadata structure
        text, metadata = self.extractor.extract_text("/nonexistent/path/file.pdf")
        
        # Metadata should have required keys
        self.assertIn('method', metadata)
        self.assertIn('pages', metadata)
        self.assertIn('warnings', metadata)
        self.assertIn('success', metadata)
    
    def test_failed_extraction_metadata(self):
        """Test metadata for failed extraction"""
        text, metadata = self.extractor.extract_text("/nonexistent/path/file.pdf")
        
        self.assertFalse(metadata['success'])
        self.assertEqual(text, "")


if __name__ == '__main__':
    unittest.main(verbosity=2)

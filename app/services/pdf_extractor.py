"""
PDF Text Extraction Module
Handles PDF parsing with fallback mechanisms and Unicode normalization
"""
import re
import unicodedata
from typing import Optional, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Advanced PDF text extraction with multiple fallback methods
    and robust Unicode normalization.
    """
    
    def __init__(self):
        self.extraction_method = None
        
    def extract_text(self, pdf_path: str) -> Tuple[str, dict]:
        """
        Extract text from PDF using multiple methods with fallback.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        text = ""
        metadata = {
            'method': None,
            'pages': 0,
            'warnings': [],
            'success': False
        }
        
        # Try pdfplumber first (better for complex layouts)
        try:
            text, pages = self._extract_with_pdfplumber(pdf_path)
            if text and len(text.strip()) > 50:
                metadata['method'] = 'pdfplumber'
                metadata['pages'] = pages
                metadata['success'] = True
                logger.info(f"Successfully extracted text using pdfplumber ({pages} pages)")
            else:
                raise ValueError("Insufficient text extracted with pdfplumber")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            metadata['warnings'].append(f"pdfplumber: {str(e)}")
            
            # Fallback to PyMuPDF
            try:
                text, pages = self._extract_with_pymupdf(pdf_path)
                if text and len(text.strip()) > 50:
                    metadata['method'] = 'pymupdf'
                    metadata['pages'] = pages
                    metadata['success'] = True
                    logger.info(f"Successfully extracted text using PyMuPDF ({pages} pages)")
                else:
                    raise ValueError("Insufficient text extracted with PyMuPDF")
            except Exception as e2:
                logger.error(f"PyMuPDF extraction failed: {e2}")
                metadata['warnings'].append(f"pymupdf: {str(e2)}")
                metadata['success'] = False
                return "", metadata
        
        # Clean and normalize the extracted text
        cleaned_text = self._clean_and_normalize(text)
        
        return cleaned_text, metadata
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[str, int]:
        """Extract text using pdfplumber"""
        import pdfplumber
        
        text_parts = []
        page_count = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=2,
                    layout=False,
                    x_density=7.25,
                    y_density=13
                )
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts), page_count
    
    def _extract_with_pymupdf(self, pdf_path: str) -> Tuple[str, int]:
        """Extract text using PyMuPDF (fitz)"""
        import fitz  # PyMuPDF
        
        text_parts = []
        
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        
        for page in doc:
            # Get text with better layout preservation
            page_text = page.get_text("text", sort=True)
            if page_text:
                text_parts.append(page_text)
        
        doc.close()
        
        return "\n\n".join(text_parts), page_count
    
    def _clean_and_normalize(self, text: str) -> str:
        """
        Clean and normalize extracted text to fix common PDF extraction issues.
        
        This handles:
        - Unicode normalization
        - Broken characters
        - Random spacing
        - Bullet symbols
        - Line reconstruction
        """
        if not text:
            return ""
        
        # Step 1: Unicode normalization (NFC form)
        text = unicodedata.normalize('NFC', text)
        
        # Step 2: Fix common encoding issues using ftfy if available
        try:
            import ftfy
            text = ftfy.fix_text(text)
        except ImportError:
            pass
        
        # Step 3: Replace problematic Unicode characters
        replacements = {
            '\uf0b7': '•',  # Bullet
            '\uf0a7': '•',  # Another bullet variant
            '\u2022': '•',  # Bullet
            '\u2023': '•',  # Triangular bullet
            '\u25cf': '•',  # Black circle
            '\u25e6': '•',  # White bullet
            '\u2043': '-',  # Hyphen bullet
            '\uf02d': '-',  # Private use dash
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u00a0': ' ',  # Non-breaking space
            '\u200b': '',   # Zero-width space
            '\ufeff': '',   # BOM
            '\t': ' ',      # Tab to space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Step 4: Remove control characters except newlines
        text = ''.join(char for char in text if char == '\n' or char == '\r' or not unicodedata.category(char).startswith('C'))
        
        # Step 5: Fix broken words (letters separated by spaces)
        # Pattern: single letter followed by space and another single letter
        text = re.sub(r'(?<=[a-zA-Z])\s(?=[a-zA-Z]\s[a-zA-Z])', '', text)
        
        # Step 6: Fix multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Step 7: Fix line breaks
        # Replace single line breaks within paragraphs with space
        lines = text.split('\n')
        processed_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if processed_lines and processed_lines[-1] != '':
                    processed_lines.append('')
                continue
            
            # Check if this line should be joined with previous
            if processed_lines and processed_lines[-1]:
                prev_line = processed_lines[-1]
                # Join if previous line doesn't end with sentence-ending punctuation
                # and current line starts with lowercase
                if (not prev_line.endswith(('.', '!', '?', ':', ';')) and
                    line and line[0].islower()):
                    processed_lines[-1] = prev_line + ' ' + line
                    continue
                # Also join if previous line ends with a hyphen (word break)
                if prev_line.endswith('-'):
                    processed_lines[-1] = prev_line[:-1] + line
                    continue
            
            processed_lines.append(line)
        
        text = '\n'.join(processed_lines)
        
        # Step 8: Clean up multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Step 9: Final trim
        text = text.strip()
        
        return text
    
    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """
        Validate PDF file before processing.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        import os
        
        # Check file exists
        if not os.path.exists(pdf_path):
            return False, "File not found"
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            return False, "File is empty"
        if file_size > 16 * 1024 * 1024:  # 16MB
            return False, "File too large (max 16MB)"
        
        # Check PDF header
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF'):
                    return False, "Invalid PDF format"
        except Exception as e:
            return False, f"Cannot read file: {str(e)}"
        
        return True, ""


# Singleton instance
pdf_extractor = PDFExtractor()

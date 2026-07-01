import os
import re
from typing import List, Dict
import fitz  # PyMuPDF
import docx  # python-docx

class DocumentParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> Dict[str, any]:
        """
        Accepts PDF, DOCX, TXT file uploads, extracts text,
        splits into paragraphs, and returns text and paragraph list.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = self.extract_text_from_docx(file_path)
        elif ext in ['.txt', '.md', '.py', '.js', '.json', '.html', '.css']:
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        # Ensure text is not completely empty
        text = text.strip()
        paragraphs = self.split_into_paragraphs(text)

        return {
            "text": text,
            "paragraphs": paragraphs
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file using PyMuPDF (fitz)"""
        text_parts = []
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file using python-docx"""
        try:
            doc = docx.Document(file_path)
            paragraphs_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs_text.append(paragraph.text)
            return "\n\n".join(paragraphs_text)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from a plain text file"""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode TXT file with standard encodings.")

    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into distinct paragraphs based on double newlines"""
        if not text:
            return []
        
        # Split by double newline or multiple blank lines
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text)]
        # Filter out empty strings
        paragraphs = [p for p in paragraphs if p]
        
        # Fallback if text is long but no double newlines exist (e.g. single newline separated)
        if len(paragraphs) <= 1 and len(text.splitlines()) > 5:
            # Try splitting by single newline if it seems formatted line-by-line
            lines = [l.strip() for l in text.splitlines()]
            paragraphs = [l for l in lines if l]
            
        return paragraphs

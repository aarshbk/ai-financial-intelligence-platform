"""
Document Processing Module
Handles PDF extraction, text cleaning, and chunking
"""
import pdfplumber
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process financial documents (PDFs) and extract text"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, dict]:
        """
        Extract text from PDF file
        
        Returns:
            Tuple of (full_text, metadata)
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                metadata = {
                    "pages": len(pdf.pages),
                    "file_name": pdf_path.split("/")[-1]
                }
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- Page {page_num + 1} ---\n"
                        full_text += text
                
                return full_text, metadata
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-.,;:()$%\/]', '', text)
        # Remove multiple punctuation
        text = re.sub(r'\.{2,}', '.', text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def process_document(self, pdf_path: str) -> Tuple[List[str], dict]:
        """
        Complete pipeline: extract -> clean -> chunk
        """
        raw_text, metadata = self.extract_text_from_pdf(pdf_path)
        cleaned_text = self.clean_text(raw_text)
        chunks = self.chunk_text(cleaned_text)
        
        metadata["chunks_count"] = len(chunks)
        metadata["total_length"] = len(cleaned_text)
        
        return chunks, metadata

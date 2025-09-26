#!/usr/bin/env python3
"""
PDF to Markdown Converter
Extracts text from PDF files and converts them to optimized markdown format
for reduced storage while maintaining context comprehension.
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple
import logging

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("Required packages not found. Please install them using:")
    print("pip install PyPDF2 pdfplumber")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFToMarkdownConverter:
    """Converts PDF files to optimized markdown format."""
    
    def __init__(self, output_dir: str = "markdown_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text_with_pdfplumber(self, pdf_path: str) -> List[str]:
        """Extract text using pdfplumber for better formatting preservation."""
        pages_text = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}/{len(pdf.pages)}")
                    
                    # Extract text with layout preservation
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                    else:
                        # Fallback to PyPDF2 if pdfplumber fails
                        pages_text.append(self._extract_with_pypdf2(pdf_path, page_num))
                        
        except Exception as e:
            logger.error(f"Error with pdfplumber: {e}")
            # Fallback to PyPDF2
            pages_text = self._extract_with_pypdf2_fallback(pdf_path)
            
        return pages_text
    
    def _extract_with_pypdf2(self, pdf_path: str, page_num: int) -> str:
        """Extract text from specific page using PyPDF2."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if page_num <= len(pdf_reader.pages):
                    page = pdf_reader.pages[page_num - 1]
                    return page.extract_text()
        except Exception as e:
            logger.error(f"Error extracting page {page_num} with PyPDF2: {e}")
        return ""
    
    def _extract_with_pypdf2_fallback(self, pdf_path: str) -> List[str]:
        """Fallback method using PyPDF2 for entire document."""
        pages_text = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    logger.info(f"Processing page {page_num}/{len(pdf_reader.pages)} (PyPDF2)")
                    text = page.extract_text()
                    pages_text.append(text)
        except Exception as e:
            logger.error(f"Error with PyPDF2 fallback: {e}")
            
        return pages_text
    
    def clean_and_optimize_text(self, text: str) -> str:
        """Clean and optimize text for markdown format."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Add space after sentence endings
        
        # Clean up bullet points and lists
        text = re.sub(r'^[\s]*[•·▪▫‣⁃]\s*', '- ', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*(\d+)[\.\)]\s*', r'\1. ', text, flags=re.MULTILINE)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Page \d+ of \d+$', '', text, flags=re.MULTILINE)
        
        # Clean up excessive punctuation
        text = re.sub(r'\.{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def format_as_markdown(self, pages_text: List[str], pdf_name: str) -> str:
        """Format extracted text as markdown."""
        markdown_content = []
        
        # Add document header
        markdown_content.append(f"# {pdf_name}")
        markdown_content.append("")
        markdown_content.append(f"*Extracted from PDF on {self._get_timestamp()}*")
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")
        
        # Process each page
        for page_num, page_text in enumerate(pages_text, 1):
            if not page_text.strip():
                continue
                
            # Clean the text
            cleaned_text = self.clean_and_optimize_text(page_text)
            
            if cleaned_text:
                # Add page separator for multi-page documents
                if len(pages_text) > 1:
                    markdown_content.append(f"## Page {page_num}")
                    markdown_content.append("")
                
                # Format paragraphs
                paragraphs = self._split_into_paragraphs(cleaned_text)
                for paragraph in paragraphs:
                    if paragraph.strip():
                        markdown_content.append(paragraph)
                        markdown_content.append("")
        
        return "\n".join(markdown_content)
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into logical paragraphs."""
        # Split on double newlines first
        paragraphs = text.split('\n\n')
        
        # Further split very long paragraphs
        processed_paragraphs = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If paragraph is too long, try to split on sentence boundaries
            if len(paragraph) > 500:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                current_para = []
                current_length = 0
                
                for sentence in sentences:
                    if current_length + len(sentence) > 500 and current_para:
                        processed_paragraphs.append(' '.join(current_para))
                        current_para = [sentence]
                        current_length = len(sentence)
                    else:
                        current_para.append(sentence)
                        current_length += len(sentence)
                
                if current_para:
                    processed_paragraphs.append(' '.join(current_para))
            else:
                processed_paragraphs.append(paragraph)
        
        return processed_paragraphs
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def convert_pdf(self, pdf_path: str) -> Optional[str]:
        """Convert a single PDF file to markdown."""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        if not pdf_path.suffix.lower() == '.pdf':
            logger.error(f"File is not a PDF: {pdf_path}")
            return None
        
        logger.info(f"Converting PDF: {pdf_path.name}")
        
        try:
            # Extract text
            pages_text = self.extract_text_with_pdfplumber(str(pdf_path))
            
            if not pages_text or not any(page.strip() for page in pages_text):
                logger.warning(f"No text extracted from {pdf_path.name}")
                return None
            
            # Format as markdown
            markdown_content = self.format_as_markdown(pages_text, pdf_path.stem)
            
            # Save markdown file
            output_file = self.output_dir / f"{pdf_path.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Calculate compression ratio
            original_size = pdf_path.stat().st_size
            markdown_size = output_file.stat().st_size
            compression_ratio = (1 - markdown_size / original_size) * 100
            
            logger.info(f"Successfully converted {pdf_path.name}")
            logger.info(f"Original size: {original_size:,} bytes")
            logger.info(f"Markdown size: {markdown_size:,} bytes")
            logger.info(f"Size reduction: {compression_ratio:.1f}%")
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error converting {pdf_path.name}: {e}")
            return None
    
    def convert_directory(self, pdf_dir: str) -> List[str]:
        """Convert all PDF files in a directory."""
        pdf_dir = Path(pdf_dir)
        converted_files = []
        
        if not pdf_dir.exists():
            logger.error(f"Directory not found: {pdf_dir}")
            return converted_files
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return converted_files
        
        logger.info(f"Found {len(pdf_files)} PDF files to convert")
        
        for pdf_file in pdf_files:
            result = self.convert_pdf(str(pdf_file))
            if result:
                converted_files.append(result)
        
        logger.info(f"Successfully converted {len(converted_files)} out of {len(pdf_files)} files")
        return converted_files


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Convert PDF files to optimized markdown format")
    parser.add_argument("input", help="PDF file or directory containing PDF files")
    parser.add_argument("-o", "--output", default="markdown_output", 
                       help="Output directory for markdown files (default: markdown_output)")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    converter = PDFToMarkdownConverter(args.output)
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Convert single file
        result = converter.convert_pdf(str(input_path))
        if result:
            print(f"Converted to: {result}")
        else:
            print("Conversion failed")
            sys.exit(1)
    elif input_path.is_dir():
        # Convert directory
        results = converter.convert_directory(str(input_path))
        if results:
            print(f"Converted {len(results)} files to {args.output}/")
        else:
            print("No files were converted")
            sys.exit(1)
    else:
        print(f"Input path does not exist: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# PDF to Markdown Converter

A Python tool that extracts text from PDF files and converts them to optimized markdown format for reduced storage while maintaining context comprehension.

## Features

- **Dual PDF Processing**: Uses both `pdfplumber` and `PyPDF2` for robust text extraction
- **Smart Text Cleaning**: Removes excessive whitespace, fixes common PDF extraction issues
- **Markdown Formatting**: Converts text to well-structured markdown with proper headings and paragraphs
- **Batch Processing**: Convert single files or entire directories
- **Size Optimization**: Significantly reduces file size while preserving readability
- **Context Preservation**: Maintains document structure and logical flow

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Convert a single PDF file:
```bash
python pdf_to_markdown.py document.pdf
```

Convert all PDFs in a directory:
```bash
python pdf_to_markdown.py /path/to/pdf/directory
```

Specify output directory:
```bash
python pdf_to_markdown.py document.pdf -o /path/to/output
```

Enable verbose logging:
```bash
python pdf_to_markdown.py document.pdf -v
```

### Programmatic Usage

```python
from pdf_to_markdown import PDFToMarkdownConverter

# Create converter instance
converter = PDFToMarkdownConverter(output_dir="markdown_output")

# Convert single file
result = converter.convert_pdf("document.pdf")

# Convert all PDFs in directory
results = converter.convert_directory("/path/to/pdfs")
```

## Output

The tool generates markdown files with:
- Document title as main heading
- Extraction timestamp
- Page separators for multi-page documents
- Clean, readable text with proper paragraph formatting
- Optimized structure for easy reading and searching

## Benefits

- **Storage Optimization**: Typically reduces file size by 60-80%
- **Better Searchability**: Plain text is easier to search than PDF content
- **Version Control Friendly**: Markdown files work well with Git
- **Cross-Platform**: Readable on any device without PDF viewers
- **Context Preservation**: Maintains document structure and meaning

## Error Handling

The tool includes robust error handling:
- Automatic fallback between PDF processing libraries
- Graceful handling of corrupted or password-protected PDFs
- Detailed logging for troubleshooting
- Continues processing other files if one fails

## Requirements

- Python 3.6+
- PyPDF2 3.0.1+
- pdfplumber 0.10.3+

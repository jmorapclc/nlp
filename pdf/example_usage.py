#!/usr/bin/env python3
"""
Example usage of the PDF to Markdown converter.
This script demonstrates how to use the converter programmatically.
"""

import os
from pathlib import Path
from pdf_to_markdown import PDFToMarkdownConverter


def example_single_file():
    """Example: Convert a single PDF file."""
    print("=== Single File Conversion Example ===")
    
    # Create converter instance
    converter = PDFToMarkdownConverter(output_dir="example_output")
    
    # Example PDF path (replace with actual PDF file)
    pdf_file = "sample.pdf"
    
    if os.path.exists(pdf_file):
        result = converter.convert_pdf(pdf_file)
        if result:
            print(f"✅ Successfully converted: {result}")
        else:
            print("❌ Conversion failed")
    else:
        print(f"⚠️  PDF file not found: {pdf_file}")
        print("   Place a PDF file named 'sample.pdf' in this directory to test")


def example_batch_conversion():
    """Example: Convert all PDFs in current directory."""
    print("\n=== Batch Conversion Example ===")
    
    # Create converter instance
    converter = PDFToMarkdownConverter(output_dir="batch_output")
    
    # Convert all PDFs in current directory
    current_dir = "."
    results = converter.convert_directory(current_dir)
    
    if results:
        print(f"✅ Successfully converted {len(results)} files:")
        for result in results:
            print(f"   - {result}")
    else:
        print("⚠️  No PDF files found in current directory")


def example_custom_processing():
    """Example: Custom processing with error handling."""
    print("\n=== Custom Processing Example ===")
    
    # Create converter with custom output directory
    converter = PDFToMarkdownConverter(output_dir="custom_output")
    
    # List of PDF files to process
    pdf_files = ["document1.pdf", "document2.pdf", "document3.pdf"]
    
    successful_conversions = []
    failed_conversions = []
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"Processing: {pdf_file}")
            result = converter.convert_pdf(pdf_file)
            
            if result:
                successful_conversions.append(result)
                print(f"  ✅ Success: {result}")
            else:
                failed_conversions.append(pdf_file)
                print(f"  ❌ Failed: {pdf_file}")
        else:
            print(f"  ⚠️  File not found: {pdf_file}")
    
    # Summary
    print(f"\n📊 Conversion Summary:")
    print(f"   Successful: {len(successful_conversions)}")
    print(f"   Failed: {len(failed_conversions)}")
    
    if failed_conversions:
        print(f"   Failed files: {', '.join(failed_conversions)}")


def main():
    """Run all examples."""
    print("PDF to Markdown Converter - Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_single_file()
    example_batch_conversion()
    example_custom_processing()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo use the converter:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run: python pdf_to_markdown.py your_file.pdf")
    print("3. Or use the programmatic API as shown in these examples")


if __name__ == "__main__":
    main()

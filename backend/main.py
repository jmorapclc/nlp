#!/usr/bin/env python3
"""
FastAPI Backend for PDF to Markdown Converter
Provides REST API endpoints for PDF conversion functionality
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add the parent directory to sys.path to import pdf_to_markdown
sys.path.append(str(Path(__file__).parent.parent))
from pdf.pdf_to_markdown import PDFToMarkdownConverter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global converter instance
converter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the converter on startup."""
    global converter
    converter = PDFToMarkdownConverter()
    logger.info("PDF to Markdown converter initialized")
    yield
    logger.info("Shutting down PDF to Markdown converter")

app = FastAPI(
    title="PDF to Markdown Converter",
    description="Convert PDF files to optimized markdown format",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PDF to Markdown Converter API",
        "version": "1.0.0",
        "endpoints": {
            "convert_single": "/api/convert/single",
            "convert_multiple": "/api/convert/multiple",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "converter_ready": converter is not None}

@app.post("/api/convert/single")
async def convert_single_pdf(
    file: UploadFile = File(...),
    output_dir: Optional[str] = Form(None)
):
    """
    Convert a single PDF file to markdown.
    
    Args:
        file: PDF file to convert
        output_dir: Optional output directory (defaults to temp directory)
    
    Returns:
        JSON response with conversion result and download link
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    if not converter:
        raise HTTPException(status_code=500, detail="Converter not initialized")
    
    try:
        # Set output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            # Use the same directory as the uploaded file (if possible) or current directory
            output_path = Path.cwd() / "markdown_output"
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Create temporary directory for processing the uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_pdf_path = Path(temp_dir) / file.filename
            
            # Save uploaded file
            with open(temp_pdf_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Set converter output directory
            converter.output_dir = output_path
            
            # Convert PDF
            result_path = converter.convert_pdf(str(temp_pdf_path))
            
            if not result_path:
                raise HTTPException(status_code=500, detail="Failed to convert PDF")
            
            # Read the converted markdown content
            with open(result_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Get file stats
            original_size = temp_pdf_path.stat().st_size
            markdown_size = Path(result_path).stat().st_size
            compression_ratio = (1 - markdown_size / original_size) * 100
            
            return {
                "success": True,
                "filename": file.filename,
                "markdown_filename": Path(result_path).name,
                "markdown_path": str(result_path),
                "output_directory": str(output_path),
                "markdown_content": markdown_content,
                "original_size": original_size,
                "markdown_size": markdown_size,
                "compression_ratio": round(compression_ratio, 1)
            }
            
    except Exception as e:
        logger.error(f"Error converting PDF {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/api/convert/multiple")
async def convert_multiple_pdfs(
    files: List[UploadFile] = File(...),
    output_dir: Optional[str] = Form(None)
):
    """
    Convert multiple PDF files to markdown.
    
    Args:
        files: List of PDF files to convert
        output_dir: Optional output directory (defaults to temp directory)
    
    Returns:
        JSON response with conversion results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate all files are PDFs
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
    
    if not converter:
        raise HTTPException(status_code=500, detail="Converter not initialized")
    
    try:
        # Set output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            # Use the same directory as the uploaded file (if possible) or current directory
            output_path = Path.cwd() / "markdown_output"
            output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set converter output directory
            converter.output_dir = output_path
            
            for file in files:
                try:
                    # Save uploaded file
                    temp_pdf_path = Path(temp_dir) / file.filename
                    with open(temp_pdf_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                    
                    # Convert PDF
                    result_path = converter.convert_pdf(str(temp_pdf_path))
                    
                    if result_path:
                        # Read the converted markdown content
                        with open(result_path, 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                        
                        # Get file stats
                        original_size = temp_pdf_path.stat().st_size
                        markdown_size = Path(result_path).stat().st_size
                        compression_ratio = (1 - markdown_size / original_size) * 100
                        
                        results.append({
                            "success": True,
                            "filename": file.filename,
                            "markdown_filename": Path(result_path).name,
                            "markdown_path": str(result_path),
                            "output_directory": str(output_path),
                            "markdown_content": markdown_content,
                            "original_size": original_size,
                            "markdown_size": markdown_size,
                            "compression_ratio": round(compression_ratio, 1)
                        })
                    else:
                        results.append({
                            "success": False,
                            "filename": file.filename,
                            "error": "Failed to convert PDF"
                        })
                        
                except Exception as e:
                    logger.error(f"Error converting PDF {file.filename}: {e}")
                    results.append({
                        "success": False,
                        "filename": file.filename,
                        "error": str(e)
                    })
            
            successful_conversions = [r for r in results if r["success"]]
            
            return {
                "success": True,
                "total_files": len(files),
                "successful_conversions": len(successful_conversions),
                "output_directory": str(output_path),
                "results": results
            }
            
    except Exception as e:
        logger.error(f"Error in batch conversion: {e}")
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download a converted markdown file.
    
    Args:
        filename: Name of the markdown file to download
    
    Returns:
        File response with the markdown file
    """
    try:
        file_path = converter.output_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='text/markdown'
        )
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

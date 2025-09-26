#!/usr/bin/env python3
"""
File Splitting Utility
Handles splitting large markdown files into smaller chunks based on various criteria.
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileSplitter:
    """Handles splitting of markdown files based on size, character count, or word count."""
    
    def __init__(self, splitting_options: Dict[str, Any]):
        self.enabled = splitting_options.get('enabled', False)
        self.max_file_size = splitting_options.get('maxFileSize', 10) * 1024 * 1024  # Convert MB to bytes
        self.max_characters = splitting_options.get('maxCharacters', 100000)
        self.max_words = splitting_options.get('maxWords', 20000)
        self.split_by = splitting_options.get('splitBy', 'size')
        
        # Smart detection options
        smart_detection = splitting_options.get('smartDetection', {})
        self.smart_detection_enabled = smart_detection.get('enabled', False)
        detection_methods = smart_detection.get('methods', {})
        self.detection_methods = {
            'chapter_markers': detection_methods.get('chapterMarkers', False),
            'numbered_headings': detection_methods.get('numberedHeadings', False),
            'major_headings': detection_methods.get('majorHeadings', False),
            'paragraph_boundaries': detection_methods.get('paragraphBoundaries', False)
        }
    
    def should_split(self, content: str) -> bool:
        """Check if content should be split based on the specified criteria."""
        if not self.enabled:
            return False
        
        if self.split_by == 'size':
            return len(content.encode('utf-8')) > self.max_file_size
        elif self.split_by == 'characters':
            return len(content) > self.max_characters
        elif self.split_by == 'words':
            word_count = len(content.split())
            return word_count > self.max_words
        
        return False
    
    def find_split_points(self, content: str) -> List[int]:
        """Find logical split points in the content based on enabled detection methods."""
        if not self.smart_detection_enabled:
            return []
        
        split_points = []
        lines = content.split('\n')
        
        # Chapter markers detection
        if self.detection_methods['chapter_markers']:
            chapter_patterns = [
                r'^#+\s*Chapter\s+\d+',  # # Chapter 1, ## Chapter 2, etc.
                r'^#+\s*Part\s+\d+',     # # Part 1, ## Part 2, etc.
                r'^#+\s*Section\s+\d+',  # # Section 1, ## Section 2, etc.
            ]
            
            for i, line in enumerate(lines):
                for pattern in chapter_patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        split_points.append(i)
                        break
        
        # Numbered headings detection
        if self.detection_methods['numbered_headings']:
            numbered_patterns = [
                r'^#+\s*\d+\.',          # # 1., ## 2., etc.
                r'^#+\s*[IVX]+\.',       # # I., ## II., etc. (Roman numerals)
            ]
            
            for i, line in enumerate(lines):
                for pattern in numbered_patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        split_points.append(i)
                        break
        
        # Major headings detection
        if self.detection_methods['major_headings']:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,3}\s+', line):  # H1, H2, H3 headings
                    split_points.append(i)
        
        # Paragraph boundaries detection (fallback)
        if self.detection_methods['paragraph_boundaries'] and not split_points:
            for i, line in enumerate(lines):
                if line.strip() == '' and i > 0:  # Empty line
                    split_points.append(i)
        
        return sorted(set(split_points))
    
    def split_content(self, content: str, base_filename: str) -> List[Dict[str, Any]]:
        """Split content into multiple files based on the specified criteria."""
        if not self.should_split(content):
            return [{
                'content': content,
                'filename': base_filename,
                'is_split': False
            }]
        
        split_points = self.find_split_points(content)
        lines = content.split('\n')
        files = []
        
        if not split_points:
            # No smart detection points found or smart detection disabled
            # Split by size/character/word limits only
            return self._split_by_size(content, base_filename)
        
        # Split at logical points
        start_idx = 0
        file_num = 1
        
        for split_point in split_points:
            if split_point <= start_idx:
                continue
                
            # Extract content for this section
            section_lines = lines[start_idx:split_point]
            section_content = '\n'.join(section_lines)
            
            # Check if this section is within limits
            if self._is_within_limits(section_content):
                filename = self._generate_filename(base_filename, file_num)
                files.append({
                    'content': section_content,
                    'filename': filename,
                    'is_split': True,
                    'section_number': file_num
                })
                file_num += 1
                start_idx = split_point
            else:
                # Section is too large, split it further
                sub_files = self._split_by_size(section_content, base_filename, file_num)
                files.extend(sub_files)
                file_num += len(sub_files)
                start_idx = split_point
        
        # Handle remaining content
        if start_idx < len(lines):
            remaining_lines = lines[start_idx:]
            remaining_content = '\n'.join(remaining_lines)
            
            if remaining_content.strip():
                if self._is_within_limits(remaining_content):
                    filename = self._generate_filename(base_filename, file_num)
                    files.append({
                        'content': remaining_content,
                        'filename': filename,
                        'is_split': True,
                        'section_number': file_num
                    })
                else:
                    sub_files = self._split_by_size(remaining_content, base_filename, file_num)
                    files.extend(sub_files)
        
        return files
    
    def _is_within_limits(self, content: str) -> bool:
        """Check if content is within the specified limits."""
        if self.split_by == 'size':
            return len(content.encode('utf-8')) <= self.max_file_size
        elif self.split_by == 'characters':
            return len(content) <= self.max_characters
        elif self.split_by == 'words':
            return len(content.split()) <= self.max_words
        return True
    
    def _split_by_size(self, content: str, base_filename: str, start_num: int = 1) -> List[Dict[str, Any]]:
        """Split content by size when no logical split points are found."""
        files = []
        file_num = start_num
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        current_content = ""
        
        for paragraph in paragraphs:
            test_content = current_content + ('\n\n' if current_content else '') + paragraph
            
            if self._is_within_limits(test_content):
                current_content = test_content
            else:
                if current_content:
                    filename = self._generate_filename(base_filename, file_num)
                    files.append({
                        'content': current_content,
                        'filename': filename,
                        'is_split': True,
                        'section_number': file_num
                    })
                    file_num += 1
                
                # If single paragraph is too large, split by sentences
                if not self._is_within_limits(paragraph):
                    sub_files = self._split_by_sentences(paragraph, base_filename, file_num)
                    files.extend(sub_files)
                    file_num += len(sub_files)
                    current_content = ""
                else:
                    current_content = paragraph
        
        # Add remaining content
        if current_content:
            filename = self._generate_filename(base_filename, file_num)
            files.append({
                'content': current_content,
                'filename': filename,
                'is_split': True,
                'section_number': file_num
            })
        
        return files
    
    def _split_by_sentences(self, content: str, base_filename: str, start_num: int) -> List[Dict[str, Any]]:
        """Split content by sentences as a last resort."""
        files = []
        file_num = start_num
        
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        current_content = ""
        
        for sentence in sentences:
            test_content = current_content + (' ' if current_content else '') + sentence
            
            if self._is_within_limits(test_content):
                current_content = test_content
            else:
                if current_content:
                    filename = self._generate_filename(base_filename, file_num)
                    files.append({
                        'content': current_content,
                        'filename': filename,
                        'is_split': True,
                        'section_number': file_num
                    })
                    file_num += 1
                
                current_content = sentence
        
        # Add remaining content
        if current_content:
            filename = self._generate_filename(base_filename, file_num)
            files.append({
                'content': current_content,
                'filename': filename,
                'is_split': True,
                'section_number': file_num
            })
        
        return files
    
    def _generate_filename(self, base_filename: str, file_num: int) -> str:
        """Generate filename with numbered suffix."""
        name, ext = os.path.splitext(base_filename)
        return f"{name}_{file_num:02d}{ext}"
    
    def save_split_files(self, files: List[Dict[str, Any]], output_dir: Path) -> List[Dict[str, Any]]:
        """Save split files to the output directory."""
        saved_files = []
        
        for file_info in files:
            file_path = output_dir / file_info['filename']
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info['content'])
                
                file_size = file_path.stat().st_size
                saved_files.append({
                    'filename': file_info['filename'],
                    'path': str(file_path),
                    'size': file_size,
                    'content': file_info['content'],  # Include content for client-side saving
                    'is_split': file_info.get('is_split', False),
                    'section_number': file_info.get('section_number', 1)
                })
                
                logger.info(f"Saved split file: {file_info['filename']} ({file_size} bytes)")
                
            except Exception as e:
                logger.error(f"Error saving split file {file_info['filename']}: {e}")
        
        return saved_files

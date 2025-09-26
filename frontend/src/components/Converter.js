import React, { useState } from 'react';
import { Upload, FolderOpen, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { convertSinglePDF, convertMultiplePDFs } from '../services/api';
import './Converter.css';

const Converter = () => {
  const [files, setFiles] = useState([]);
  const [outputDir, setOutputDir] = useState('');
  const [folderHandle, setFolderHandle] = useState(null);
  const [folderLabel, setFolderLabel] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [conversionMode, setConversionMode] = useState('single'); // 'single' or 'multiple'

  const isFileSystemAccessSupported = () => {
    return typeof window !== 'undefined' && 'showDirectoryPicker' in window;
  };

  const verifyFolderPermission = async (handle) => {
    if (!handle) return false;
    const opts = { mode: 'readwrite' };
    if (await handle.queryPermission(opts) === 'granted') return true;
    if (await handle.requestPermission(opts) === 'granted') return true;
    return false;
  };

  const selectOutputFolder = async () => {
    try {
      if (!isFileSystemAccessSupported()) {
        setError('Your browser does not support selecting a local folder. Please use Chrome/Edge or specify a server-side output directory.');
        return;
      }
      const handle = await window.showDirectoryPicker();
      const hasPerm = await verifyFolderPermission(handle);
      if (!hasPerm) {
        setError('Permission to access the selected folder was denied.');
        return;
      }
      setFolderHandle(handle);
      // Browsers do not expose full absolute path; use name label
      setFolderLabel(handle.name || 'Selected folder');
      // Mirror label to the text input for clarity (non-authoritative)
      setOutputDir(handle.name || '');
      setError(null);
    } catch (e) {
      if (e && e.name === 'AbortError') return; // user cancelled
      setError(e?.message || 'Failed to select folder');
    }
  };

  const saveMarkdownToFolder = async (name, content) => {
    if (!folderHandle) return null;
    try {
      const hasPerm = await verifyFolderPermission(folderHandle);
      if (!hasPerm) return null;
      const fileHandle = await folderHandle.getFileHandle(name, { create: true });
      const writable = await fileHandle.createWritable();
      await writable.write(content);
      await writable.close();
      return `${folderHandle.name}/${name}`; // display label; not absolute path
    } catch (e) {
      console.error('Saving to selected folder failed:', e);
      return null;
    }
  };

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const pdfFiles = selectedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== selectedFiles.length) {
      setError('Please select only PDF files.');
      return;
    }
    
    setFiles(pdfFiles);
    setError(null);
    setResults(null);
    
    // If user has not picked a folder via the File System Access API,
    // we can't infer a real local path due to browser security.
    // Encourage selecting a folder explicitly.
  };

  const handleOutputDirChange = (event) => {
    setOutputDir(event.target.value);
  };

  const handleConvert = async () => {
    if (files.length === 0) {
      setError('Please select at least one PDF file.');
      return;
    }

    setIsConverting(true);
    setError(null);
    setResults(null);

    try {
      let response;
      if (conversionMode === 'single' && files.length === 1) {
        response = await convertSinglePDF(files[0], outputDir);
      } else {
        response = await convertMultiplePDFs(files, outputDir);
      }
      
      // Attempt client-side save if a folder is selected and API supported
      if (folderHandle && isFileSystemAccessSupported()) {
        if (conversionMode === 'single' && response?.success) {
          const savedLabelPath = await saveMarkdownToFolder(response.markdown_filename, response.markdown_content || '');
          setResults({ ...response, client_saved_path: savedLabelPath });
        } else if (response?.results?.length) {
          const enriched = await Promise.all(response.results.map(async (r) => {
            if (r.success) {
              const p = await saveMarkdownToFolder(r.markdown_filename, r.markdown_content || '');
              return { ...r, client_saved_path: p };
            }
            return r;
          }));
          setResults({ ...response, results: enriched });
        } else {
          setResults(response);
        }
      } else {
        setResults(response);
      }
    } catch (err) {
      setError(err.message || 'Conversion failed. Please try again.');
    } finally {
      setIsConverting(false);
    }
  };


  const resetForm = () => {
    setFiles([]);
    setOutputDir('');
    setResults(null);
    setError(null);
    // Reset file input
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

  return (
    <div className="converter">
      <div className="converter-header">
        <h2>Convert PDF to Markdown</h2>
        <p>Upload PDF files and convert them to optimized Markdown format</p>
      </div>

      <div className="converter-content">
        {/* Mode Selection */}
        <div className="mode-selector">
          <label className="mode-option">
            <input
              type="radio"
              name="conversionMode"
              value="single"
              checked={conversionMode === 'single'}
              onChange={(e) => setConversionMode(e.target.value)}
            />
            <span>Single File</span>
          </label>
          <label className="mode-option">
            <input
              type="radio"
              name="conversionMode"
              value="multiple"
              checked={conversionMode === 'multiple'}
              onChange={(e) => setConversionMode(e.target.value)}
            />
            <span>Multiple Files</span>
          </label>
        </div>

        {/* File Upload */}
        <div className="upload-section">
          <div className="upload-area">
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              multiple={conversionMode === 'multiple'}
              onChange={handleFileSelect}
              className="file-input"
            />
            <label htmlFor="file-input" className="upload-label">
              <Upload className="upload-icon" />
              <div className="upload-text">
                <strong>Choose PDF files</strong>
                <span>
                  {conversionMode === 'single' 
                    ? 'Select a single PDF file' 
                    : 'Select one or more PDF files'
                  }
                </span>
              </div>
            </label>
          </div>
          
          {files.length > 0 && (
            <div className="file-list">
              <h4>Selected Files:</h4>
              <ul>
                {files.map((file, index) => (
                  <li key={index} className="file-item">
                    <FileText className="file-icon" />
                    <span>{file.name}</span>
                    <span className="file-size">
                      ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Output Directory */}
        <div className="output-section">
          <label htmlFor="output-dir" className="output-label">
            Output Directory (optional)
          </label>
          <input
            id="output-dir"
            type="text"
            value={outputDir}
            onChange={handleOutputDirChange}
            placeholder="Leave empty to use default location"
            className="output-input"
          />
          <div className="folder-picker-row">
            <button type="button" className="folder-button" onClick={selectOutputFolder}>
              <FolderOpen className="button-icon" />
              Select output folder (local)
            </button>
            {folderLabel && (
              <span className="folder-label">Selected: {folderLabel}</span>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <AlertCircle className="error-icon" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            onClick={handleConvert}
            disabled={files.length === 0 || isConverting}
            className="convert-button"
          >
            {isConverting ? (
              <>
                <Loader className="button-icon spinning" />
                Converting...
              </>
            ) : (
              <>
                <FileText className="button-icon" />
                Convert to Markdown
              </>
            )}
          </button>
          
          <button
            onClick={resetForm}
            disabled={isConverting}
            className="reset-button"
          >
            Reset
          </button>
        </div>

        {/* Results Display */}
        {results && (
          <div className="results-section">
            <h3>Conversion Results</h3>
            
            {conversionMode === 'single' ? (
              <div className="single-result">
                <div className="result-header">
                  <CheckCircle className="success-icon" />
                  <span>Successfully converted!</span>
                </div>
                <div className="result-details">
                  <p><strong>File:</strong> {results.filename}</p>
                  <p><strong>Size Reduction:</strong> {results.compression_ratio}%</p>
                  <p><strong>Original Size:</strong> {(results.original_size / 1024).toFixed(2)} KB</p>
                  <p><strong>Markdown Size:</strong> {(results.markdown_size / 1024).toFixed(2)} KB</p>
                  <div className="file-location">
                    <p><strong>Saved to:</strong></p>
                    {folderHandle && results.client_saved_path ? (
                      <p className="file-path">{results.client_saved_path}</p>
                    ) : (
                      <p className="file-path">{results.output_directory}/{results.markdown_filename}</p>
                    )}
                  </div>
                </div>
                <div className="success-message">
                  <CheckCircle className="success-icon small" />
                  <span>Markdown file has been saved{folderHandle ? ' to the selected local folder' : ' to the server output directory'}</span>
                </div>
              </div>
            ) : (
              <div className="multiple-results">
                <div className="results-summary">
                  <CheckCircle className="success-icon" />
                  <span>
                    Converted {results.successful_conversions} of {results.total_files} files
                  </span>
                </div>
                
                {!folderHandle && (
                  <div className="output-directory-info">
                    <p><strong>Server Output Directory:</strong> {results.output_directory}</p>
                  </div>
                )}
                
                <div className="results-list">
                  {results.results.map((result, index) => (
                    <div key={index} className="result-item">
                      <div className="result-item-header">
                        {result.success ? (
                          <CheckCircle className="success-icon small" />
                        ) : (
                          <AlertCircle className="error-icon small" />
                        )}
                        <span className="result-filename">{result.filename}</span>
                      </div>
                      
                      {result.success ? (
                        <div className="result-item-details">
                          <p>Size Reduction: {result.compression_ratio}%</p>
                          <div className="file-location">
                            {folderHandle && result.client_saved_path ? (
                              <p><strong>Saved to:</strong> {result.client_saved_path}</p>
                            ) : (
                              <p><strong>Saved to:</strong> {results.output_directory}/{result.markdown_filename}</p>
                            )}
                          </div>
                        </div>
                      ) : (
                        <p className="error-text">{result.error}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Converter;

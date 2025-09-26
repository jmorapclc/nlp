import React, { useState } from 'react';
import { Upload, Download, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { convertSinglePDF, convertMultiplePDFs } from '../services/api';
import './Converter.css';

const Converter = () => {
  const [files, setFiles] = useState([]);
  const [outputDir, setOutputDir] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [conversionMode, setConversionMode] = useState('single'); // 'single' or 'multiple'

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
      
      setResults(response);
    } catch (err) {
      setError(err.message || 'Conversion failed. Please try again.');
    } finally {
      setIsConverting(false);
    }
  };

  const handleDownload = (downloadUrl) => {
    window.open(downloadUrl, '_blank');
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
                </div>
                <button
                  onClick={() => handleDownload(results.download_url)}
                  className="download-button"
                >
                  <Download className="button-icon" />
                  Download Markdown
                </button>
              </div>
            ) : (
              <div className="multiple-results">
                <div className="results-summary">
                  <CheckCircle className="success-icon" />
                  <span>
                    Converted {results.successful_conversions} of {results.total_files} files
                  </span>
                </div>
                
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
                          <button
                            onClick={() => handleDownload(result.download_url)}
                            className="download-button small"
                          >
                            <Download className="button-icon" />
                            Download
                          </button>
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

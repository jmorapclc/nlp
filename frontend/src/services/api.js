import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 300000, // 5 minutes timeout for large PDF conversions
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout. The PDF conversion is taking longer than expected. Please try with a smaller file or wait longer.');
      } else {
        throw new Error('No response from server. Please check if the backend is running and try again.');
      }
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

/**
 * Convert a single PDF file to markdown
 * @param {File} file - The PDF file to convert
 * @param {string} outputDir - Optional output directory
 * @returns {Promise<Object>} Conversion result
 */
export const convertSinglePDF = async (file, outputDir = '') => {
  const formData = new FormData();
  formData.append('file', file);
  if (outputDir) {
    formData.append('output_dir', outputDir);
  }

  try {
    console.log('Starting single PDF conversion...');
    const response = await api.post('/convert/single', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Single PDF conversion response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Single PDF conversion error:', error);
    throw new Error(`Single PDF conversion failed: ${error.message}`);
  }
};

/**
 * Convert multiple PDF files to markdown
 * @param {File[]} files - Array of PDF files to convert
 * @param {string} outputDir - Optional output directory
 * @returns {Promise<Object>} Conversion results
 */
export const convertMultiplePDFs = async (files, outputDir = '') => {
  const formData = new FormData();
  
  // Append all files
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  if (outputDir) {
    formData.append('output_dir', outputDir);
  }

  try {
    console.log('Starting multiple PDF conversion...');
    const response = await api.post('/convert/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Multiple PDF conversion response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Multiple PDF conversion error:', error);
    throw new Error(`Multiple PDF conversion failed: ${error.message}`);
  }
};

/**
 * Download a converted markdown file
 * @param {string} filename - Name of the file to download
 * @returns {Promise<Blob>} File blob
 */
export const downloadMarkdownFile = async (filename) => {
  try {
    const response = await api.get(`/download/${filename}`, {
      responseType: 'blob',
    });
    
    return response.data;
  } catch (error) {
    throw new Error(`Download failed: ${error.message}`);
  }
};

/**
 * Check if the API is healthy
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(`Health check failed: ${error.message}`);
  }
};

export default api;

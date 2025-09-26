# PDF to Markdown Converter Web App

A modern, responsive web application for converting PDF files to optimized Markdown format. Built with FastAPI backend and React frontend, featuring a dark/light theme toggle and minimalist design.

## Features

- **Single & Multiple File Conversion**: Convert one or multiple PDF files at once
- **Modern UI**: Clean, minimalist interface with dark/light theme support
- **Real-time Progress**: Visual feedback during conversion process
- **File Management**: Easy file selection and output directory configuration
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Comprehensive error messages and validation
- **Size Optimization**: Shows compression ratios and file size reductions

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PyPDF2 & pdfplumber**: PDF text extraction
- **Uvicorn**: ASGI server
- **CORS**: Cross-origin resource sharing

### Frontend
- **React 18**: Modern React with hooks
- **Axios**: HTTP client for API communication
- **Lucide React**: Modern icon library
- **CSS Variables**: Dynamic theming system

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI server**:
   ```bash
   cd backend
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the React development server**:
   ```bash
   npm start
   ```
   
   The app will be available at `http://localhost:3000`

## Usage

1. **Open the web application** in your browser
2. **Choose conversion mode**: Single file or multiple files
3. **Select PDF files** by clicking the upload area or using the file picker
4. **Optional**: Specify an output directory (defaults to server temp directory)
5. **Click "Convert to Markdown"** to start the conversion
6. **Download results** when conversion is complete

## API Endpoints

### Backend API (`http://localhost:8000`)

- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/convert/single` - Convert single PDF
- `POST /api/convert/multiple` - Convert multiple PDFs
- `GET /api/download/{filename}` - Download converted file

### Example API Usage

```bash
# Convert single PDF
curl -X POST "http://localhost:8000/api/convert/single" \
  -F "file=@document.pdf" \
  -F "output_dir=/path/to/output"

# Convert multiple PDFs
curl -X POST "http://localhost:8000/api/convert/multiple" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "output_dir=/path/to/output"
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Backend Configuration

The backend can be configured by modifying `backend/main.py`:

- **CORS origins**: Add allowed origins for production
- **File size limits**: Adjust upload limits
- **Output directory**: Set default output location

## Development

### Project Structure

```
nlp/
├── backend/
│   └── main.py              # FastAPI application
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API services
│   │   └── App.js
│   └── package.json
├── pdf/
│   └── pdf_to_markdown.py   # Core conversion logic
└── requirements.txt
```

### Adding Features

1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Create components in `frontend/src/components/`
3. **API**: Update services in `frontend/src/services/api.js`

## Deployment

### Backend Deployment

1. **Install production dependencies**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
   ```

### Frontend Deployment

1. **Build for production**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve static files** with nginx or similar

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure backend CORS is configured for your frontend URL
2. **File upload fails**: Check file size limits and PDF file validity
3. **Conversion errors**: Verify PDF files are not password-protected or corrupted
4. **Port conflicts**: Change ports in package.json (frontend) or main.py (backend)

### Debug Mode

Enable debug logging:

```bash
# Backend
cd backend
python main.py --log-level debug

# Frontend
cd frontend
REACT_APP_DEBUG=true npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

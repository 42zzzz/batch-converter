# MarkItDown Batch Converter

## Overview

A Python-based batch conversion tool that transforms documents into Markdown format using the MarkItDown library, with support for all MarkItDown-compatible file types.

## Supported File Types

| Category | Extensions |
|---|---|
| Text / Markdown | `.txt`, `.text`, `.md`, `.markdown` |
| Data | `.json`, `.jsonl`, `.csv` |
| Web | `.html`, `.htm`, `.rss`, `.atom`, `.xml` |
| Microsoft Office | `.docx`, `.pptx`, `.xlsx`, `.xls` |
| PDF | `.pdf` |
| Images | `.jpg`, `.jpeg`, `.png` |
| Audio / Video | `.wav`, `.mp3`, `.m4a`, `.mp4` |
| Email | `.msg` |
| Notebooks | `.ipynb` |
| E-books | `.epub` |
| Archives | `.zip` |

## Features

- Batch process all supported documents in a folder
- Preserve document structure and formatting
- Interactive folder selection prompt
- Automatic output to a `Markdown/` subfolder
- Progress tracking with progress bar
- Detailed logging to a `Logs/` subfolder
- Error handling with retry logic

## Prerequisites

- Python 3.8+
- pip package manager

## Installation

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

```
pdf-converter/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── converter.py       # Core conversion logic
│   ├── batch_processor.py # Interactive batch processing
│   └── ocr_handler.py     # OCR implementation (future)
└── tests/
    ├── __init__.py
    ├── test_converter.py
    └── test_batch_processor.py
```

## Usage

Run the script — it will prompt you for the folder path:

```bash
python src/batch_processor.py
```

```
MarkItDown Batch Converter
==============================
Enter the path to the folder containing documents:
```

Type or paste the path to your folder of documents. The script will:
- Scan for all supported file types in that folder
- Convert each one to Markdown using MarkItDown
- Save the `.md` files to a `Markdown/` subfolder inside your chosen folder
- Write processing logs to a `Logs/` subfolder
- Report results when complete

## Implementation

### Core Components

**1. BatchProcessor Class**
- Handles directory scanning across all supported extensions
- Manages file queue
- Generates progress reports
- Supports resume via progress file

**2. Converter Class**
- Initializes MarkItDown engine
- Validates file types before processing
- Handles single file conversion
- Error handling and retry logic

**3. OCR Handler (Future)**
- Detects images within PDF
- Extracts images using pdf2image
- Applies Tesseract OCR
- Injects extracted text into Markdown output

## Error Handling

- Validation of supported file types before processing
- Graceful failure with detailed error logs
- Resume capability for interrupted batches
- Timeout protection for problematic files

## Performance Considerations

- Process files sequentially to manage memory
- Implement streaming for very large files
- Cache OCR results when implemented
- Optimize image resolution settings

## Testing

```bash
python -m unittest discover tests -v
```

## Future Enhancements

- [ ] OCR support for embedded images
- [ ] Parallel processing support
- [ ] Custom CSS styling for output
- [ ] Integration with cloud storage
- [ ] Web interface wrapper
- [ ] Support for password-protected PDFs
- [ ] Automated quality scoring

## Security Considerations

- Validate input paths to prevent directory traversal
- Sanitize file names in output
- Log processing without exposing sensitive data
- Sandbox OCR operations when possible

## License

MIT License

# MetadataCleaner

A Flask-based web application to clean metadata from files and check for digital signatures in PDF files. It supports multiple file types, including images, PDFs, documents, spreadsheets, and audio files. Additionally, it processes ZIP and RAR archives by cleaning metadata of individual files within the archive.

## Features

- Metadata Removal: Removes metadata from supported files.
- PDF Signature Check: Checks if a PDF is digitally signed.
- Archive Processing: Extracts and processes files within ZIP and RAR archives.
- File Types Supported:
  - Images: jpg, jpeg, png
  - PDFs: pdf
  - Documents: doc, docx
  - Spreadsheets: xls, xlsx
  - Audio: mp3, flac, wav
  - Archives: zip, rar

## Installation

1. Clone the Repository:

git clone https://github.com/yourusername/file-metadata-cleaner.git
cd file-metadata-cleaner
2. Set Up Virtual Environment:
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies:
pip install -r requirements.txt
4. Install System Dependencies (if needed):
- Install 'libmagic' and other dependencies for rarfile and mutagen.
5. Run the Application:
  
```python
app.py
```

The application will be accessible at http://127.0.0.1:8000.

## Usage

### Web Interface

1. Navigate to the home page: http://127.0.0.1:8000.

2. Upload a file through the provided form.

3. The app will process the file and provide a cleaned version for download.

### API Endpoints

```
POST /check_pdf_signature
```

**Description:** Checks if a PDF is digitally signed.
  
**Request:** Form data with file as the PDF.
**Response:** 

```json
{"signed": true}
```
If the PDF is signed.

```json
{"signed": false}
```
If the PDF is not signed.

```
POST /upload
```

**Description:** Upload and process a file for metadata cleaning.
**Request:** Form data with file as the input.
**Response:**
```json
{"message": "File successfully cleaned", "download_url": "<URL>"}
```

On success.

```json
{"error": "<error message>"}
```

On failure.

```
GET /download/<filename>
```

**Description:** Download the cleaned file.
**Response:** The cleaned file is served for download.

## File Processing Logic

Images: Removes EXIF data using Pillow.
PDFs: Strips metadata and checks for digital signatures using pikepdf.
Documents and Spreadsheets: Uses python-docx and openpyxl to rewrite files without metadata.
Audio Files: Strips metadata using mutagen.
Archives: Extracts files, cleans metadata, and re-packages them into a ZIP.
Configuration

*The application runs on http://0.0.0.0:8000 by default. Modify the app.run() parameters in app.py to change the host and port.*

## Dependencies

```
Flask
Pillow
pikepdf
python-docx
openpyxl
mutagen
rarfile
Logging
```

*The application logs errors and processing details using Python's logging module.*

## Contributing

Feel free to submit issues or pull requests to improve this project.

## License

This project is licensed under the MIT License.

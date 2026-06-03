# OCR Web Application

A complete OCR web app built with Flask and PaddleOCR for extracting text from images and PDFs.

## Features
- Text recognition from images and scanned documents
- PDF, JPG, PNG, TIFF, BMP, WEBP upload support
- Multi-language OCR (`en, fr, de, es, ch, ar, hi` configurable)
- Table detection from OCR lines
- Handwriting mode flag support in OCR flow
- Real-time job progress polling
- Drag-and-drop style upload interface
- Batch upload processing
- Export OCR results to JSON and TXT
- REST API endpoints for automation

## Project Structure

```text
ocr-web-app/
├── app.py
├── requirements.txt
├── config.py
├── utils/
│   ├── __init__.py
│   ├── ocr_processor.py
│   ├── image_processor.py
│   ├── pdf_handler.py
│   └── table_detector.py
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── templates/
│   ├── index.html
│   ├── upload.html
│   └── results.html
├── uploads/
├── tests/
│   └── test_app.py
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## API Endpoints

- `POST /api/ocr` - Submit one or many files (`file` or `files`) with optional `lang`, `detect_tables`, `handwriting`
- `POST /api/ocr/batch` - Alias for batch OCR processing
- `GET /api/jobs/<job_id>` - Check OCR job status and result
- `GET /api/export/<job_id>.json` - Export OCR output in JSON
- `GET /api/export/<job_id>.txt` - Export OCR output in text
- `GET /health` - Health endpoint

## Notes

- PaddleOCR is loaded lazily in `utils/ocr_processor.py`.
- If PaddleOCR is unavailable at runtime, the app responds with a fallback empty result instead of crashing.
- For PDF OCR, install Poppler on your system so `pdf2image` can render PDF pages.

## Run Tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

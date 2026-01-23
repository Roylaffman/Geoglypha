# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Geoglypha is a full-stack web application combining a static front-end (HTML/CSS/JavaScript) with a Python Flask backend. It focuses on archaeology, history, and geography, featuring interactive Leaflet.js maps and a KML/KMZ to GeoJSON file conversion service.

## Development Commands

### Flask Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Flask dev server (port 5000)
python app.py

# Production (Google App Engine)
gunicorn -b :$PORT app:app
```

### Frontend Dependencies
```bash
npm install   # Installs Leaflet.js
```

### Deployment
```powershell
# AWS infrastructure setup
./aws-setup.ps1

# Verify AWS infrastructure
./verify-aws-infrastructure.ps1

# Upload to Google Cloud Storage
./upload-to-gcs.ps1
```

## Architecture

### Frontend
- Vanilla HTML/CSS/JavaScript with no framework
- **Leaflet.js** (v1.9.4) for interactive mapping, loaded via CDN (unpkg.com)
- Root-level HTML pages for each project/tool (cahokia.html, stonehenge.html, kml_to_geojson.html, etc.)
- CSS custom properties for theming (primary: `#3a6351`, secondary: `#f2edd7`, accent: `#a0937d`)

### Backend (`app.py`)
- Flask application serving as a KML/KMZ to GeoJSON converter
- API endpoints:
  - `GET /` — Serves homepage
  - `POST /upload` — Accepts KML/KMZ files, converts to GeoJSON FeatureCollection
  - `POST /download` — Returns GeoJSON as downloadable file
- Uses `pykml`/`lxml` for KML parsing, `python-magic` for file type detection
- Storage: Google Cloud Storage (production) with local tempdir fallback
- 16MB max upload size

### Data
- GeoJSON files at root level (cahokiaboundary.geojson, cmounds.geojson, Mounds.geojson)
- `cuneiform_library.py` — Unicode Cuneiform symbol mappings used by cunescript.js

### Subdirectories
- `graphita/` — Graphite artwork gallery
- `weather/` — Weather visualization charts (barometric pressure, precipitation, temperature, wind)
- `images/` — Project images

## Infrastructure

- **Current production**: Google App Engine (Python 3.9 runtime, `app.yaml`)
- **AWS migration in progress**: S3 static hosting + CloudFront CDN
- Bucket name: `geoglypha1` (GCS) / `geoglypha-website` (AWS S3)
- AWS config template in `aws-config.template.json`

## No Test Framework

There is currently no test suite configured. The npm test script is a placeholder.

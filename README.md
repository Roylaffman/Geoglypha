# KML/KMZ to GeoJSON Converter - Quick Start Guide

This application allows users to upload KML or KMZ files and convert them to GeoJSON format, preserving folder structures, placemarks, and descriptions.

## Local Development

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup and Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the application at http://localhost:8080

## Features

- Upload KML or KMZ files
- Extract placemarks with coordinates
- Preserve folder structure information
- Capture descriptions and popup content
- Visualize data on an interactive map
- Download converted GeoJSON files

## File Structure

- `app.py` - Main Flask application with KML/KMZ parsing logic
- `templates/index.html` - Frontend interface with styling
- `app.yaml` - Google App Engine configuration
- `requirements.txt` - Python dependencies
- `deployment_guide.md` - Detailed Google Cloud deployment instructions

## Google Cloud Deployment

For detailed deployment instructions, see `deployment_guide.md`.

Quick deployment steps:
1. Create a Google Cloud Storage bucket
2. Update the `BUCKET_NAME` in app.yaml
3. Deploy with `gcloud app deploy`

## Testing

The application has been tested with various KML and KMZ files to ensure proper extraction of:
- Placemarks and coordinates
- Folder hierarchies
- Descriptions and popup content

## Troubleshooting

- If you encounter issues with the `python-magic` library, ensure `libmagic` is installed on your system:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install libmagic1
  
  # macOS
  brew install libmagic
  ```

- For deployment issues, refer to the detailed troubleshooting section in `deployment_guide.md`

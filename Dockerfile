# Dockerfile
# Ryan Lafferty — Geoglypha Tools API
# Deploys to Google Cloud Run at tools.geoglypha1.org

FROM python:3.12-slim

WORKDIR /app

# System deps:
#   libmagic1     — python-magic file type detection
#   libpq-dev     — psycopg2 PostgreSQL driver
#   gdal-bin      — GDAL CLI tools (gdalinfo, gdal_translate, etc.)
#   libgdal-dev   — GDAL headers for rasterio/fiona build
#   libgeos-dev   — GEOS geometry engine for shapely/geopandas
#   libproj-dev   — PROJ for coordinate transforms (pyproj)
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL version env so rasterio/fiona can link against it
RUN export GDAL_VERSION=$(gdal-config --version) && echo "GDAL $GDAL_VERSION"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY models.py .
COPY init_db.py .
COPY templates/ templates/

# Default port for Cloud Run
ENV PORT=8080

EXPOSE 8080

# 2 workers, 4 threads, 180s timeout for raster/COG operations
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 180 app:app

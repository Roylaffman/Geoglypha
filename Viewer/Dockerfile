# Viewer/Dockerfile
# Ryan Lafferty — Geoglypha Viewer (Streamlit)
# Deploys to viewer.geoglypha1.org as a Cloud Run service

FROM python:3.12-slim

WORKDIR /app

# System deps: GDAL for rasterio/geopandas, GEOS for shapely
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY viewer.py .
COPY .streamlit/ .streamlit/

ENV PORT=8080

EXPOSE 8080

CMD streamlit run viewer.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false

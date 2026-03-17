# Geoglypha Tools — Deployment Guide
Ryan Lafferty

This guide covers deploying the Flask tools API to Google Cloud Run with a Cloud SQL PostgreSQL database, wiring it to `tools.geoglypha1.org` via Cloudflare, and verifying each layer is working.

## Architecture Summary

```
Cloudflare DNS
      |
      +── www.geoglypha1.org  ──► GCS Bucket (static HTML/CSS/JS)
      |
      +── tools.geoglypha1.org ──► Cloud Run: geoglypha-api
                                        |
                                   Cloud SQL (PostgreSQL)
                                   (geoglyph points, future data)
```

## GCP Project Reference

| Item | Value |
|---|---|
| Project ID | `precise-equator-411516` |
| Region | `us-central1` |
| Cloud Run service | `geoglypha-api` |
| Artifact Registry | `us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api` |
| GCS bucket | `www.geoglypha1.org` |


## Prerequisites

Install and authenticate these tools before starting:

```bash
# Google Cloud CLI
gcloud auth login
gcloud config set project precise-equator-411516

# Docker Desktop (must be running)
docker --version

# Verify Artifact Registry credentials
gcloud auth configure-docker us-central1-docker.pkg.dev
```


## Step 1 — Cloud SQL Database (PostgreSQL)

Skip this section if you do not need the geoglyphs database endpoints.

### 1a. Create the instance

```bash
gcloud sql instances create geoglypha-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-size=10GB \
  --storage-auto-increase
```

The `db-f1-micro` tier is the lowest cost option (~$7/month). Upgrade to `db-g1-small` when traffic grows.

### 1b. Create the database and user

```bash
gcloud sql databases create geoglypha \
  --instance=geoglypha-db

gcloud sql users create geoglypha_user \
  --instance=geoglypha-db \
  --password=YOUR_SECURE_PASSWORD
```

### 1c. Note the connection name

```bash
gcloud sql instances describe geoglypha-db \
  --format="value(connectionName)"
# Returns: precise-equator-411516:us-central1:geoglypha-db
```

### 1d. Seed the database

```bash
# Connect locally via Cloud SQL Proxy for initial setup
gcloud sql connect geoglypha-db --user=geoglypha_user

# Then run:
python init_db.py
```


## Step 2 — Build and Push the Docker Image

Every time `app.py`, `templates/`, `requirements.txt`, or `Dockerfile` changes, rebuild and push.

```bash
cd "C:\Users\royla\OneDrive\Documents\2.9Dev\Geoglypha"

# Build
docker build -t us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest .

# Push
docker push us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest
```

If the Artifact Registry repository does not exist yet:

```bash
gcloud artifacts repositories create geoglypha \
  --repository-format=docker \
  --location=us-central1
```


## Step 3 — Deploy to Cloud Run

### 3a. Full deploy with database

```bash
gcloud run deploy geoglypha-api \
  --image=us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --add-cloudsql-instances=precise-equator-411516:us-central1:geoglypha-db \
  --set-env-vars="BUCKET_NAME=www.geoglypha1.org,\
DB_HOST=/cloudsql/precise-equator-411516:us-central1:geoglypha-db,\
DB_NAME=geoglypha,\
DB_USER=geoglypha_user,\
DB_PASS=YOUR_SECURE_PASSWORD"
```

### 3b. Deploy without database (tools-only mode)

Use this for a faster deploy while the database is not yet configured:

```bash
gcloud run deploy geoglypha-api \
  --image=us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="BUCKET_NAME=www.geoglypha1.org"
```

### Memory requirements

| Load | Minimum memory |
|---|---|
| KML/GeoJSON conversion only | 256 MB |
| Vector viewer (geopandas) | 512 MB |
| Raster info (rasterio) | 512 MB |
| TIF to COG conversion | 1 GB |

Set to **1 GB** to cover all tools. Increase to 2 GB for large rasters.


## Step 4 — Cloudflare DNS

In the Cloudflare dashboard for `geoglypha1.org`:

| Type | Name | Content | Proxy status |
|---|---|---|---|
| CNAME | `www` | `c.storage.googleapis.com` | Proxied (orange cloud) |
| CNAME | `tools` | `ghs.googlehosted.com.` | DNS only (gray cloud) |

The `tools` subdomain must be **DNS only** (gray cloud). Google Cloud Run provisions its own SSL certificate and Cloudflare proxying breaks the certificate handshake.

After deploying, map the custom domain in Cloud Run:

```bash
gcloud run domain-mappings create \
  --service=geoglypha-api \
  --domain=tools.geoglypha1.org \
  --region=us-central1
```

Google will verify domain ownership and provision an SSL cert. This can take 10-30 minutes on first setup.


## Step 5 — Verify Deployment

```bash
# Check service status
gcloud run services describe geoglypha-api \
  --region=us-central1 \
  --format="value(status.url)"

# Hit the API info endpoint
curl https://tools.geoglypha1.org/api

# Expected response includes:
# "rasterio": true
# "geopandas": true
```

Check Cloud Run logs if something is wrong:

```bash
gcloud run services logs read geoglypha-api \
  --region=us-central1 \
  --limit=50
```


## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `BUCKET_NAME` | Yes | GCS bucket name (`www.geoglypha1.org`) |
| `DB_HOST` | No | Cloud SQL socket path or IP |
| `DB_NAME` | No | Database name (default: `geoglypha`) |
| `DB_USER` | No | Database user |
| `DB_PASS` | No | Database password |
| `PORT` | Auto | Set by Cloud Run, do not override |

The app starts in degraded mode if database variables are missing. All GIS tools (KML converter, Vector Viewer, Raster Info, TIF to COG) work without a database. Only `/api/geoglyphs` routes require it.


## Quick Redeploy Workflow

After code changes, the full cycle is:

```bash
docker build -t us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest .
docker push us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest
gcloud run deploy geoglypha-api \
  --image=us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest \
  --region=us-central1
```

Cloud Run performs a zero-downtime rolling deploy. The old container continues serving until the new one passes its health check.


## Adding Future Capabilities

### TIF/COG/Vector overlay map

The tools are already modular. When you are ready to display TIFs, COGs, and vector data together:

1. Add a `POST /api/map/composite` endpoint in `app.py` that accepts multiple files
2. Return a combined GeoJSON + raster bounds envelope + COG tile URL
3. Use Leaflet's `L.tileLayer.wms` or `georaster-layer-for-leaflet` for COG rendering on the frontend

### GRASS / QGIS operations

Add GRASS or QGIS to the Docker image:

```dockerfile
RUN apt-get install -y grass-core
```

Then call operations via subprocess in a new route:

```python
import subprocess
result = subprocess.run(
    ['grass', '--tmp-location', 'EPSG:4326', '--exec', 'v.buffer', ...],
    capture_output=True, text=True
)
```

Note: adding GRASS increases the container image size by ~400 MB. Use a multi-stage build to keep the final image lean.

### Streamlit viewer (future subdomain)

A Streamlit app with `streamlit-folium` + `st.dataframe` can be deployed as a separate Cloud Run service at `viewer.geoglypha1.org`. It calls the same Flask API endpoints and adds richer interactive attribute browsing with no additional backend work.

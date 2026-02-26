# Geoglypha Cloud Deployment Guide

## Overview

This guide covers deploying Flask applications to Google Cloud Run and routing custom subdomain traffic through Cloudflare DNS. It was written during the setup of `tools.geoglypha1.org`, which serves the Geoglypha KML/KMZ-to-GeoJSON converter API.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Flask App Setup](#flask-app-setup)
4. [Google Cloud Run Deployment](#google-cloud-run-deployment)
5. [Cloudflare DNS Routing](#cloudflare-dns-routing)
6. [SSL Certificate](#ssl-certificate)
7. [Maintenance & Troubleshooting](#maintenance--troubleshooting)
8. [Quick Reference Commands](#quick-reference-commands)

---

## Architecture

```
User Request
    |
    v
Cloudflare DNS (tools.geoglypha1.org)
    |  CNAME -> ghs.googlehosted.com
    v
Google Cloud Run (geoglypha-api)
    |
    v
Flask App (app.py via gunicorn)
```

- **Static site**: `www.geoglypha1.org` hosted on GCS bucket via Cloudflare
- **API/Apps**: `tools.geoglypha1.org` hosted on Google Cloud Run via Cloudflare
- **DNS Provider**: Cloudflare (manages both domains)

---

## Prerequisites

- Google Cloud SDK (`gcloud`) installed and authenticated
- A GCP project (ours: `precise-equator-411516`)
- Cloudflare account managing `geoglypha1.org`
- Python 3.12+
- Docker (optional, for local testing)

### Required GCP APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Required IAM Roles for the Cloud Build Service Account

```bash
PROJECT_ID="precise-equator-411516"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/cloudbuild.builds.builder"
```

---

## Flask App Setup

### Project Structure

```
Geoglypha/
  app.py              # Flask application
  models.py           # SQLAlchemy models (optional)
  init_db.py           # Database seed script (optional)
  requirements.txt     # Python dependencies
  Dockerfile           # Container build instructions
  app.yaml             # App Engine config (alternative to Cloud Run)
  .gcloudignore        # Files to exclude from deployment
```

### requirements.txt

```
Flask==3.1.0
flask-cors==4.0.0
gunicorn==21.2.0
pykml==0.2.0
lxml==5.3.2
geojson==3.2.0
python-magic==0.4.27
google-cloud-storage==2.13.0
psycopg2-binary==2.9.9
SQLAlchemy==2.0.25
Flask-SQLAlchemy==3.1.1
```

> **Note**: Use `python-magic==0.4.27` (not `python-magic-bin`) for Python 3.12 on Linux/Cloud Run. The `python-magic-bin` package doesn't support Python 3.12.

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for python-magic and psycopg2
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY models.py .
COPY init_db.py .

# Default port for Cloud Run
ENV PORT=8080

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 app:app
```

### Key Flask App Patterns (app.py)

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow requests from your static site
CORS(app, origins=[
    "https://www.geoglypha1.org",
    "https://geoglypha1.org",
    "http://localhost:*"
])

@app.route('/')
def index():
    return jsonify({"status": "Geoglypha API is running"})

# Add your endpoints here...

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### .gcloudignore

Controls which files are **excluded** from deployment. Only deploy what the API needs:

```
.git
.gitignore
.claude
.vscode
node_modules/
images/
graphita/
weather/
docs/
data/
*.geojson
*.html
*.md
*.ps1
*.json
*.jpg
*.jpeg
*.png
*.webp
*.css
*.js
!cunescript.js
*.mhtml
*.txt
!requirements.txt
*.kml
*.xls
Dockerfile
.dockerignore
```

The `!filename` syntax means "DO include this file" even though the wildcard would exclude it.

---

## Google Cloud Run Deployment

### Step 1: Deploy the Service

From the project root directory:

```bash
gcloud run deploy geoglypha-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars BUCKET_NAME=www.geoglypha1.org
```

This command:
- Builds a Docker container using Cloud Build
- Pushes it to Artifact Registry
- Deploys it to Cloud Run
- Makes it publicly accessible (no auth required)

### Step 2: Verify Deployment

```bash
# Get the direct Cloud Run URL
gcloud run services describe geoglypha-api --region us-central1 --format="value(status.url)"
```

Visit the URL in your browser. You should see:
```json
{"status": "Geoglypha API is running", "endpoints": {...}}
```

### Step 3: Redeploying Updates

After making changes to `app.py` or other files, redeploy with the same command:

```bash
gcloud run deploy geoglypha-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Cloudflare DNS Routing

### Step 1: Create Domain Mapping in Google Cloud

```bash
gcloud beta run domain-mappings create \
  --service geoglypha-api \
  --domain tools.geoglypha1.org \
  --region us-central1
```

This tells Google Cloud Run to accept traffic for `tools.geoglypha1.org` and returns the required DNS record:

```
NAME: tools
RECORD TYPE: CNAME
CONTENTS: ghs.googlehosted.com.
```

### Step 2: Configure Cloudflare DNS

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select the `geoglypha1.org` domain
3. Go to **DNS** > **Records**
4. Add a new record:
   - **Type**: CNAME
   - **Name**: `tools`
   - **Target**: `ghs.googlehosted.com`
   - **Proxy status**: **DNS only** (gray cloud icon)

> **IMPORTANT**: The proxy status MUST be **DNS only** (gray cloud), NOT **Proxied** (orange cloud). Google needs direct access to the domain to provision and renew the SSL certificate. If you use Cloudflare's proxy, the certificate challenge will fail.

### Step 3: Wait for SSL Certificate

Google automatically provisions a managed SSL certificate. This typically takes **15-30 minutes** but can take up to 24 hours.

Check status:

```bash
gcloud beta run domain-mappings describe \
  --domain tools.geoglypha1.org \
  --region us-central1 \
  --format="value(status.conditions)"
```

**Certificate pending** (not ready yet):
```
'reason': 'CertificatePending', 'status': 'Unknown'
```

**Certificate provisioned** (ready):
```
'type': 'CertificateProvisioned', 'status': 'True'
```

### Adding More Subdomains

To add another app (e.g., `maps.geoglypha1.org`):

1. Deploy a new Cloud Run service:
   ```bash
   gcloud run deploy geoglypha-maps --source . --region us-central1 --allow-unauthenticated
   ```

2. Create domain mapping:
   ```bash
   gcloud beta run domain-mappings create \
     --service geoglypha-maps \
     --domain maps.geoglypha1.org \
     --region us-central1
   ```

3. Add CNAME in Cloudflare: `maps` -> `ghs.googlehosted.com` (DNS only)

4. Wait for SSL certificate provisioning

---

## SSL Certificate

### How It Works

- Google Cloud Run provides **free, auto-managed SSL certificates** via Let's Encrypt
- Certificates auto-renew before expiration (~90-day cycle)
- No manual action required

### Requirements to Keep It Working

1. CNAME record stays pointed at `ghs.googlehosted.com`
2. Cloudflare proxy status stays as **DNS only** (gray cloud)
3. Cloud Run service remains deployed
4. Domain mapping is not deleted

### If Certificate Stops Working

If the certificate expires or stops working:

```bash
# Delete the old mapping
gcloud beta run domain-mappings delete \
  --domain tools.geoglypha1.org \
  --region us-central1 --quiet

# Recreate it
gcloud beta run domain-mappings create \
  --service geoglypha-api \
  --domain tools.geoglypha1.org \
  --region us-central1
```

This resets the certificate provisioning process. Wait 15-30 minutes for the new certificate.

---

## Maintenance & Troubleshooting

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `CertificatePending` won't resolve | Cloudflare proxy is orange (proxied) | Switch to DNS only (gray cloud) |
| `Resource readiness deadline exceeded` | Stale domain mapping | Delete and recreate the mapping |
| `python-magic-bin` install fails | Not available for Python 3.12 | Use `python-magic==0.4.27` instead |
| `python39 is end of support` | Python 3.9 runtime deprecated | Use `python312` in app.yaml |
| Staging bucket permissions error | Service account lacks access | Grant `roles/storage.objectAdmin` |
| Logs permission error | Service account can't write logs | Grant `roles/logging.logWriter` |
| CORS errors from frontend | Origin not in allowed list | Add domain to `CORS(app, origins=[...])` |

### Viewing Logs

```bash
# Stream live logs
gcloud run services logs read geoglypha-api --region us-central1 --limit 50

# Or use the Cloud Console
# https://console.cloud.google.com/run/detail/us-central1/geoglypha-api/logs
```

### Checking Service Health

```bash
# Service status
gcloud run services describe geoglypha-api --region us-central1

# Domain mapping status
gcloud beta run domain-mappings describe \
  --domain tools.geoglypha1.org \
  --region us-central1 \
  --format="value(status.conditions)"

# DNS resolution
nslookup tools.geoglypha1.org
```

---

## Quick Reference Commands

```bash
# === DEPLOYMENT ===
# Deploy/update the API
gcloud run deploy geoglypha-api --source . --region us-central1 --allow-unauthenticated

# === DOMAIN MANAGEMENT ===
# List domain mappings
gcloud beta run domain-mappings list --region us-central1

# Check domain status
gcloud beta run domain-mappings describe --domain tools.geoglypha1.org --region us-central1

# Reset domain mapping (if certificate issues)
gcloud beta run domain-mappings delete --domain tools.geoglypha1.org --region us-central1 --quiet
gcloud beta run domain-mappings create --service geoglypha-api --domain tools.geoglypha1.org --region us-central1

# === MONITORING ===
# View logs
gcloud run services logs read geoglypha-api --region us-central1 --limit 50

# Check service URL
gcloud run services describe geoglypha-api --region us-central1 --format="value(status.url)"

# === STATIC SITE (GCS) ===
# Upload a file to the static site bucket
gsutil cp filename.html gs://www.geoglypha1.org/

# Make a file publicly readable
gsutil acl ch -u AllUsers:R gs://www.geoglypha1.org/filename.html

# List bucket contents
gsutil ls gs://www.geoglypha1.org/
```

---

## Current Live Services

| Service | URL | Host |
|---------|-----|------|
| Static Site | https://www.geoglypha1.org | GCS Bucket + Cloudflare |
| API (direct) | https://geoglypha-api-941611175760.us-central1.run.app | Cloud Run |
| API (custom domain) | https://tools.geoglypha1.org | Cloud Run + Cloudflare DNS |

---

*Last updated: February 2026*

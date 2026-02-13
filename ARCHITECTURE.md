# Geoglypha Architecture Guide

## Overview

Geoglypha uses a hybrid architecture with static hosting for the frontend and Cloud Run for dynamic API services.

```
                    Cloudflare DNS
                         |
          +--------------+--------------+
          |                             |
    www.geoglypha1.org           tools.geoglypha1.org
          |                             |
   Google Cloud Storage           Google Cloud Run
   (Static Frontend)              (Flask API)
```

## Components

### 1. Static Frontend (GCS)
- **Domain**: `www.geoglypha1.org`
- **Host**: Google Cloud Storage bucket `www.geoglypha1.org`
- **Content**: HTML, CSS, JS, images, GeoJSON files
- **Managed by**: Cloudflare (DNS + CDN)

### 2. API Backend (Cloud Run)
- **Domain**: `tools.geoglypha1.org`
- **Service**: `geoglypha-api`
- **Region**: `us-central1`
- **Direct URL**: `https://geoglypha-api-941611175760.us-central1.run.app`
- **Container**: `us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest`

## Cloudflare DNS Configuration

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `www` | `c.storage.googleapis.com` | Proxied (orange) |
| CNAME | `tools` | `ghs.googlehosted.com.` | DNS only (gray) |

**Important**: The `tools` subdomain must be DNS-only (gray cloud) for Google's SSL certificate to provision correctly.

## How Requests Flow

### Static Page Request
```
User -> www.geoglypha1.org/kml_to_geojson.html
     -> Cloudflare CDN
     -> GCS Bucket
     -> Returns HTML/CSS/JS
```

### API Request (KML Conversion)
```
User uploads KML file on kml_to_geojson.html
     -> JavaScript POST to tools.geoglypha1.org/upload
     -> Cloudflare DNS (passthrough)
     -> Cloud Run container
     -> Flask processes KML -> GeoJSON
     -> Returns JSON response
```

## Adding New Geoprocessing Tools

### Step 1: Add Flask Endpoint

Edit `app.py` to add new routes:

```python
@app.route('/api/buffer', methods=['POST'])
def buffer_geometry():
    """Buffer a GeoJSON geometry by a given distance"""
    data = request.get_json()
    geojson = data.get('geojson')
    distance = data.get('distance', 100)  # meters
    # Process with shapely or similar
    return jsonify({'result': buffered_geojson})

@app.route('/api/attributes', methods=['POST'])
def manipulate_attributes():
    """Add, edit, or delete GeoJSON properties"""
    data = request.get_json()
    # Process attributes
    return jsonify({'result': modified_geojson})
```

### Step 2: Rebuild & Deploy

```powershell
# Rebuild Docker image
docker build -t geoglypha-api .

# Tag for Artifact Registry
docker tag geoglypha-api us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest

# Push to registry
docker push us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest

# Deploy to Cloud Run (auto-pulls latest)
gcloud run deploy geoglypha-api \
  --image us-central1-docker.pkg.dev/precise-equator-411516/geoglypha/api:latest \
  --region us-central1
```

### Step 3: Create Frontend Page

Create a new HTML file (e.g., `buffer_tool.html`) that calls the API:

```javascript
fetch('https://tools.geoglypha1.org/api/buffer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ geojson: myGeojson, distance: 500 })
})
.then(response => response.json())
.then(data => displayOnMap(data.result));
```

### Step 4: Upload to GCS

```powershell
gsutil cp buffer_tool.html gs://www.geoglypha1.org/
```

## Future Tool Ideas

| Tool | Endpoint | Description |
|------|----------|-------------|
| Buffer | `/api/buffer` | Create buffer zones around features |
| Simplify | `/api/simplify` | Reduce geometry complexity |
| Dissolve | `/api/dissolve` | Merge adjacent polygons |
| Clip | `/api/clip` | Clip features to boundary |
| Attribute Editor | `/api/attributes` | Add/edit/delete properties |
| Attribute Table | `/api/table` | View/export feature attributes |
| Style Generator | `/api/style` | Generate Leaflet/Mapbox styles |

## Python Libraries for Geoprocessing

Add to `requirements.txt`:

```
shapely>=2.0.0      # Geometry operations
pyproj>=3.0.0       # Coordinate transformations
geopandas>=0.14.0   # GeoDataFrame operations
rasterio>=1.3.0     # Raster processing (if needed)
```

## Environment Variables

Cloud Run supports environment variables for configuration:

```bash
gcloud run services update geoglypha-api \
  --set-env-vars "MAX_UPLOAD_SIZE=32MB,DEBUG=false" \
  --region us-central1
```

## Monitoring

View logs and metrics:
- **Cloud Console**: https://console.cloud.google.com/run?project=precise-equator-411516
- **CLI**: `gcloud run services logs read geoglypha-api --region us-central1`

## Cost Considerations

- **Cloud Run**: Pay per request, first 2M requests/month free
- **Artifact Registry**: ~$0.10/GB/month storage
- **GCS**: Static hosting is very cheap (~$0.02/GB/month)
- **Cloudflare**: Free tier covers most needs

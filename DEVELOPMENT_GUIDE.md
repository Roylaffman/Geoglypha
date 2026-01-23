# Geoglypha Development Guide

## Site Architecture

```
www.geoglypha1.org (GCS Bucket + Cloudflare)
├── index.html                    ← Main homepage
├── history.html                  ← History hub page
├── cahokia.html                  ← Cahokia Mounds project
├── stonehenge.html               ← Stonehenge 3D model
├── cuneiform.html                ← Cuneiform translator
├── alphabet_evolution.html       ← Alphabet evolution
├── ceremonial_magic.html         ← Ceremonial magic
├── geoglyph_visualization.html   ← Geoglyph map (fetches from API)
├── kml_to_geojson.html           ← KML converter UI (calls tools subdomain)
├── graphita/                     ← Lo-fi art gallery
├── images/                       ← Project images
├── weather/                      ← Weather charts (also on weather subdomain)
└── *.geojson                     ← GeoJSON data files

weather.geoglypha1.org (Separate GCS Bucket)
├── index.html                    ← Weather landing page
├── temperature_chart.html
├── precipitation_chart.html
├── wind_speed_chart.html
├── barometric_pressure_chart.html
└── slide.html                    ← Title slide

tools.geoglypha1.org (Google Cloud Run)
├── POST /upload                  ← KML/KMZ file upload → GeoJSON
├── POST /download                ← GeoJSON download
├── GET  /api/geoglyphs           ← All geoglyph points (GeoJSON)
└── GET  /api/geoglyphs/<id>      ← Single geoglyph detail
```

## Hosting Setup

| Component | Host | Config |
|-----------|------|--------|
| Main static site | GCS bucket `www.geoglypha1.org` | Cloudflare DNS CNAME → `c.storage.googleapis.com` |
| Weather subdomain | GCS bucket `weather.geoglypha1.org` | Cloudflare CNAME → `c.storage.googleapis.com` |
| Tools/API subdomain | Google Cloud Run | Cloudflare CNAME → Cloud Run service URL |
| Database | Cloud SQL (PostgreSQL 15 + PostGIS) | Connected to Cloud Run via Unix socket |

## Design System

- **Primary color:** `#3a6351` (dark green — header, footer, nav)
- **Secondary color:** `#f2edd7` (cream — section backgrounds, hover states)
- **Accent color:** `#a0937d` (tan — buttons, highlights)
- **Text color:** `#333`
- **Header font:** Georgia, serif
- **Body font:** Arial, sans-serif
- **Map library:** Leaflet.js v1.9.4 (via CDN)
- **Charts:** Chart.js for simple charts, D3.js for custom visualizations

## How to Add a New Static Page

1. Create a new HTML file at the root level (e.g., `my_project.html`)
2. Use the same header/footer pattern as `index.html`:
   ```html
   <header>
     <div class="container header-content">
       <div class="logo"><a href="index.html">Geoglypha</a></div>
       <button class="mobile-menu-btn">☰</button>
       <nav>
         <ul>
           <li><a href="index.html">Home</a></li>
           <li><a href="cahokia.html">Cahokia</a></li>
           <!-- ... other nav links ... -->
         </ul>
       </nav>
     </div>
   </header>
   ```
3. Include the same CSS variables and responsive styles
4. Add a link to the new page from `index.html` (in the Projects grid or nav)
5. Upload to GCS: `gsutil cp my_project.html gs://www.geoglypha1.org/`

## How to Add a New Interactive Map Page

1. Create the HTML file with Leaflet.js:
   ```html
   <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
   <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
   ```
2. Add a `<div id="map">` with appropriate height
3. Load data either:
   - **Static:** Include a `.geojson` file at root level, fetch it with `fetch('mydata.geojson')`
   - **Dynamic:** Fetch from the API at `https://tools.geoglypha1.org/api/...`
4. Use `L.geoJSON()` to render the data on the map

## How to Add a New API Endpoint

1. Edit `app.py` and add a new route:
   ```python
   @app.route('/api/my-endpoint', methods=['GET'])
   def my_endpoint():
       # Query database or process data
       return jsonify(result)
   ```
2. If it needs database access, add a model in `models.py`
3. Rebuild and deploy:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/geoglypha-tools
   gcloud run deploy geoglypha-tools --image gcr.io/PROJECT_ID/geoglypha-tools ...
   ```

## How to Add a New Subdomain App

For a new subdomain (e.g., `maps.geoglypha1.org`):

### Option A: Static content (GCS bucket)
```bash
# Create bucket named after the subdomain
gsutil mb gs://maps.geoglypha1.org
gsutil iam ch allUsers:objectViewer gs://maps.geoglypha1.org
gsutil web set -m index.html -e 404.html gs://maps.geoglypha1.org

# Upload files
gsutil -m cp -r my-app/* gs://maps.geoglypha1.org/

# Add Cloudflare DNS record:
# Type: CNAME, Name: maps, Content: c.storage.googleapis.com, Proxy: ON
```

### Option B: Dynamic app (Cloud Run)
```bash
# Create a Dockerfile in your app directory
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/my-app
gcloud run deploy my-app \
    --image gcr.io/PROJECT_ID/my-app \
    --platform managed --region us-central1 \
    --allow-unauthenticated

# Map custom domain
gcloud run domain-mappings create --service my-app --domain maps.geoglypha1.org

# Add Cloudflare DNS record:
# Type: CNAME, Name: maps, Content: <cloud-run-service-url>, Proxy: ON
```

### Option C: AWS (S3 + CloudFront)
```bash
# Create S3 bucket
aws s3 mb s3://maps.geoglypha1.org

# Enable static website hosting
aws s3 website s3://maps.geoglypha1.org --index-document index.html

# Create CloudFront distribution pointing to the bucket
# Add Cloudflare CNAME pointing to the CloudFront distribution domain
```

## How to Add New Research Content

### Adding a new project card to the homepage:
Edit `index.html` and add a new card in the `.projects-grid`:
```html
<div class="project-card">
    <div class="project-img" style="background-image: url('images/my-image.jpg');"></div>
    <div class="project-content">
        <h3>Project Title</h3>
        <p>Short description of the project.</p>
        <a href="my_project.html" class="btn">Explore</a>
    </div>
</div>
```

### Adding to the History hub:
Edit `history.html` and add a new card in the card grid following the same pattern.

### Adding weather/climate analysis:
1. Create a new chart page in `weather/` following the template of existing charts
2. Add a nav link in all weather pages
3. Add a card on `weather/index.html`
4. Upload to the weather GCS bucket

### Adding geoglyph data points:
1. Prepare data with columns: name, type, latitude, longitude, description, folder_path
2. Insert into the `geoglyphs` table in Cloud SQL
3. Points will automatically appear on `geoglyph_visualization.html` via the API

## Deployment Workflows

### Update main static site:
```bash
# Upload specific files
gsutil cp index.html gs://www.geoglypha1.org/
gsutil cp history.html gs://www.geoglypha1.org/

# Or sync everything (be careful with this)
gsutil -m rsync -r -x 'node_modules|.git|__pycache__' . gs://www.geoglypha1.org/
```

### Update weather subdomain:
```bash
gsutil -m cp weather/* gs://weather.geoglypha1.org/
```

### Update Flask API (Cloud Run):
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/geoglypha-tools
gcloud run deploy geoglypha-tools --image gcr.io/PROJECT_ID/geoglypha-tools --region us-central1
```

### Invalidate Cloudflare cache (after updates):
Go to Cloudflare dashboard → Caching → Purge Everything (or purge specific URLs).

## Database Management

### Connect to Cloud SQL:
```bash
# Via Cloud SQL Auth Proxy
cloud-sql-proxy PROJECT_ID:us-central1:geoglypha-db &
psql -h 127.0.0.1 -U geoglypha_user -d geoglypha
```

### Run seed script:
```bash
python init_db.py
```

### Add PostGIS spatial queries:
```sql
-- Find geoglyphs within a bounding box
SELECT * FROM geoglyphs
WHERE ST_Within(geom, ST_MakeEnvelope(lon1, lat1, lon2, lat2, 4326));

-- Find geoglyphs near a point (within 10km)
SELECT *, ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography) as distance
FROM geoglyphs
WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography, 10000)
ORDER BY distance;
```

## Ideas for Future Growth

- **Google Earth Engine integration:** Add a subdomain for Earth Engine apps (ee.geoglypha1.org) using the Earth Engine JavaScript API
- **3D models:** Host Three.js or CesiumJS visualizations for archaeological sites
- **User contributions:** Add authentication and allow researchers to submit geoglyph coordinates
- **Timelines:** D3.js timeline visualizations for historical events
- **Image processing:** Add machine learning endpoints to Cloud Run for satellite image analysis
- **Data exports:** API endpoints that return data in multiple formats (GeoJSON, KML, CSV, Shapefile)

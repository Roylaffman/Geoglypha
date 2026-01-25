# Geoglypha Project Tasks

Last updated: 2026-01-24

## Completed

- [x] **Mobile responsiveness fix** — Headers and styles on phones fixed; media queries at 480px, 600px, 768px, 992px breakpoints ensure no text overlapping
- [x] **Connect weather folder to homepage** — Weather section added with cards linking to temperature, precipitation, wind speed, and barometric pressure charts; navigation and footer links included
- [x] **Create weather API dashboard** — Built `weather/dashboard.html` with:
  - Interactive Leaflet.js map centered on Asheville, NC (35.5951°N, 82.5515°W)
  - Current conditions from Open-Meteo API (temp, humidity, wind, precipitation)
  - 7-day forecast from NWS Weather.gov API
  - Historic data chart (past 7 days) showing temperature, precipitation, wind speed
  - NWS observation stations displayed on map
  - Auto-refresh every 5 minutes
  - Fully responsive design
  - Links added to homepage and weather index

## In Progress / Pending

### Deployment & Infrastructure

- [ ] **Republish files to GCS bucket** — Update live www.geoglypha1.org site via gcloud commands (walk through manually next session)
- [ ] **Get Flask backend working** — KML/KMZ to GeoJSON converter currently non-functional; connect through index.html
- [ ] **Host Flask app on cloud** — Deploy to AWS EC2 or GCS/Cloud Run as subdomain (e.g., api.geoglypha1.org)
- [ ] **Set up subdomain routing** — Configure Cloudflare to route traffic to cloud-hosted applications

### Maintenance

- [ ] **Review and complete started projects** — Audit directory for in-progress work; complete or archive as needed

## Future Expansion Ideas

- Additional webmaps using Google Earth Engine
- More archaeological site interactive maps
- Expanded cuneiform tools

## Infrastructure Notes

- **Current production**: www.geoglypha1.org (GCS bucket + Cloudflare)
- **Target subdomains**: weather.geoglypha1.org, api.geoglypha1.org
- **Cloud options**: GCS/Cloud Run, AWS EC2/S3/CloudFront
## Notes and progress 
✅ Mobile responsiveness (already done)
✅ Weather folder connected to homepage (already done)
✅ Weather API dashboard — created weather/dashboard.html
Next Session:

Task: Republish files to GCS bucket using gcloud commands (manual walkthrough)
Bucket: www.geoglypha1.org
Goal: Push new dashboard and updated files to live Cloudflare site
Files ready to deploy:

weather/dashboard.html (new)
weather/index.html (updated nav + card)
index.html (updated weather section)
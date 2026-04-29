# Gallery

Infinite-scroll art gallery. Pulls high-res images from the Art Institute of
Chicago's public API alongside your own artwork and cartographic maps.

## File Structure

```
aic-gallery/
├── index.html          ← main page
├── style.css           ← all styles
├── gallery.js          ← API fetching, infinite scroll, lightbox, filters
├── your-images.json    ← YOUR artwork + maps manifest (edit this)
├── README.md
└── images/
    ├── maps/           ← your static map images
    └── artwork/        ← your artwork images
```

## Adding Your Work

Edit `your-images.json`. Each entry:

```json
{
  "title":  "Map or artwork title",
  "type":   "map" | "painting" | "drawing" | "photograph" | "print",
  "year":   "2024",
  "medium": "QGIS / Cartography",
  "credit": "Your Name",
  "src":    "images/maps/my-map-full.jpg",
  "thumb":  "images/maps/my-map-thumb.jpg",
  "link":   ""
}
```

**Image prep tips:**
- `src` — full resolution, aim for 1600–2400px on the long edge
- `thumb` — 600–800px wide, same aspect ratio (loads fast in grid)
- Format: JPG at 85% quality is fine for photos/maps; PNG for line art

Your images appear at the **top of the grid** and show up under the "maps"
filter for maps, and the matching type filter for artwork.

## Customizing the AIC Feed

In `gallery.js`, change `AIC_QUERY` to search for specific subjects:

```js
const AIC_QUERY = 'landscape';   // landscape paintings
const AIC_QUERY = 'portrait';    // portraits
const AIC_QUERY = 'chicago';     // Chicago imagery
const AIC_QUERY = '';            // broad public domain sweep
```

## Deploying to Google Cloud Storage

```bash
# 1. Create a bucket (if not already done)
gsutil mb -l us-central1 gs://your-gallery-bucket

# 2. Make bucket publicly readable
gsutil iam ch allUsers:objectViewer gs://your-gallery-bucket

# 3. Upload all files
gsutil -m cp -r . gs://your-gallery-bucket

# 4. Set index and error pages
gsutil web set -m index.html -e 404.html gs://your-gallery-bucket

# 5. (Optional) Point a custom domain via Cloud Load Balancer or Firebase Hosting
```

For a subdomain like `gallery.yoursite.com`:
- Use a Cloud Load Balancer with the bucket as backend
- Or use Firebase Hosting with GCS as a rewrite target

## Claude Code Fine-Tuning Suggestions

Prompt Claude Code with:

- "Add a search bar that filters the AIC results by keyword using the
  /artworks/search endpoint"
- "Add a shuffle mode that randomizes the AIC fetch order"
- "Replace the viewer count with a real-time Supabase Realtime counter"
- "Add a department filter dropdown using AIC's /departments endpoint"
- "Lazy-load full-res images in the lightbox instead of thumbnails"
- "Add keyboard arrow navigation between lightbox images"
- "Export the current visible grid as a curated JSON list"

## API Notes

- AIC API is free, no key required, 60 req/min per IP
- Only public domain artworks are fetched (`is_public_domain=true`)
- IIIF images support CORS — safe to hotlink from any domain
- Recommended size: 843px wide (cached, fast)
- Do not scrape more than one image at a time if downloading locally

## License

Your artwork and maps remain your own copyright.
AIC collection data and images are public domain unless otherwise noted.

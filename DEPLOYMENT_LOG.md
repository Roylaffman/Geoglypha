# Deployment Log

Tracks the state of every file across the GCS production bucket (`gs://www.geoglypha1.org`)
and the `Geoglypha` git repo. Update this file whenever you push to the bucket or merge a branch.

The canonical map registry is at `C:\Users\royla\Documents\projects\maps.json` — that file
tracks all map pages with metadata, GCS timestamps, and source paths. This log covers the
broader site (nav pages, tools, galleries) that maps.json does not.

The authoritative cross-project deployment log is at:
`C:\Users\royla\Documents\projects\Docs\DEPLOYMENT_LOG.md`
Keep both in sync. The projects/Docs version is the source of truth for GIS/Quarto pushes.

## How to update

After any `gsutil cp` upload, add a row under the relevant section with today's date.
After a branch merge, update the git column.

Source key: **[GEO]** = Geoglypha site project (`C:\Users\royla\OneDrive\Documents\2.9Dev\Geoglypha\`) | **[GIS]** = GIS/Quarto project (`C:\Users\royla\Documents\projects\`)

## Production bucket — site shell

| File | GCS last pushed | Git branch (current) | Notes |
|------|----------------|---------------------|-------|
| index.html | 2026-04-11 | design-system-refactor | Argonauts link updated 2026-05-06 |
| geography.html | 2026-05-08 | design-system-refactor | Bagan card added 2026-05-08 |
| history.html | 2026-05-10 | main | Koh Ker card added 2026-05-10 |
| stack.html | 2026-04-11 | design-system-refactor | |
| supplies.html | 2026-04-11 | design-system-refactor | |
| cahokia.html | 2026-02-16 | design-system-refactor | Needs re-push after branch merge |
| cuneiform.html | 2026-01-11 | design-system-refactor | Needs re-push after branch merge |
| alphabet_evolution.html | 2026-01-25 | design-system-refactor | Needs re-push after branch merge |
| stonehenge.html | 2026-01-11 | design-system-refactor | Needs re-push after branch merge |
| geoglyph_visualization.html | 2026-01-25 | design-system-refactor | Needs re-push after branch merge |
| kml_to_geojson.html | 2026-03-15 | main | |
| 404.html | 2026-01-11 | main | |

## Production bucket — maps (summary; full record in maps.json)

| Slug | File | GCS last pushed | Source | Status |
|------|------|----------------|--------|--------|
| argonauts-route-roads | argonauts-route-roads.html | 2026-04-17 | [GEO] | live — canonical |
| argonauts_map | argonauts_map.html | 2026-05-01 | [GEO] | live — OLD build, links replaced |
| chimney-rock | chimney-rock.html | 2026-04-11 | [GEO] | live |
| angkor-barays | angkor-barays.html | 2026-05-12 | [GEO] | live — companion links (Flow Network Map + Analysis Dashboard) added, parchment map wrappers |
| angkor-hydraulic-map | angkor-hydraulic-map.html | 2026-04-28 | [GIS] | live — OSM coord fix (Indratataka, East Baray, Srah Srang) |
| angkor-sedimentation-timeline-charts | angkor-sedimentation-timeline-charts.html | 2026-05-04 | [GIS] | live — chart label + legend fixes |
| forest-carbon | forest-carbon.html | 2026-05-06 | [GEO] | live — updated |
| outlaw-trail | outlaw-trail.html | 2026-04-03 | [GEO] | live |
| sino-tibetan-towers | sino-tibetan-towers.html | 2026-03-10 | [GEO] | live |
| americas-minerals | americas-minerals.html | 2026-03-10 | [GEO] | live |
| everglades-history | everglades-history.html | 2026-03-10 | [GEO] | live |
| rana-boylii-map | rana-boylii-map.html | 2026-04-11 | [GEO] | live |
| yamnaya-report | yamnaya-report.html | 2026-04-26 | [GIS] | live — new report pushed from GIS project |
| bagan-empire | bagan-empire.html | 2026-05-08 | [GIS] | live — Bagan story map, 5 map layers, Esri Topo basemap |
| storyboard | storyboard.html | 2026-04-04 | [GEO] | live |
| outlaw-trail-map | outlaw-trail-map.html | 2026-04-11 | [GEO] | live |
| angkor-barays-presentation | angkor-barays-presentation.html | 2026-03-10 | [GEO] | live |
| lithium-analysis | lithium_analysis.html | 2026-05-12 | [GEO] | live — user-refactored, self-contained with PDF |
| petra-nabataean-atlas | petra-nabataean-atlas.html | 2026-05-19 | [GIS] | live — Petra & the Nabataeans atlas, self-contained 95.4 KB |

## GIS / Quarto Project push history

Pushes originating from `C:\Users\royla\Documents\projects\` to `gs://www.geoglypha1.org`. Cross-referenced with **[GIS]** tag in the maps table above. The maps.json manifest is the canonical slug registry and is uploaded alongside every map push.

| Date | File(s) pushed | Bucket path | Notes |
|------|---------------|-------------|-------|
| 2026-04-26 | yamnaya-report.html, maps.json | gs://www.geoglypha1.org/ | New Yamnaya Bronze Age migration story map. Manifest entry added via manage_manifest.py. |
| 2026-04-28 | angkor-hydraulic-map.html | gs://www.geoglypha1.org/ | OSM coordinate enrichment via Overpass API. Indratataka corrected by -6.5 km, East Baray and Srah Srang nodes also fixed. Scripts: Scripts/enrich_angkor_coords.py, Scripts/patch_angkor_html.py. |
| 2026-05-04 | angkor-sedimentation-timeline-charts.html | gs://www.geoglypha1.org/ | Chart fixes: Tab 1 drought labels staggered, Siamese Sack moved to row 3, System Capacity legend shifted left to clear East Baray Fails milestone label. |
| 2026-05-08 | bagan-empire.html, maps.json | gs://www.geoglypha1.org/ | New Bagan story map. Self-contained (map inlined as data URI). Layers: OSM monuments 1,365 footprints, waterways 131, Zamani Project 12, CyArk 8. Esri World Topo default basemap. |
| 2026-05-08 | geography.html, maps.json | gs://www.geoglypha1.org/ | Bagan card added to geography.html. maps.json page field corrected to geography. |
| 2026-05-08 | assets/css/design-system.css | gs://www.geoglypha1.org/assets/css/ | CSS was missing from bucket — caused unstyled geography.html. Now live at /assets/css/design-system.css. |
| 2026-05-08 | images/bagan-card.jpg | gs://www.geoglypha1.org/images/ | New Bagan card thumbnail. geography.html updated from west-baray.jpg. [GEO] |
| 2026-05-08 | angkor-barays.html | gs://www.geoglypha1.org/ | Editorial parchment theme (bagan-empire style). Source: Analysis/angkor-barays.qmd + angkor-barays.scss. [GIS] |
| 2026-05-19 | petra-nabataean-atlas.html | gs://www.geoglypha1.org/ | Petra & the Nabataeans: An Atlas of the Rose-Red City and the Incense Road. 95.4 KB, self-contained HTML. Source: Analysis/petra-nabataean-atlas.html [GIS]. Copy placed in Geoglypha/docs/. |

## Production bucket — galleries

| Path | GCS last pushed | Notes |
|------|----------------|-------|
| gallery/index.html | bucket-only before 2026-05-05 | Added to git 2026-05-05 |
| gallery/gallery.js | bucket-only before 2026-05-05 | Added to git 2026-05-05 |
| gallery/style.css | bucket-only before 2026-05-05 | Added to git 2026-05-05 |
| gallery/your-images.json | bucket-only before 2026-05-05 | Currently empty [] |
| graphita/index.html | 2026-04-11 (approx) | design-system-refactor |
| graphita/gallery.js | 2026-04-11 (approx) | main |
| graphita/your-images.json | 2026-04-11 (approx) | 62 entries |

## Production bucket — weather

| File | GCS last pushed | Notes |
|------|----------------|-------|
| weather/index.html | 2026-04-11 (approx) | design-system-refactor |
| weather/dashboard.html | 2026-01 (approx) | main |
| weather/temperature_chart.html | 2026-05-10 | main | Refactored to design-system.css — Cinzel/Cormorant Garamond, parchment bg, footer added |
| weather/precipitation_chart.html | 2026-05-10 | main | Refactored to design-system.css — D3 fonts updated, parchment tooltip, footer added |
| weather/wind_speed_chart.html | 2026-05-10 | main | Refactored to design-system.css — Cinzel/Cormorant Garamond, parchment bg, footer added |
| weather/barometric_pressure_chart.html | 2026-05-10 | main | Refactored to design-system.css — Cinzel/Cormorant Garamond, parchment bg, footer added |

## Git branches

| Branch | State | Description |
|--------|-------|-------------|
| main | production | Last deployed batch: 2026-04-11 |
| design-system-refactor | in development | Full site editorial redesign — not yet merged or deployed as a batch |

## Files in git not yet pushed to bucket

These exist on `design-system-refactor` and need deployment after merge:

- `assets/css/design-system.css` — shared stylesheet, required by all refactored pages
- `cahokia.html`, `cuneiform.html`, `alphabet_evolution.html`, `stonehenge.html`, `geoglyph_visualization.html`
- `gallery/` directory (all files)
- `argonauts-route-roads.html` — already in bucket from 2026-04-17; branch version has no nav changes

## Deployment command reference

Push a single file:
```
gsutil cp <file> gs://www.geoglypha1.org/<file>
```

Push the full shell (index, geography, history, stack, supplies, css):
```
gsutil -m cp index.html geography.html history.html stack.html supplies.html gs://www.geoglypha1.org/
gsutil -m cp assets/css/design-system.css gs://www.geoglypha1.org/assets/css/design-system.css
```

Push gallery/:
```
gsutil -m cp -r gallery/ gs://www.geoglypha1.org/gallery/
```

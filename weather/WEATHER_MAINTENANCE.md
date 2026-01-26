# Weather Dashboard - Maintenance & Upgrade Guide

## Overview

The Geoglypha Weather Dashboard displays real-time and historic weather data for West Asheville, NC. It uses two free APIs that require no authentication keys.

## Data Sources

### Open-Meteo API
- **URL**: https://open-meteo.com/
- **Cost**: Free (no API key required)
- **Rate Limits**: 10,000 requests/day for non-commercial use
- **Data Provided**:
  - Current conditions (temperature, humidity, wind, precipitation, pressure)
  - Hourly historical data (up to 7 days back)
  - Forecast data
- **Documentation**: https://open-meteo.com/en/docs

### NWS Weather.gov API
- **URL**: https://api.weather.gov/
- **Cost**: Free (no API key required)
- **Rate Limits**: No strict limits, but include User-Agent header
- **Data Provided**:
  - 7-day forecasts
  - Observation station locations
  - Current observations from stations
- **Documentation**: https://www.weather.gov/documentation/services-web-api

## File Structure

```
weather/
├── dashboard.html          # Main live dashboard with map
├── index.html              # Weather overview/landing page
├── temperature_chart.html  # Historic temperature analysis
├── precipitation_chart.html # Historic precipitation analysis
├── wind_speed_chart.html   # Historic wind analysis
├── barometric_pressure_chart.html # Historic pressure analysis
├── slide.html              # Presentation slides
└── WEATHER_MAINTENANCE.md  # This file
```

## Dashboard Features

### Current Location
- **Center Point**: West Asheville / Haywood Road (35.5847°N, 82.5879°W)
- **Search Radius**: 5 miles
- Displayed as a dashed circle on the map

### Weather Stations
- Stations are fetched from NWS API on page load
- Only stations within 5-mile radius are displayed
- Click station markers or use dropdown to select
- Selected station highlights in red
- Data refreshes for selected station location

### Data Display
| Metric | Source | Refresh Rate |
|--------|--------|--------------|
| Temperature | Open-Meteo | 5 minutes |
| Humidity | Open-Meteo | 5 minutes |
| Wind Speed | Open-Meteo | 5 minutes |
| Precipitation | Open-Meteo | 5 minutes |
| Barometric Pressure | Open-Meteo | 5 minutes |
| 7-Day Forecast | NWS | Page load |
| Historic Chart | Open-Meteo | Page load |

## Common Maintenance Tasks

### Changing the Center Location
Edit `dashboard.html` and update these constants:

```javascript
const WEST_ASHEVILLE_LAT = 35.5847;  // New latitude
const WEST_ASHEVILLE_LON = -82.5879; // New longitude
```

### Changing the Search Radius
Edit `dashboard.html`:

```javascript
const SEARCH_RADIUS_MILES = 5;  // Change to desired radius
```

### Adding New Weather Metrics
1. Add the metric to the Open-Meteo API URL in `fetchCurrentWeather()`:
   ```javascript
   &current=temperature_2m,NEW_METRIC
   ```
2. Add display HTML in the current-conditions div
3. For charts, add to `fetchHistoricalData()` URL and `renderHistoryChart()`

### Updating Chart Colors
In `renderHistoryChart()`, modify the `borderColor` values:
- Temperature: `#FF9A73` (orange)
- Precipitation: `#5b9bd5` (blue)
- Wind: `#7a9a8a` (green)
- Pressure: `#9b59b6` (purple)

## Deployment

### Push to Google Cloud Storage
```bash
# Upload single file
gsutil cp weather/dashboard.html gs://www.geoglypha1.org/weather/

# Upload entire weather folder
gsutil -m cp -r weather/* gs://www.geoglypha1.org/weather/
```

### Verify Deployment
Visit: https://www.geoglypha1.org/weather/dashboard.html

## Troubleshooting

### "Unable to load current conditions"
- Check browser console for API errors
- Verify Open-Meteo API is accessible
- Check if coordinates are valid

### "No stations within 5 miles"
- NWS may not have stations in the selected radius
- Try increasing `SEARCH_RADIUS_MILES`
- Check NWS API status

### Chart not rendering
- Ensure Chart.js CDN is loading
- Check browser console for JavaScript errors
- Verify historical data API response

### Map not loading
- Ensure Leaflet.js CDN is loading
- Check for JavaScript errors
- Verify OpenStreetMap tiles are accessible

## Future Upgrade Ideas

1. **Add more NWS station data**: Fetch actual observations from stations
2. **Radar overlay**: Add NWS radar tiles to the map
3. **Alerts**: Display active weather alerts for the area
4. **Export data**: Allow users to download CSV of historical data
5. **Mobile app**: Convert to PWA for offline access
6. **Multiple locations**: Allow users to save/compare locations

## API Reference Quick Links

- Open-Meteo Docs: https://open-meteo.com/en/docs
- NWS API Docs: https://www.weather.gov/documentation/services-web-api
- Leaflet.js Docs: https://leafletjs.com/reference.html
- Chart.js Docs: https://www.chartjs.org/docs/latest/

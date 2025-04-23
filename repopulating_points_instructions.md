# Instructions for Repopulating Points from Google Earth Engine Analysis

When you run your geoglyph analysis in Google Earth Engine, you'll need to export the results and integrate them into your visualization. Here's how to do it:

## Option 1: Export as GeoJSON and Load Dynamically

This is the recommended approach as it keeps your data separate from your HTML code, making it easier to update.

### Step 1: Export from Google Earth Engine
1. After running your analysis in Google Earth Engine, use the `Export.table.toDrive()` function to export your features as a GeoJSON file:

```javascript
// Example Google Earth Engine code to export features
var features = ee.FeatureCollection('your_analyzed_features');

// Export to Google Drive as GeoJSON
Export.table.toDrive({
  collection: features,
  description: 'geoglyph_points',
  fileFormat: 'GeoJSON'
});
```

2. Download the GeoJSON file from your Google Drive.
3. Upload it to your Google Cloud Storage bucket alongside your HTML files.

### Step 2: Modify your HTML to load the GeoJSON file

Add this code to replace the existing point definitions in your geoglyph_visualization.html file:

```javascript
// Remove all the existing circle marker definitions and replace with this code
fetch('your_geoglyph_points.geojson')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("GeoJSON data loaded:", data);
    L.geoJSON(data, {
      pointToLayer: function (feature, latlng) {
        // Determine color based on feature type
        let markerColor = "gray";
        if (feature.properties.type && feature.properties.type.toLowerCase() === "circle") {
          markerColor = "red";
        }
        
        // Create circle marker
        return L.circleMarker(latlng, {
          radius: 5,
          fillColor: markerColor,
          color: markerColor,
          weight: 3,
          opacity: 1.0,
          fillOpacity: 0.2
        });
      },
      onEachFeature: function (feature, layer) {
        // Create popup content
        if (feature.properties) {
          let popupContent = '';
          if (feature.properties.name) {
            popupContent += `<div style="width: 100%; height: 100%;">Name: ${feature.properties.name}<br>`;
          }
          if (feature.properties.type) {
            popupContent += `Type: ${feature.properties.type}</div>`;
          } else {
            popupContent += `Type: unknown</div>`;
          }
          
          // Bind popup to layer
          layer.bindPopup(popupContent);
        }
      }
    }).addTo(map_11fa091a775d8bad7e200017eb6df400);
  })
  .catch(error => {
    console.error("Error loading or processing GeoJSON:", error);
  });
```

## Option 2: Generate JavaScript Code Directly from Google Earth Engine

If you prefer to have the points directly embedded in your HTML:

### Step 1: Create a custom export function in Google Earth Engine

```javascript
// Function to format feature collection as Leaflet marker code
function formatAsLeafletMarkers(featureCollection) {
  return featureCollection.map(function(feature) {
    var coords = feature.geometry().coordinates();
    var lat = coords.get(1);
    var lon = coords.get(0);
    var name = feature.get('name');
    var type = feature.get('type') || 'unknown';
    var color = (type.toLowerCase() === 'circle') ? 'red' : 'gray';
    
    var markerCode = 'var circle_marker_' + name.replace(/[^a-zA-Z0-9]/g, '') + ' = L.circleMarker(\n';
    markerCode += '    [' + lat + ', ' + lon + '],\n';
    markerCode += '    {"bubblingMouseEvents": true, "color": "' + color + '", "dashArray": null, "dashOffset": null, "fill": true, "fillColor": "' + color + '", "fillOpacity": 0.2, "fillRule": "evenodd", "lineCap": "round", "lineJoin": "round", "opacity": 1.0, "radius": 5, "stroke": true, "weight": 3}\n';
    markerCode += ').addTo(map_11fa091a775d8bad7e200017eb6df400);\n\n';
    
    markerCode += 'var popup_' + name.replace(/[^a-zA-Z0-9]/g, '') + ' = L.popup({\n';
    markerCode += '    "maxWidth": "100%",\n';
    markerCode += '});\n\n';
    
    markerCode += 'var html_' + name.replace(/[^a-zA-Z0-9]/g, '') + ' = $(`<div style="width: 100.0%; height: 100.0%;">Name: ' + name + '<br>Type: ' + type + '</div>`)[0];\n';
    markerCode += 'popup_' + name.replace(/[^a-zA-Z0-9]/g, '') + '.setContent(html_' + name.replace(/[^a-zA-Z0-9]/g, '') + ');\n\n';
    
    markerCode += 'circle_marker_' + name.replace(/[^a-zA-Z0-9]/g, '') + '.bindPopup(popup_' + name.replace(/[^a-zA-Z0-9]/g, '') + ');\n\n';
    
    return ee.String(markerCode);
  });
}

// Generate marker code
var features = ee.FeatureCollection('your_analyzed_features');
var markerCode = formatAsLeafletMarkers(features);

// Print to console (you'll need to copy this)
print(markerCode);

// Or export to a text file
Export.table.toDrive({
  collection: ee.FeatureCollection(markerCode.map(function(s) {
    return ee.Feature(null, {'code': s});
  })),
  description: 'leaflet_marker_code',
  fileFormat: 'CSV'
});
```

### Step 2: Copy the generated code

1. Copy the generated JavaScript code from the Earth Engine console or from the exported CSV file.
2. Replace the existing circle marker definitions in your HTML file with this code.

## Option 3: Use Folium in Python to Generate the HTML

If you're using Python with Earth Engine:

1. Export your features from Earth Engine to a GeoJSON file.
2. Use the Folium library to create a new map with your points:

```python
import folium
import json
import ee

# Initialize Earth Engine
ee.Initialize()

# Your Earth Engine analysis code here
# ...

# Export your features to GeoJSON (local file)
geojson_data = your_feature_collection.getInfo()

# Save to file
with open('geoglyph_points.geojson', 'w') as f:
    json.dump(geojson_data, f)

# Create a new map with Folium
m = folium.Map(
    location=[-11.766552999331651, -66.71029599290235],
    zoom_start=8
)

# Function to style points
def style_function(feature):
    feature_type = feature['properties'].get('type', '').lower()
    if feature_type == 'circle':
        return {
            'fillColor': 'red',
            'color': 'red',
            'fillOpacity': 0.2,
            'weight': 3
        }
    else:
        return {
            'fillColor': 'gray',
            'color': 'gray',
            'fillOpacity': 0.2,
            'weight': 3
        }

# Function to create popups
def popup_function(feature, layer):
    if feature['properties']:
        name = feature['properties'].get('name', 'Unknown')
        feature_type = feature['properties'].get('type', 'unknown')
        layer.bindPopup(f"Name: {name}<br>Type: {feature_type}")

# Add GeoJSON to map
folium.GeoJson(
    'geoglyph_points.geojson',
    style_function=style_function,
    popup=popup_function
).add_to(m)

# Save the map
m.save('new_geoglyph_visualization.html')
```

3. Copy the relevant parts from the generated HTML to update your existing file, or use the new file directly.

## Important Notes

1. Make sure your GeoJSON file is properly formatted with the expected properties (name, type).
2. The map ID (`map_11fa091a775d8bad7e200017eb6df400`) in the code should match the ID in your HTML file.
3. Test your visualization locally before uploading to Google Cloud Storage.
4. If your points have additional properties you want to display, modify the popup content accordingly.

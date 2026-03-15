from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import zipfile
import tempfile
import magic
from lxml import etree
from pykml import parser
import json
from geojson import Feature, FeatureCollection, Point, dumps
import io
import shutil

# For Google Cloud Storage integration
try:
    from google.cloud import storage
    USING_GCP = True
except ImportError:
    USING_GCP = False

# For database
try:
    from models import db, Geoglyph
    USING_DB = True
except ImportError:
    USING_DB = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# CORS configuration
CORS(app, origins=[
    'https://www.geoglypha1.org',
    'https://geoglypha1.org',
    'https://tools.geoglypha1.org',
    'http://localhost:*',
    'http://127.0.0.1:*'
])

# Database configuration
db_host = os.environ.get('DB_HOST', '')
db_name = os.environ.get('DB_NAME', 'geoglypha')
db_user = os.environ.get('DB_USER', 'geoglypha_user')
db_pass = os.environ.get('DB_PASS', '')

if db_host and USING_DB:
    if db_host.startswith('/cloudsql/'):
        # Cloud SQL Unix socket
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}'
            f'?host={db_host}'
        )
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}'
        )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

# Configure storage - either local or GCS
if USING_GCP:
    try:
        storage_client = storage.Client()
        bucket_name = os.environ.get('BUCKET_NAME')
        if bucket_name:
            bucket = storage_client.bucket(bucket_name)
        else:
            print("Warning: BUCKET_NAME environment variable not set")
            USING_GCP = False
    except Exception as e:
        print(f"Warning: Could not initialize GCS client: {e}")
        USING_GCP = False

# Fall back to local storage if GCS is not configured
if not USING_GCP:
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    print("Using local temp storage for uploads")


@app.route('/api')
def api_info():
    return jsonify({
        'service': 'Geoglypha Tools API',
        'version': '1.0.0',
        'endpoints': {
            'POST /upload': 'Upload KML/KMZ file, returns GeoJSON',
            'POST /download': 'Download GeoJSON as file',
            'GET /api/geoglyphs': 'List all geoglyph points as GeoJSON FeatureCollection',
            'GET /api/geoglyphs/<id>': 'Get single geoglyph detail'
        }
    })


HOMEPAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KML/KMZ to GeoJSON Converter - Geoglypha</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <style>
        :root {
            --primary-color: #3a6351;
            --secondary-color: #f2edd7;
            --accent-color: #a0937d;
            --text-color: #333;
            --light-text: #f5f5f5;
            --header-font: 'Georgia', serif;
            --body-font: 'Arial', sans-serif;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: var(--body-font); line-height: 1.6; color: var(--text-color); background-color: #f9f9f9; }
        .container { width: 90%; max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        header { background-color: var(--primary-color); color: var(--light-text); padding: 1rem 0; position: relative; }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-family: var(--header-font); font-size: 2rem; font-weight: bold; }
        .logo a { color: var(--light-text); text-decoration: none; }
        nav ul { display: flex; list-style: none; }
        nav ul li { margin-left: 1.5rem; }
        nav ul li a { color: var(--light-text); text-decoration: none; font-weight: 500; transition: color 0.3s; }
        nav ul li a:hover { color: var(--secondary-color); }
        .mobile-menu-btn { display: none; background: none; border: none; color: var(--light-text); font-size: 1.5rem; cursor: pointer; }
        .page-title { background-color: var(--secondary-color); padding: 2rem 0; text-align: center; }
        .page-title h1 { font-family: var(--header-font); font-size: 2.5rem; color: var(--primary-color); margin-bottom: 1rem; }
        .page-title p { max-width: 800px; margin: 0 auto; }
        .upload-section { margin: 20px 0; padding: 40px 20px; border: 2px dashed var(--accent-color); border-radius: 8px; text-align: center; background-color: white; transition: border-color 0.3s, background-color 0.3s; }
        .upload-section.drag-over { border-color: var(--primary-color); background-color: #f0f7f3; }
        .file-input { display: none; }
        .file-label { display: inline-block; padding: 10px 20px; background-color: var(--primary-color); color: white; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
        .file-label:hover { background-color: #2a4d3e; }
        .file-name { margin-top: 10px; font-style: italic; }
        .drag-text { margin-bottom: 15px; color: #888; font-size: 0.95rem; }
        .results-section { margin-top: 30px; display: none; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .map-container { height: 400px; margin: 20px 0; border-radius: 8px; overflow: hidden; border: 1px solid var(--accent-color); }
        #map { height: 100%; }
        .feature-list { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
        .feature-item { padding: 8px; border-bottom: 1px solid #eee; }
        .feature-item:last-child { border-bottom: none; }
        .download-btn { display: block; width: 100%; padding: 10px; background-color: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; transition: background-color 0.3s; }
        .download-btn:hover { background-color: #2a4d3e; }
        .loading { display: none; text-align: center; margin: 20px 0; }
        .spinner { border: 4px solid rgba(0,0,0,0.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: var(--primary-color); animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error-message { color: #f44336; margin: 10px 0; display: none; }
        .success-message { color: var(--primary-color); margin: 10px 0; display: none; }
        footer { background-color: var(--primary-color); color: var(--light-text); padding: 3rem 0 1.5rem; margin-top: 50px; }
        .footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-bottom: 2rem; }
        .footer-column h3 { font-family: var(--header-font); margin-bottom: 1.5rem; font-size: 1.2rem; }
        .footer-column ul { list-style: none; }
        .footer-column ul li { margin-bottom: 0.8rem; }
        .footer-column ul li a { color: var(--light-text); text-decoration: none; transition: color 0.3s; }
        .footer-column ul li a:hover { color: var(--secondary-color); }
        .copyright { text-align: center; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); }
        @media (max-width: 768px) {
            .header-content { flex-direction: column; text-align: center; }
            nav ul { margin-top: 1rem; flex-direction: column; align-items: center; }
            nav ul li { margin: 0.5rem 0; }
            .mobile-menu-btn { display: block; position: absolute; top: 1rem; right: 1rem; }
            nav { display: none; }
            nav.active { display: block; }
            #map { height: 300px; }
            .page-title h1 { font-size: 1.8rem; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <div class="logo"><a href="https://www.geoglypha1.org">Geoglypha</a></div>
            <button class="mobile-menu-btn">&#9776;</button>
            <nav>
                <ul>
                    <li><a href="https://www.geoglypha1.org">Home</a></li>
                    <li><a href="https://www.geoglypha1.org/geography.html">Geography</a></li>
                    <li><a href="https://www.geoglypha1.org/history.html">History</a></li>
                    <li><a href="https://www.geoglypha1.org/#projects">Projects</a></li>
                    <li><a href="https://www.geoglypha1.org/weather">Weather</a></li>
                    <li><a href="https://www.geoglypha1.org/graphita/graphitia.html">Gallery</a></li>
                    <li><a href="/">Tools</a></li>
                    <li><a href="https://www.geoglypha1.org/supplies.html" style="color:#D8B4FE;">Supplies</a></li>
                    <li><a href="https://www.geoglypha1.org/stack.html" style="color:#86EFAC;">Stack</a></li>
                    <li><a href="https://www.geoglypha1.org/#about">About</a></li>
                    <li><a href="https://www.geoglypha1.org/#contact">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>
    <section class="page-title">
        <div class="container">
            <h1>KML/KMZ to GeoJSON Converter</h1>
            <p>Upload your KML or KMZ files to convert them to GeoJSON format with preserved folder structure and descriptions.</p>
        </div>
    </section>
    <div class="container">
        <div class="upload-section" id="upload-section">
            <p class="drag-text">Drag &amp; drop your file here, or</p>
            <input type="file" id="file-input" class="file-input" accept=".kml,.kmz">
            <label for="file-input" class="file-label">Choose File</label>
            <div class="file-name" id="file-name">No file selected</div>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing file...</p>
            </div>
            <div class="error-message" id="error-message"></div>
            <div class="success-message" id="success-message"></div>
        </div>
        <div class="results-section" id="results-section">
            <h2>Conversion Results</h2>
            <div class="map-container"><div id="map"></div></div>
            <h3>Features Found</h3>
            <div class="feature-list" id="feature-list"></div>
            <button class="download-btn" id="download-btn">Download GeoJSON</button>
        </div>
    </div>
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-column">
                    <h3>Geoglypha</h3>
                    <p>Exploring Earth's Historical Landscapes through the lens of archaeology, history, and geography.</p>
                </div>
                <div class="footer-column">
                    <h3>Tools</h3>
                    <ul>
                        <li><a href="/">KML/KMZ Converter</a></li>
                        <li><a href="/api">API Reference</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Connect</h3>
                    <ul>
                        <li><a href="https://www.facebook.com/profile.php?id=61574222720588">Facebook</a></li>
                        <li><a href="https://www.instagram.com/geoglypha/">Instagram</a></li>
                        <li><a href="https://www.tiktok.com/@geoglypha">TikTok</a></li>
                        <li><a href="https://substack.com/@geoglypha">Substack</a></li>
                    </ul>
                </div>
            </div>
            <div class="copyright">
                <p>&copy; <span id="year"></span> Geoglypha. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script>
        let geojsonData = null, map = null, layerGroup = null;
        const API_BASE = window.location.origin;
        const fileInput = document.getElementById('file-input');
        const fileName = document.getElementById('file-name');
        const loading = document.getElementById('loading');
        const errorMessage = document.getElementById('error-message');
        const successMessage = document.getElementById('success-message');
        const resultsSection = document.getElementById('results-section');
        const featureList = document.getElementById('feature-list');
        const downloadBtn = document.getElementById('download-btn');
        const uploadSection = document.getElementById('upload-section');

        function initMap() {
            map = L.map('map').setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            layerGroup = L.layerGroup().addTo(map);
        }

        function displayGeoJSON(geojson) {
            layerGroup.clearLayers();
            L.geoJSON(geojson, {
                pointToLayer: function(feature, latlng) {
                    return L.circleMarker(latlng, { radius: 8, fillColor: "#3a6351", color: "#000", weight: 1, opacity: 1, fillOpacity: 0.8 });
                },
                onEachFeature: function(feature, layer) {
                    let popup = '<strong>' + (feature.properties.name || 'Unnamed') + '</strong>';
                    if (feature.properties.description) popup += '<p>' + feature.properties.description + '</p>';
                    if (feature.properties.folder_path) popup += '<p><em>Folder: ' + feature.properties.folder_path + '</em></p>';
                    layer.bindPopup(popup);
                }
            }).addTo(layerGroup);
            var bounds = layerGroup.getBounds();
            if (bounds.isValid()) map.fitBounds(bounds);
        }

        function displayFeatureList(geojson) {
            featureList.innerHTML = '';
            if (!geojson.features || geojson.features.length === 0) {
                featureList.innerHTML = '<p>No features found.</p>';
                return;
            }
            geojson.features.forEach(function(feature) {
                var div = document.createElement('div');
                div.className = 'feature-item';
                var html = '<strong>' + (feature.properties.name || 'Unnamed') + '</strong>';
                if (feature.properties.folder_path) html += '<br><em>Folder: ' + feature.properties.folder_path + '</em>';
                div.innerHTML = html;
                featureList.appendChild(div);
            });
        }

        function processFile(file) {
            fileName.textContent = file.name;
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
            resultsSection.style.display = 'none';
            loading.style.display = 'block';
            var formData = new FormData();
            formData.append('file', file);
            fetch(API_BASE + '/upload', { method: 'POST', body: formData })
                .then(function(r) {
                    if (!r.ok) return r.json().then(function(d) { throw new Error(d.error || 'Error processing file'); });
                    return r.json();
                })
                .then(function(data) {
                    loading.style.display = 'none';
                    geojsonData = data.geojson;
                    successMessage.textContent = data.message;
                    successMessage.style.display = 'block';
                    if (!map) initMap();
                    displayGeoJSON(geojsonData);
                    displayFeatureList(geojsonData);
                    resultsSection.style.display = 'block';
                })
                .catch(function(err) {
                    loading.style.display = 'none';
                    errorMessage.textContent = err.message;
                    errorMessage.style.display = 'block';
                });
        }

        fileInput.addEventListener('change', function(e) {
            if (e.target.files[0]) processFile(e.target.files[0]);
        });

        // Drag and drop
        uploadSection.addEventListener('dragover', function(e) { e.preventDefault(); uploadSection.classList.add('drag-over'); });
        uploadSection.addEventListener('dragleave', function() { uploadSection.classList.remove('drag-over'); });
        uploadSection.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadSection.classList.remove('drag-over');
            if (e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
        });

        downloadBtn.addEventListener('click', function() {
            if (!geojsonData) return;
            fetch(API_BASE + '/download', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ geojson: geojsonData }) })
                .then(function(r) { if (!r.ok) throw new Error('Download error'); return r.blob(); })
                .then(function(blob) {
                    var url = URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url; a.download = 'converted.geojson';
                    document.body.appendChild(a); a.click();
                    URL.revokeObjectURL(url);
                })
                .catch(function(err) { errorMessage.textContent = err.message; errorMessage.style.display = 'block'; });
        });

        document.getElementById('year').textContent = new Date().getFullYear();
        document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
            document.querySelector('nav').classList.toggle('active');
        });
    </script>
</body>
</html>"""


@app.route('/')
def index():
    return render_template_string(HOMEPAGE_HTML)


def extract_kmz(file_path):
    """Extract KMZ file to a temporary directory and return the KML file path."""
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    for file in os.listdir(temp_dir):
        if file.endswith('.kml'):
            return os.path.join(temp_dir, file)

    return None


def parse_kml(kml_path, folder_path=None):
    """Parse KML file and extract placemarks with folder information and all attributes."""
    with open(kml_path, 'rb') as f:
        root = parser.parse(f).getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    features = []

    def extract_extended_data(placemark):
        """Extract all ExtendedData fields (Data, SimpleData, SchemaData)."""
        props = {}
        ext = placemark.find('.//kml:ExtendedData', namespaces=ns)
        if ext is None:
            # Try without namespace for mixed-namespace KML
            ext = placemark.find('.//{http://www.opengis.net/kml/2.2}ExtendedData')
        if ext is None:
            return props

        # Handle <Data name="key"><value>val</value></Data>
        for data_elem in ext.findall('kml:Data', namespaces=ns):
            key = data_elem.get('name', '')
            val_elem = data_elem.find('kml:value', namespaces=ns)
            if key and val_elem is not None and val_elem.text:
                props[key] = val_elem.text

        # Handle <SchemaData><SimpleData name="key">val</SimpleData></SchemaData>
        for schema_data in ext.findall('.//kml:SchemaData', namespaces=ns):
            for simple in schema_data.findall('kml:SimpleData', namespaces=ns):
                key = simple.get('name', '')
                if key and simple.text:
                    props[key] = simple.text

        return props

    def extract_geometry(placemark):
        """Extract geometry from placemark — Point, LineString, Polygon, MultiGeometry."""
        from geojson import LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, GeometryCollection

        def parse_coords(coord_text):
            coords = []
            for c in coord_text.strip().split():
                parts = c.split(',')
                if len(parts) >= 2:
                    coords.append((float(parts[0]), float(parts[1])))
            return coords

        # Point
        point = placemark.find('.//kml:Point/kml:coordinates', namespaces=ns)
        if point is not None:
            coords = point.text.strip().split(',')
            if len(coords) >= 2:
                return Point((float(coords[0]), float(coords[1])))

        # LineString
        line = placemark.find('.//kml:LineString/kml:coordinates', namespaces=ns)
        if line is not None:
            coords = parse_coords(line.text)
            if coords:
                return LineString(coords)

        # Polygon
        poly = placemark.find('.//kml:Polygon', namespaces=ns)
        if poly is not None:
            outer = poly.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns)
            if outer is not None:
                outer_coords = parse_coords(outer.text)
                rings = [outer_coords]
                for inner in poly.findall('.//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns):
                    rings.append(parse_coords(inner.text))
                return Polygon(rings)

        return None

    def process_element(element, current_folder_path=None):
        if element.tag.endswith('Folder'):
            name_elem = element.find('./kml:name', namespaces=ns)
            folder_name = name_elem.text if name_elem is not None else "Unnamed Folder"
            if current_folder_path:
                new_folder_path = f"{current_folder_path}/{folder_name}"
            else:
                new_folder_path = folder_name
        else:
            new_folder_path = current_folder_path

        for placemark in element.findall('./kml:Placemark', namespaces=ns):
            name_elem = placemark.find('./kml:name', namespaces=ns)
            name = name_elem.text if name_elem is not None else "Unnamed Placemark"

            description_elem = placemark.find('./kml:description', namespaces=ns)
            description = description_elem.text if description_elem is not None else ""

            geometry = extract_geometry(placemark)
            if geometry is None:
                continue

            properties = {'name': name, 'description': description}
            if new_folder_path:
                properties['folder_path'] = new_folder_path

            # Merge ExtendedData attributes
            properties.update(extract_extended_data(placemark))

            feature = Feature(geometry=geometry, properties=properties)
            features.append(feature)

        for child in element:
            if child.tag.endswith('Folder') or child.tag.endswith('Document'):
                process_element(child, new_folder_path)

    process_element(root, folder_path)
    return features


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        temp_file.close()
        file.save(temp_file_path)

        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(temp_file_path)

            features = []

            if 'application/vnd.google-earth.kmz' in file_type or file.filename.endswith('.kmz'):
                kml_path = extract_kmz(temp_file_path)
                if kml_path:
                    features = parse_kml(kml_path)
                    shutil.rmtree(os.path.dirname(kml_path), ignore_errors=True)
            elif 'application/vnd.google-earth.kml+xml' in file_type or file.filename.endswith('.kml'):
                features = parse_kml(temp_file_path)
            else:
                return jsonify({'error': 'Unsupported file format. Please upload KML or KMZ files.'}), 400

            feature_collection = FeatureCollection(features)
            geojson_str = dumps(feature_collection, indent=2)
            os.remove(temp_file_path)

            return jsonify({
                'geojson': json.loads(geojson_str),
                'message': f'Successfully processed {file.filename}. Found {len(features)} features.'
            })
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/download', methods=['POST'])
def download_geojson():
    geojson_data = request.json.get('geojson')
    if not geojson_data:
        return jsonify({'error': 'No GeoJSON data provided'}), 400

    geojson_str = json.dumps(geojson_data, indent=2)
    mem_file = io.BytesIO()
    mem_file.write(geojson_str.encode('utf-8'))
    mem_file.seek(0)

    return send_file(
        mem_file,
        mimetype='application/json',
        as_attachment=True,
        download_name='converted.geojson'
    )


@app.route('/api/geoglyphs', methods=['GET'])
def get_geoglyphs():
    """Return all geoglyph points as a GeoJSON FeatureCollection."""
    if not USING_DB or not db_host:
        return jsonify({'error': 'Database not configured'}), 503

    try:
        geoglyphs = Geoglyph.query.all()
        features = []
        for g in geoglyphs:
            feature = Feature(
                id=g.id,
                geometry=Point((g.longitude, g.latitude)),
                properties={
                    'name': g.name,
                    'type': g.type,
                    'description': g.description or '',
                    'folder_path': g.folder_path or ''
                }
            )
            features.append(feature)

        collection = FeatureCollection(features)
        return jsonify(json.loads(dumps(collection)))
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/geoglyphs/<int:geoglyph_id>', methods=['GET'])
def get_geoglyph(geoglyph_id):
    """Return a single geoglyph point."""
    if not USING_DB or not db_host:
        return jsonify({'error': 'Database not configured'}), 503

    try:
        g = Geoglyph.query.get(geoglyph_id)
        if not g:
            return jsonify({'error': 'Geoglyph not found'}), 404

        feature = Feature(
            id=g.id,
            geometry=Point((g.longitude, g.latitude)),
            properties={
                'name': g.name,
                'type': g.type,
                'description': g.description or '',
                'folder_path': g.folder_path or ''
            }
        )
        return jsonify(json.loads(dumps(feature)))
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

from flask import Flask, request, jsonify, send_file
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


@app.route('/')
def index():
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
    """Parse KML file and extract placemarks with folder information."""
    with open(kml_path, 'rb') as f:
        root = parser.parse(f).getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    features = []

    def process_element(element, current_folder_path=None):
        if element.tag.endswith('Folder'):
            name_elem = element.find('.//kml:name', namespaces=ns)
            folder_name = name_elem.text if name_elem is not None else "Unnamed Folder"
            if current_folder_path:
                new_folder_path = f"{current_folder_path}/{folder_name}"
            else:
                new_folder_path = folder_name
        else:
            new_folder_path = current_folder_path

        for placemark in element.findall('.//kml:Placemark', namespaces=ns):
            name_elem = placemark.find('./kml:name', namespaces=ns)
            name = name_elem.text if name_elem is not None else "Unnamed Placemark"

            description_elem = placemark.find('./kml:description', namespaces=ns)
            description = description_elem.text if description_elem is not None else ""

            point = placemark.find('.//kml:Point/kml:coordinates', namespaces=ns)
            if point is not None:
                coords = point.text.strip().split(',')
                if len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    properties = {
                        'name': name,
                        'description': description
                    }
                    if new_folder_path:
                        properties['folder_path'] = new_folder_path

                    feature = Feature(
                        geometry=Point((lon, lat)),
                        properties=properties
                    )
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
                    os.remove(kml_path)
                    os.rmdir(os.path.dirname(kml_path))
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

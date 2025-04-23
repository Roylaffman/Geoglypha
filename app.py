from flask import Flask, request, render_template, jsonify, send_file
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

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Configure storage - either local or GCS
if USING_GCP:
    # Google Cloud Storage setup
    storage_client = storage.Client()
    bucket_name = os.environ.get('geoglypha1')
    if bucket_name:
        bucket = storage_client.bucket(bucket_name)
    else:
        print("Warning: BUCKET_NAME environment variable not set")
        USING_GCP = False

# Fall back to local storage if GCS is not configured
if not USING_GCP:
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route('/')
def index():
    return render_template('index.html')

def extract_kmz(file_path):
    """Extract KMZ file to a temporary directory and return the KML file path."""
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Find the main KML file (usually doc.kml)
    for file in os.listdir(temp_dir):
        if file.endswith('.kml'):
            return os.path.join(temp_dir, file)
    
    return None

def parse_kml(kml_path, folder_path=None):
    """Parse KML file and extract placemarks with folder information."""
    with open(kml_path, 'rb') as f:
        root = parser.parse(f).getroot()
    
    # Define KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    features = []
    
    # Process the KML document recursively
    def process_element(element, current_folder_path=None):
        # Update folder path if this is a folder
        if element.tag.endswith('Folder'):
            name_elem = element.find('.//kml:name', namespaces=ns)
            folder_name = name_elem.text if name_elem is not None else "Unnamed Folder"
            
            if current_folder_path:
                new_folder_path = f"{current_folder_path}/{folder_name}"
            else:
                new_folder_path = folder_name
        else:
            new_folder_path = current_folder_path
        
        # Process placemarks
        for placemark in element.findall('.//kml:Placemark', namespaces=ns):
            name_elem = placemark.find('./kml:name', namespaces=ns)
            name = name_elem.text if name_elem is not None else "Unnamed Placemark"
            
            description_elem = placemark.find('./kml:description', namespaces=ns)
            description = description_elem.text if description_elem is not None else ""
            
            # Extract coordinates
            point = placemark.find('.//kml:Point/kml:coordinates', namespaces=ns)
            if point is not None:
                coords = point.text.strip().split(',')
                if len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    
                    # Create GeoJSON feature
                    properties = {
                        'name': name,
                        'description': description
                    }
                    
                    # Add folder information if available
                    if new_folder_path:
                        properties['folder_path'] = new_folder_path
                    
                    feature = Feature(
                        geometry=Point((lon, lat)),
                        properties=properties
                    )
                    features.append(feature)
        
        # Process child elements recursively
        for child in element:
            if child.tag.endswith('Folder') or child.tag.endswith('Document'):
                process_element(child, new_folder_path)
    
    # Start processing from the root
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
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Save the uploaded file
        file.save(temp_file_path)
        
        try:
            # Determine file type
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(temp_file_path)
            
            features = []
            
            if 'application/vnd.google-earth.kmz' in file_type or file.filename.endswith('.kmz'):
                # Extract KMZ and get KML path
                kml_path = extract_kmz(temp_file_path)
                if kml_path:
                    features = parse_kml(kml_path)
                    # Clean up extracted files
                    os.remove(kml_path)
                    os.rmdir(os.path.dirname(kml_path))
            elif 'application/vnd.google-earth.kml+xml' in file_type or file.filename.endswith('.kml'):
                # Parse KML directly
                features = parse_kml(temp_file_path)
            else:
                return jsonify({'error': 'Unsupported file format. Please upload KML or KMZ files.'}), 400
            
            # Create GeoJSON FeatureCollection
            feature_collection = FeatureCollection(features)
            geojson_str = dumps(feature_collection, indent=2)
            
            # Clean up temporary file
            os.remove(temp_file_path)
            
            return jsonify({
                'geojson': json.loads(geojson_str),
                'message': f'Successfully processed {file.filename}. Found {len(features)} features.'
            })
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download_geojson():
    geojson_data = request.json.get('geojson')
    if not geojson_data:
        return jsonify({'error': 'No GeoJSON data provided'}), 400
    
    # Convert to string
    geojson_str = json.dumps(geojson_data, indent=2)
    
    # Create in-memory file
    mem_file = io.BytesIO()
    mem_file.write(geojson_str.encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        mimetype='application/json',
        as_attachment=True,
        download_name='converted.geojson'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

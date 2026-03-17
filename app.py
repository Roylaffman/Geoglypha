# app.py
# Ryan Lafferty
# Geoglypha Tools API — Flask backend for tools.geoglypha1.org
# Tools: KML/KMZ to GeoJSON, Vector Viewer, Raster Info, TIF to COG

from flask import Flask, request, jsonify, send_file, render_template
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

# Optional: rasterio for raster operations
try:
	import numpy as np
	import rasterio
	from rasterio.enums import Resampling
	from rasterio.shutil import copy as rio_copy
	USING_RASTERIO = True
except ImportError:
	USING_RASTERIO = False

# Optional: geopandas for vector reading
try:
	import geopandas as gpd
	import fiona
	fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
	fiona.drvsupport.supported_drivers['KML'] = 'rw'
	USING_GEOPANDAS = True
except ImportError:
	USING_GEOPANDAS = False

# Optional: Google Cloud Storage
try:
	from google.cloud import storage
	USING_GCP = True
except ImportError:
	USING_GCP = False

# Optional: database
try:
	from models import db, Geoglyph
	USING_DB = True
except ImportError:
	USING_DB = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024  # 128MB

CORS(app, origins=[
	'https://www.geoglypha1.org',
	'https://geoglypha1.org',
	'https://tools.geoglypha1.org',
	'http://localhost:5000',
	'http://127.0.0.1:5000',
	'http://localhost:8080',
	'http://127.0.0.1:8080',
])

# Database configuration
db_host = os.environ.get('DB_HOST', '')
db_name = os.environ.get('DB_NAME', 'geoglypha')
db_user = os.environ.get('DB_USER', 'geoglypha_user')
db_pass = os.environ.get('DB_PASS', '')

if db_host and USING_DB:
	if db_host.startswith('/cloudsql/'):
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

# Configure storage
if USING_GCP:
	try:
		storage_client = storage.Client()
		bucket_name = os.environ.get('BUCKET_NAME')
		if bucket_name:
			bucket = storage_client.bucket(bucket_name)
		else:
			USING_GCP = False
	except Exception as e:
		print(f"Warning: Could not initialize GCS client: {e}")
		USING_GCP = False

if not USING_GCP:
	app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()


# ─── Helper: KMZ extraction ───────────────────────────────────────────────────

def extract_kmz(file_path):
	"""Extract KMZ to temp dir, return path to the inner KML file."""
	temp_dir = tempfile.mkdtemp()
	with zipfile.ZipFile(file_path, 'r') as zf:
		zf.extractall(temp_dir)
	for f in os.listdir(temp_dir):
		if f.endswith('.kml'):
			return os.path.join(temp_dir, f)
	return None


# ─── Helper: KML parsing ──────────────────────────────────────────────────────

def parse_description_html(description):
	"""
	Extract key-value attributes from an HTML description field.
	Handles the ArcGIS KML export pattern where attributes are packed into
	a <description> as an HTML table with xmlns:fo XSL-FO namespace.
	Returns a dict of {field: value} pairs, or {} if nothing parseable.
	"""
	if not description or '<' not in description:
		return {}
	try:
		from lxml import html as lhtml
		tree = lhtml.fromstring(description)
		props = {}
		for row in tree.findall('.//tr'):
			cells = row.findall('.//td')
			if len(cells) >= 2:
				key = (cells[0].text_content() or '').strip()
				val = (cells[1].text_content() or '').strip()
				if key and val:
					props[key] = val
		return props
	except Exception:
		return {}


def parse_kml(kml_path, folder_path=None):
	"""Parse KML file and extract placemarks with folder paths and all attributes."""
	with open(kml_path, 'rb') as f:
		root = parser.parse(f).getroot()

	ns = {'kml': 'http://www.opengis.net/kml/2.2'}
	features = []

	def extract_extended_data(placemark):
		props = {}
		ext = placemark.find('.//kml:ExtendedData', namespaces=ns)
		if ext is None:
			ext = placemark.find('.//{http://www.opengis.net/kml/2.2}ExtendedData')
		if ext is None:
			return props
		for data_elem in ext.findall('kml:Data', namespaces=ns):
			key = data_elem.get('name', '')
			val_elem = data_elem.find('kml:value', namespaces=ns)
			if key and val_elem is not None and val_elem.text:
				props[key] = val_elem.text
		for schema_data in ext.findall('.//kml:SchemaData', namespaces=ns):
			for simple in schema_data.findall('kml:SimpleData', namespaces=ns):
				key = simple.get('name', '')
				if key and simple.text:
					props[key] = simple.text
		return props

	def extract_geometry(placemark):
		from geojson import LineString, Polygon

		def parse_coords(coord_text):
			coords = []
			for c in coord_text.strip().split():
				parts = c.split(',')
				if len(parts) >= 2:
					coords.append((float(parts[0]), float(parts[1])))
			return coords

		point = placemark.find('.//kml:Point/kml:coordinates', namespaces=ns)
		if point is not None:
			coords = point.text.strip().split(',')
			if len(coords) >= 2:
				return Point((float(coords[0]), float(coords[1])))

		line = placemark.find('.//kml:LineString/kml:coordinates', namespaces=ns)
		if line is not None:
			coords = parse_coords(line.text)
			if coords:
				return LineString(coords)

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
			folder_name = name_elem.text if name_elem is not None else 'Unnamed Folder'
			new_folder_path = f"{current_folder_path}/{folder_name}" if current_folder_path else folder_name
		else:
			new_folder_path = current_folder_path

		for placemark in element.findall('./kml:Placemark', namespaces=ns):
			name_elem = placemark.find('./kml:name', namespaces=ns)
			name = name_elem.text if name_elem is not None else 'Unnamed Placemark'
			desc_elem = placemark.find('./kml:description', namespaces=ns)
			description = desc_elem.text if desc_elem is not None else ''
			geometry = extract_geometry(placemark)
			if geometry is None:
				continue
			properties = {'name': name, 'description': description}
			if new_folder_path:
				properties['folder_path'] = new_folder_path
			# Pull attributes from HTML description (ArcGIS/XSL-FO export pattern)
			properties.update(parse_description_html(description))
			# ExtendedData always takes priority over description-parsed values
			properties.update(extract_extended_data(placemark))
			features.append(Feature(geometry=geometry, properties=properties))

		for child in element:
			if child.tag.endswith('Folder') or child.tag.endswith('Document'):
				process_element(child, new_folder_path)

	process_element(root, folder_path)
	return features


# ─── Helper: COG conversion ───────────────────────────────────────────────────

def convert_to_cog(input_path, output_path):
	"""Convert a GeoTIFF to Cloud Optimized GeoTIFF using rasterio."""
	temp_path = output_path + '.tmp.tif'
	try:
		with rasterio.open(input_path) as src:
			profile = src.profile.copy()
			profile.update(
				driver='GTiff',
				tiled=True,
				blockxsize=512,
				blockysize=512,
				compress='deflate',
				predictor=2,
				bigtiff='IF_SAFER',
			)
			with rasterio.open(temp_path, 'w', **profile) as dst:
				for i in range(1, src.count + 1):
					dst.write(src.read(i), i)

		with rasterio.open(temp_path, 'r+') as dst:
			overview_levels = [2, 4, 8, 16, 32]
			dst.build_overviews(overview_levels, Resampling.nearest)
			dst.update_tags(ns='rio_overview', resampling='nearest')

		rio_copy(
			temp_path, output_path,
			driver='GTiff',
			copy_src_overviews=True,
			tiled=True,
			compress='deflate',
		)
	finally:
		if os.path.exists(temp_path):
			os.remove(temp_path)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/api')
def api_info():
	return jsonify({
		'service': 'Geoglypha Tools API',
		'version': '2.0.0',
		'endpoints': {
			'POST /upload': 'KML/KMZ to GeoJSON conversion',
			'POST /download': 'Download GeoJSON as file',
			'POST /api/vector/info': 'Read vector file (KML/GeoJSON/Shapefile zip), returns GeoJSON + attributes',
			'POST /api/raster/info': 'Read GeoTIFF metadata and band statistics',
			'POST /api/convert/tif-to-cog': 'Convert GeoTIFF to Cloud Optimized GeoTIFF',
			'GET /api/geoglyphs': 'List geoglyph points as GeoJSON FeatureCollection',
			'GET /api/geoglyphs/<id>': 'Single geoglyph detail',
		},
		'capabilities': {
			'rasterio': USING_RASTERIO,
			'geopandas': USING_GEOPANDAS,
		}
	})


@app.route('/upload', methods=['POST'])
def upload_file():
	"""KML/KMZ to GeoJSON — existing endpoint preserved for backward compat."""
	if 'file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	file = request.files['file']
	if file.filename == '':
		return jsonify({'error': 'No selected file'}), 400

	temp_file = tempfile.NamedTemporaryFile(delete=False)
	temp_path = temp_file.name
	temp_file.close()
	file.save(temp_path)

	try:
		mime = magic.Magic(mime=True)
		file_type = mime.from_file(temp_path)
		features = []

		if 'application/vnd.google-earth.kmz' in file_type or file.filename.endswith('.kmz'):
			kml_path = extract_kmz(temp_path)
			if kml_path:
				features = parse_kml(kml_path)
				shutil.rmtree(os.path.dirname(kml_path), ignore_errors=True)
		elif 'application/vnd.google-earth.kml+xml' in file_type or file.filename.endswith('.kml'):
			features = parse_kml(temp_path)
		else:
			return jsonify({'error': 'Unsupported file format. Upload KML or KMZ.'}), 400

		collection = FeatureCollection(features)
		geojson_str = dumps(collection, indent=2)
		os.remove(temp_path)
		return jsonify({
			'geojson': json.loads(geojson_str),
			'message': f'Processed {file.filename}. Found {len(features)} features.',
		})
	except Exception as e:
		if os.path.exists(temp_path):
			os.remove(temp_path)
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
	return send_file(mem_file, mimetype='application/json', as_attachment=True, download_name='converted.geojson')


@app.route('/api/vector/info', methods=['POST'])
def vector_info():
	"""
	Accept KML, KMZ, GeoJSON, or zipped Shapefile.
	Return GeoJSON FeatureCollection + attribute schema + CRS + bbox.
	"""
	if not USING_GEOPANDAS:
		return jsonify({'error': 'Vector reading not available (geopandas not installed)'}), 503

	if 'file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	file = request.files['file']
	if file.filename == '':
		return jsonify({'error': 'No file selected'}), 400

	suffix = os.path.splitext(file.filename)[1].lower()
	temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
	temp_path = temp_file.name
	temp_file.close()
	file.save(temp_path)

	try:
		fname = file.filename.lower()

		if fname.endswith('.geojson') or fname.endswith('.json'):
			gdf = gpd.read_file(temp_path)

		elif fname.endswith('.kml'):
			gdf = gpd.read_file(temp_path, driver='KML')

		elif fname.endswith('.kmz'):
			kml_path = extract_kmz(temp_path)
			if not kml_path:
				return jsonify({'error': 'No KML found inside KMZ'}), 400
			try:
				gdf = gpd.read_file(kml_path, driver='KML')
			finally:
				shutil.rmtree(os.path.dirname(kml_path), ignore_errors=True)

		elif fname.endswith('.zip'):
			gdf = gpd.read_file(f'zip://{temp_path}')

		else:
			return jsonify({'error': 'Unsupported format. Upload GeoJSON, KML, KMZ, or zipped Shapefile.'}), 400

		# Reproject to WGS84 for map display
		if gdf.crs and gdf.crs.to_epsg() != 4326:
			crs_str = gdf.crs.to_string()
			gdf = gdf.to_crs(epsg=4326)
		else:
			crs_str = str(gdf.crs) if gdf.crs else 'Unknown'

		geojson_str = gdf.to_json()
		geojson_data = json.loads(geojson_str)

		# Build attribute schema (exclude geometry column)
		schema = {}
		for col in gdf.columns:
			if col == 'geometry':
				continue
			dtype = str(gdf[col].dtype)
			if 'int' in dtype:
				schema[col] = 'integer'
			elif 'float' in dtype:
				schema[col] = 'float'
			else:
				schema[col] = 'string'

		columns = [c for c in gdf.columns if c != 'geometry']
		bbox = list(gdf.total_bounds) if len(gdf) > 0 else []
		geom_types = gdf.geometry.geom_type.unique().tolist()

		return jsonify({
			'geojson': geojson_data,
			'schema': schema,
			'columns': columns,
			'crs': crs_str,
			'feature_count': len(gdf),
			'geometry_types': geom_types,
			'bbox': bbox,
			'message': f'Loaded {len(gdf)} features with {len(columns)} attribute fields.',
		})

	except Exception as e:
		return jsonify({'error': f'Error reading vector file: {str(e)}'}), 500
	finally:
		if os.path.exists(temp_path):
			os.remove(temp_path)


@app.route('/api/raster/info', methods=['POST'])
def raster_info():
	"""
	Accept GeoTIFF. Return CRS, dimensions, resolution, bounds, band stats.
	"""
	if not USING_RASTERIO:
		return jsonify({'error': 'Raster reading not available (rasterio not installed)'}), 503

	if 'file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	file = request.files['file']
	if file.filename == '':
		return jsonify({'error': 'No file selected'}), 400

	fname = file.filename.lower()
	if not (fname.endswith('.tif') or fname.endswith('.tiff') or fname.endswith('.geotiff')):
		return jsonify({'error': 'Upload a GeoTIFF file (.tif, .tiff)'}), 400

	temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tif')
	temp_path = temp_file.name
	temp_file.close()
	file.save(temp_path)

	try:
		with rasterio.open(temp_path) as src:
			crs = src.crs.to_string() if src.crs else 'Unknown'
			bounds = src.bounds
			res = src.res
			file_size_mb = round(os.path.getsize(temp_path) / (1024 * 1024), 2)
			is_cog = src.profile.get('tiled', False) and len(src.overviews(1)) > 0

			band_stats = []
			for i in range(1, src.count + 1):
				# Downsample large rasters for fast stats
				out_h = min(src.height, 512)
				out_w = min(src.width, 512)
				data = src.read(
					i,
					out_shape=(1, out_h, out_w),
					resampling=Resampling.nearest,
					masked=True,
				)
				arr = data[0]
				valid = arr.compressed() if hasattr(arr, 'compressed') else arr.flatten()
				valid = valid[np.isfinite(valid)]

				band_stats.append({
					'band': i,
					'dtype': str(src.dtypes[i - 1]),
					'nodata': src.nodata,
					'min': float(valid.min()) if len(valid) else None,
					'max': float(valid.max()) if len(valid) else None,
					'mean': float(valid.mean()) if len(valid) else None,
					'std': float(valid.std()) if len(valid) else None,
					'colorinterp': str(src.colorinterp[i - 1].name),
				})

		return jsonify({
			'driver': src.driver,
			'crs': crs,
			'width': src.width,
			'height': src.height,
			'band_count': src.count,
			'resolution': [float(res[0]), float(res[1])],
			'bounds': {
				'left': bounds.left,
				'bottom': bounds.bottom,
				'right': bounds.right,
				'top': bounds.top,
			},
			'file_size_mb': file_size_mb,
			'is_cog': is_cog,
			'compression': src.profile.get('compress', 'none'),
			'bands': band_stats,
			'message': f'Read {src.count}-band {src.width}x{src.height} raster.',
		})

	except Exception as e:
		return jsonify({'error': f'Error reading raster: {str(e)}'}), 500
	finally:
		if os.path.exists(temp_path):
			os.remove(temp_path)


@app.route('/api/convert/tif-to-cog', methods=['POST'])
def tif_to_cog():
	"""
	Accept GeoTIFF, return a Cloud Optimized GeoTIFF as a file download.
	COG = tiled layout + deflate compression + embedded overview pyramid.
	"""
	if not USING_RASTERIO:
		return jsonify({'error': 'COG conversion not available (rasterio not installed)'}), 503

	if 'file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	file = request.files['file']
	if file.filename == '':
		return jsonify({'error': 'No file selected'}), 400

	fname = file.filename.lower()
	if not (fname.endswith('.tif') or fname.endswith('.tiff')):
		return jsonify({'error': 'Upload a GeoTIFF file (.tif, .tiff)'}), 400

	temp_in = tempfile.NamedTemporaryFile(delete=False, suffix='.tif')
	temp_in_path = temp_in.name
	temp_in.close()
	file.save(temp_in_path)

	base_name = os.path.splitext(file.filename)[0]
	temp_out = tempfile.NamedTemporaryFile(delete=False, suffix='_cog.tif')
	temp_out_path = temp_out.name
	temp_out.close()

	try:
		convert_to_cog(temp_in_path, temp_out_path)
		out_size_mb = round(os.path.getsize(temp_out_path) / (1024 * 1024), 2)

		return send_file(
			temp_out_path,
			mimetype='image/tiff',
			as_attachment=True,
			download_name=f'{base_name}_cog.tif',
		)
	except Exception as e:
		return jsonify({'error': f'COG conversion failed: {str(e)}'}), 500
	finally:
		if os.path.exists(temp_in_path):
			os.remove(temp_in_path)
		# temp_out_path is sent as file — Flask streams it before cleanup


@app.route('/api/geoglyphs', methods=['GET'])
def get_geoglyphs():
	if not USING_DB or not db_host:
		return jsonify({'error': 'Database not configured'}), 503
	try:
		geoglyphs = Geoglyph.query.all()
		features = [
			Feature(
				id=g.id,
				geometry=Point((g.longitude, g.latitude)),
				properties={
					'name': g.name,
					'type': g.type,
					'description': g.description or '',
					'folder_path': g.folder_path or '',
				}
			)
			for g in geoglyphs
		]
		return jsonify(json.loads(dumps(FeatureCollection(features))))
	except Exception as e:
		return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/geoglyphs/<int:geoglyph_id>', methods=['GET'])
def get_geoglyph(geoglyph_id):
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
				'folder_path': g.folder_path or '',
			}
		)
		return jsonify(json.loads(dumps(feature)))
	except Exception as e:
		return jsonify({'error': f'Database error: {str(e)}'}), 500


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(
		host='127.0.0.1',
		port=port,
		debug=True,
		use_reloader=False,
	)

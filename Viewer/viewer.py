# viewer.py
# Ryan Lafferty
# Geoglypha Viewer — Streamlit app for interactive vector and raster exploration
# Deploys to viewer.geoglypha1.org as a Cloud Run service

import os
import zipfile
import tempfile
import shutil

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
import folium
import fiona
import rasterio
from rasterio.enums import Resampling
from streamlit_folium import st_folium

# Enable KML/KMZ drivers
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
fiona.drvsupport.supported_drivers['KML'] = 'rw'

st.set_page_config(
	page_title="Geoglypha Viewer",
	page_icon="🗺",
	layout="wide",
	initial_sidebar_state="expanded",
)

# ── Custom header HTML ────────────────────────────────────────────────────────
st.markdown("""
<div style="
	background:#3a6351;
	padding:0.9rem 1.4rem;
	margin:-1rem -1rem 1.5rem -1rem;
	border-bottom:3px solid #7c3d12;
	display:flex;
	align-items:baseline;
	gap:1rem;
">
	<a href="https://www.geoglypha1.org" style="
		font-family:'Georgia',serif;
		font-size:1.5rem;
		font-weight:700;
		color:#f2edd7;
		text-decoration:none;
	">Geoglypha</a>
	<span style="color:rgba(242,237,215,0.6);font-size:0.8rem;letter-spacing:0.08em;">
		VIEWER
	</span>
	<span style="margin-left:auto;font-size:0.78rem;color:rgba(242,237,215,0.55);">
		<a href="https://tools.geoglypha1.org" style="color:rgba(242,237,215,0.7);text-decoration:none;">
			← Tools
		</a>
	</span>
</div>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_kmz(path):
	"""Extract KMZ zip to temp dir, return path to inner KML file."""
	temp_dir = tempfile.mkdtemp()
	with zipfile.ZipFile(path, 'r') as zf:
		zf.extractall(temp_dir)
	for f in os.listdir(temp_dir):
		if f.endswith('.kml'):
			return os.path.join(temp_dir, f), temp_dir
	return None, temp_dir


def load_vector(uploaded_file):
	"""Read any supported vector file into a GeoDataFrame."""
	fname = uploaded_file.name.lower()
	suffix = os.path.splitext(fname)[1]
	tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
	tmp.write(uploaded_file.read())
	tmp.close()
	tmp_dir = None

	try:
		if fname.endswith('.geojson') or fname.endswith('.json'):
			gdf = gpd.read_file(tmp.name)
		elif fname.endswith('.kml'):
			gdf = gpd.read_file(tmp.name, driver='KML')
		elif fname.endswith('.kmz'):
			kml_path, tmp_dir = extract_kmz(tmp.name)
			if not kml_path:
				raise ValueError("No KML found inside KMZ.")
			gdf = gpd.read_file(kml_path, driver='KML')
		elif fname.endswith('.zip'):
			gdf = gpd.read_file(f'zip://{tmp.name}')
		else:
			raise ValueError(f"Unsupported format: {suffix}")

		if gdf.crs and gdf.crs.to_epsg() != 4326:
			gdf = gdf.to_crs(epsg=4326)

		return gdf
	finally:
		os.unlink(tmp.name)
		if tmp_dir:
			shutil.rmtree(tmp_dir, ignore_errors=True)


def build_vector_map(gdf, columns):
	"""Build a Folium map from a GeoDataFrame with popup and tooltip."""
	bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
	center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

	m = folium.Map(location=center, zoom_start=8, tiles=None)
	folium.TileLayer(
		tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
		attr='&copy; OpenStreetMap &copy; CARTO',
		name='CARTO Voyager',
		max_zoom=19,
	).add_to(m)

	# Pick tooltip fields (first 3 non-empty columns)
	tip_fields = [c for c in columns if c not in ('description',)][:3]
	pop_fields = columns

	folium.GeoJson(
		gdf,
		style_function=lambda _: {
			'color': '#3a6351',
			'weight': 2,
			'fillColor': '#3a6351',
			'fillOpacity': 0.25,
		},
		highlight_function=lambda _: {
			'color': '#7c3d12',
			'weight': 3,
			'fillOpacity': 0.45,
		},
		tooltip=folium.GeoJsonTooltip(
			fields=tip_fields,
			aliases=[f.replace('_', ' ').title() for f in tip_fields],
			sticky=True,
		) if tip_fields else None,
		popup=folium.GeoJsonPopup(
			fields=pop_fields,
			aliases=[f.replace('_', ' ').title() for f in pop_fields],
			max_width=360,
		) if pop_fields else None,
	).add_to(m)

	m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
	return m


def raster_preview(src, max_px=600):
	"""
	Build a matplotlib figure previewing a raster.
	Downsamples large rasters and handles single-band, RGB, and RGBA.
	"""
	scale = min(1.0, max_px / max(src.width, src.height))
	out_h = max(1, int(src.height * scale))
	out_w = max(1, int(src.width * scale))

	if src.count >= 3:
		# RGB / RGBA composite
		bands = [src.read(i, out_shape=(1, out_h, out_w), resampling=Resampling.nearest)[0]
				 for i in range(1, 4)]
		rgb = np.dstack(bands)
		# Normalize to 0-1
		lo, hi = np.percentile(rgb[rgb > 0], (2, 98)) if rgb.max() > 0 else (0, 1)
		rgb = np.clip((rgb.astype(float) - lo) / max(hi - lo, 1), 0, 1)
		fig, ax = plt.subplots(figsize=(8, 5), facecolor='#faf8f4')
		ax.imshow(rgb)
		ax.set_title("RGB Preview (bands 1-2-3)", fontfamily='serif', color='#2c1810', pad=10)
	else:
		# Single band
		data = src.read(1, out_shape=(1, out_h, out_w), resampling=Resampling.nearest,
						masked=True).squeeze()
		fig, ax = plt.subplots(figsize=(8, 5), facecolor='#faf8f4')
		im = ax.imshow(data, cmap='terrain', interpolation='nearest')
		plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
		ax.set_title("Band 1 Preview", fontfamily='serif', color='#2c1810', pad=10)

	ax.axis('off')
	fig.patch.set_facecolor('#faf8f4')
	plt.tight_layout()
	return fig


def raster_band_stats(src):
	"""Compute per-band stats using downsampled reads for speed."""
	rows = []
	for i in range(1, src.count + 1):
		data = src.read(
			i,
			out_shape=(1, min(src.height, 512), min(src.width, 512)),
			resampling=Resampling.nearest,
			masked=True,
		)
		arr = data.compressed() if hasattr(data, 'compressed') else data.flatten()
		arr = arr[np.isfinite(arr)]
		rows.append({
			'Band': i,
			'Type': str(src.dtypes[i - 1]),
			'Color Interp': src.colorinterp[i - 1].name,
			'Min': round(float(arr.min()), 4) if len(arr) else None,
			'Max': round(float(arr.max()), 4) if len(arr) else None,
			'Mean': round(float(arr.mean()), 4) if len(arr) else None,
			'Std Dev': round(float(arr.std()), 4) if len(arr) else None,
			'NoData': src.nodata,
		})
	return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
	st.markdown("### Tool")
	tool = st.radio(
		label="tool",
		options=["Vector Viewer", "Raster Inspector"],
		label_visibility="collapsed",
	)

	st.markdown("### Upload")
	if tool == "Vector Viewer":
		uploaded = st.file_uploader(
			"Vector file",
			type=["geojson", "json", "kml", "kmz", "zip"],
			label_visibility="collapsed",
			help="GeoJSON, KML, KMZ, or zipped Shapefile",
		)
	else:
		uploaded = st.file_uploader(
			"Raster file",
			type=["tif", "tiff"],
			label_visibility="collapsed",
			help="GeoTIFF (.tif / .tiff)",
		)

	st.markdown("### Links")
	st.markdown("[Geoglypha Tools](https://tools.geoglypha1.org)")
	st.markdown("[Main Site](https://www.geoglypha1.org)")


# ── Vector Viewer ─────────────────────────────────────────────────────────────

if tool == "Vector Viewer":
	if not uploaded:
		st.markdown("## Vector Viewer")
		st.info("Upload a GeoJSON, KML, KMZ, or zipped Shapefile to get started.")

		col1, col2, col3 = st.columns(3)
		col1.markdown("**Supported formats**\nGeoJSON · KML · KMZ · Shapefile (.zip)")
		col2.markdown("**Map features**\nInteractive Folium map · click popups · hover tooltips")
		col3.markdown("**Attribute table**\nSortable · filterable · full pandas DataFrame")
	else:
		with st.spinner("Reading file..."):
			try:
				gdf = load_vector(uploaded)
			except Exception as e:
				st.error(f"Could not read file: {e}")
				st.stop()

		columns = [c for c in gdf.columns if c != 'geometry']
		crs_str = str(gdf.crs) if gdf.crs else "Unknown CRS"

		# Summary row
		c1, c2, c3, c4 = st.columns(4)
		c1.metric("Features", len(gdf))
		c2.metric("Fields", len(columns))
		c3.metric("Geometry", gdf.geometry.geom_type.iloc[0] if len(gdf) else "None")
		c4.metric("CRS", crs_str.split(':')[-1] if ':' in crs_str else crs_str[:12])

		st.markdown("#### Map")
		map_obj = build_vector_map(gdf, columns)
		st_folium(map_obj, use_container_width=True, height=480, returned_objects=[])

		st.markdown("#### Attribute Table")
		attr_df = gdf[columns].copy()
		# Truncate very long strings for display
		for col in attr_df.select_dtypes(include='object').columns:
			attr_df[col] = attr_df[col].astype(str).str[:120]

		st.dataframe(
			attr_df,
			use_container_width=True,
			height=340,
		)

		col_dl, col_info = st.columns([1, 3])
		with col_dl:
			geojson_str = gdf.to_json()
			st.download_button(
				label="Download GeoJSON",
				data=geojson_str,
				file_name=uploaded.name.rsplit('.', 1)[0] + '.geojson',
				mime='application/json',
			)
		with col_info:
			st.caption(f"CRS: {crs_str} | {len(gdf)} features | {len(columns)} attribute fields")


# ── Raster Inspector ──────────────────────────────────────────────────────────

elif tool == "Raster Inspector":
	if not uploaded:
		st.markdown("## Raster Inspector")
		st.info("Upload a GeoTIFF to inspect metadata, band statistics, and a preview.")

		col1, col2, col3 = st.columns(3)
		col1.markdown("**Raster preview**\nRGB composite or single-band colormap")
		col2.markdown("**Metadata**\nCRS · dimensions · resolution · bounds · compression")
		col3.markdown("**Band statistics**\nMin · max · mean · std dev per band")
	else:
		tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tif')
		tmp.write(uploaded.read())
		tmp.close()

		try:
			with rasterio.open(tmp.name) as src:
				bounds = src.bounds
				res = src.res
				file_mb = round(os.path.getsize(tmp.name) / 1024 / 1024, 2)
				is_cog = src.profile.get('tiled', False) and len(src.overviews(1)) > 0
				compress = src.profile.get('compress', 'none')

				# Summary metrics
				c1, c2, c3, c4, c5 = st.columns(5)
				c1.metric("Width", f"{src.width:,} px")
				c2.metric("Height", f"{src.height:,} px")
				c3.metric("Bands", src.count)
				c4.metric("File Size", f"{file_mb} MB")
				c5.metric("COG", "Yes" if is_cog else "No")

				# Preview + metadata side by side
				col_map, col_meta = st.columns([3, 2])

				with col_map:
					st.markdown("#### Preview")
					with st.spinner("Rendering preview..."):
						fig = raster_preview(src)
					st.pyplot(fig, use_container_width=True)
					plt.close(fig)

				with col_meta:
					st.markdown("#### Metadata")
					meta = {
						"CRS": str(src.crs) if src.crs else "Unknown",
						"Driver": src.driver,
						"Compression": compress,
						"Resolution X": f"{res[0]:.8f}",
						"Resolution Y": f"{res[1]:.8f}",
						"West": f"{bounds.left:.6f}",
						"East": f"{bounds.right:.6f}",
						"South": f"{bounds.bottom:.6f}",
						"North": f"{bounds.top:.6f}",
						"NoData": str(src.nodata),
					}
					meta_df = pd.DataFrame(
						meta.items(), columns=["Property", "Value"]
					)
					st.dataframe(meta_df, use_container_width=True, hide_index=True, height=360)

				# Band stats table
				st.markdown("#### Band Statistics")
				with st.spinner("Computing statistics..."):
					band_df = raster_band_stats(src)
				st.dataframe(band_df, use_container_width=True, hide_index=True)

		except Exception as e:
			st.error(f"Could not read raster: {e}")
		finally:
			os.unlink(tmp.name)

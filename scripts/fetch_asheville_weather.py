"""
fetch_asheville_weather.py
Ryan Lafferty

Pulls 7 days of weather from Open-Meteo and river gauge data from USGS NWIS,
writes data/asheville_weather.json for asheville_weather_live.html.

Usage:
    python scripts/fetch_asheville_weather.py
    python scripts/fetch_asheville_weather.py --upload   # also push to GCS

After running, upload manually if needed:
    gsutil cp data/asheville_weather.json gs://www.geoglypha1.org/data/asheville_weather.json
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta


class Config:
	# Asheville, NC
	LAT = 35.5951
	LON = -82.5515
	TIMEZONE = "America/New_York"

	# USGS French Broad River at Asheville
	USGS_GAUGE = "03451500"
	USGS_DAYS = 7

	# Open-Meteo — hourly variables for 7 past days
	OPENMETEO_PAST_DAYS = 7

	OUTPUT_PATH = "data/asheville_weather.json"
	GCS_DEST = "gs://www.geoglypha1.org/data/asheville_weather.json"


def fetch_url(url):
	req = urllib.request.Request(url, headers={"User-Agent": "geoglypha-weather/1.0"})
	with urllib.request.urlopen(req, timeout=30) as resp:
		return json.loads(resp.read().decode("utf-8"))


def fetch_weather():
	"""Fetch hourly weather from Open-Meteo for the past 7 days."""
	params = urllib.parse.urlencode({
		"latitude": Config.LAT,
		"longitude": Config.LON,
		"hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m,surface_pressure",
		"temperature_unit": "celsius",
		"wind_speed_unit": "kmh",
		"precipitation_unit": "mm",
		"timezone": Config.TIMEZONE,
		"past_days": Config.OPENMETEO_PAST_DAYS,
		"forecast_days": 1,
	})
	url = f"https://api.open-meteo.com/v1/forecast?{params}"
	print(f"Fetching weather: {url[:80]}...")
	data = fetch_url(url)
	h = data["hourly"]
	return {
		"labels": h["time"],
		"temp_c": h["temperature_2m"],
		"precip_mm": h["precipitation"],
		"humidity_pct": h["relative_humidity_2m"],
		"wind_kmh": h["wind_speed_10m"],
		"pressure_hpa": h["surface_pressure"],
	}


def fetch_river():
	"""Fetch 15-min river stage + flow from USGS NWIS gauge 03451500."""
	end_dt = datetime.now(timezone.utc)
	start_dt = end_dt - timedelta(days=Config.USGS_DAYS)
	start_str = start_dt.strftime("%Y-%m-%dT%H:%M")
	end_str = end_dt.strftime("%Y-%m-%dT%H:%M")

	# Parameters: 00060 = discharge (cfs), 00065 = gage height (ft), 00010 = water temp (C)
	params = urllib.parse.urlencode({
		"format": "json",
		"sites": Config.USGS_GAUGE,
		"startDT": start_str,
		"endDT": end_str,
		"parameterCd": "00065,00060,00010",
	})
	url = f"https://waterservices.usgs.gov/nwis/iv/?{params}"
	print(f"Fetching river: {url[:80]}...")
	data = fetch_url(url)

	ts_list = data["value"]["timeSeries"]

	labels = []
	height_ft = []
	flow_cfs = []
	water_temp_c = []

	# Index each series by parameter code
	series = {}
	for ts in ts_list:
		code = ts["variable"]["variableCode"][0]["value"]
		series[code] = ts["values"][0]["value"]

	# Build aligned arrays from the stage series (00065) as the index
	if "00065" in series:
		for pt in series["00065"]:
			labels.append(pt["dateTime"])
			val = pt["value"]
			height_ft.append(float(val) if val != "-999999" else None)

	# Align flow and water temp to the same timestamps
	flow_map = {pt["dateTime"]: pt["value"] for pt in series.get("00060", [])}
	temp_map = {pt["dateTime"]: pt["value"] for pt in series.get("00010", [])}

	for lbl in labels:
		v = flow_map.get(lbl, "-999999")
		flow_cfs.append(float(v) if v != "-999999" else None)
		v = temp_map.get(lbl, "-999999")
		water_temp_c.append(float(v) if v != "-999999" else None)

	# Latest non-null values
	latest_ft = next((v for v in reversed(height_ft) if v is not None), None)
	latest_cfs = next((v for v in reversed(flow_cfs) if v is not None), None)
	latest_temp = next((v for v in reversed(water_temp_c) if v is not None), None)

	return {
		"gauge": Config.USGS_GAUGE,
		"labels": labels,
		"height_ft": height_ft,
		"flow_cfs": flow_cfs,
		"water_temp_c": water_temp_c,
		"latest_ft": latest_ft,
		"latest_cfs": latest_cfs,
		"latest_water_temp_c": latest_temp,
	}


def build_latest(weather):
	"""Pull most recent non-null hourly reading as the headline stat."""
	labels = weather["labels"]
	temp = weather["temp_c"]
	hum = weather["humidity_pct"]
	precip = weather["precip_mm"]
	wind = weather["wind_kmh"]
	pressure = weather["pressure_hpa"]

	# Work backward to find latest populated entry
	for i in range(len(labels) - 1, -1, -1):
		if temp[i] is not None:
			return {
				"time": labels[i],
				"temp_c": temp[i],
				"humidity_pct": hum[i],
				"precip_mm": precip[i] if precip[i] is not None else 0.0,
				"wind_kmh": wind[i] if wind[i] is not None else 0.0,
				"pressure_hpa": pressure[i],
			}
	return {}


def main():
	upload = "--upload" in sys.argv

	weather = fetch_weather()
	river = fetch_river()
	latest = build_latest(weather)

	now_edt = datetime.now(timezone(timedelta(hours=-4)))
	generated = now_edt.strftime("%Y-%m-%d %H:%M EDT")

	payload = {
		"generated": generated,
		"generated_unix": int(datetime.now(timezone.utc).timestamp()),
		"latest": latest,
		"weather": weather,
		"river": river,
	}

	with open(Config.OUTPUT_PATH, "w") as f:
		json.dump(payload, f, separators=(",", ":"))

	size_kb = len(json.dumps(payload)) / 1024
	print(f"Written {Config.OUTPUT_PATH} ({size_kb:.1f} KB)")
	print(f"  Weather labels: {len(weather['labels'])}")
	print(f"  River labels:   {len(river['labels'])}")
	print(f"  Latest temp:    {latest.get('temp_c')}°C")
	print(f"  Latest river:   {river['latest_ft']} ft / {river['latest_cfs']} cfs")
	print(f"  Generated:      {generated}")

	if upload:
		import subprocess
		result = subprocess.run(
			["gsutil", "cp", Config.OUTPUT_PATH, Config.GCS_DEST],
			capture_output=True, text=True
		)
		if result.returncode == 0:
			print(f"Uploaded to {Config.GCS_DEST}")
		else:
			print(f"Upload failed: {result.stderr}")


if __name__ == "__main__":
	main()

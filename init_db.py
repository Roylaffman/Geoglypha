"""
Database initialization and seed script for Geoglypha.

Usage:
    # Set environment variables first:
    export DB_HOST=localhost
    export DB_NAME=geoglypha
    export DB_USER=geoglypha_user
    export DB_PASS=your_password

    python init_db.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Geoglyph

# Seed data extracted from geoglyph_visualization.html
SEED_DATA = [
    {"name": "abuc1", "type": "circle", "latitude": -10.48284000161554, "longitude": -67.07037799917336, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abuc2", "type": "circle", "latitude": -10.28729799974037, "longitude": -67.07577000007602, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abucc", "type": "circle", "latitude": -10.46657400137342, "longitude": -67.21192700029695, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abuge", "type": "unknown", "latitude": -10.46333899988018, "longitude": -67.2094150007805, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abung", "type": "unknown", "latitude": -10.41260199819366, "longitude": -67.29513700037768, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abucq", "type": "unknown", "latitude": -10.4284909998873, "longitude": -67.1137099972466, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abunc", "type": "circle", "latitude": -10.306942, "longitude": -67.220174, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abunq", "type": "circle", "latitude": -10.30685900077723, "longitude": -67.21787199995943, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abuno", "type": "unknown", "latitude": -9.979387000098159, "longitude": -66.73494599878383, "folder_path": "Amazonian Geoglyphs"},
    {"name": "abuov", "type": "unknown", "latitude": -10.07957900087295, "longitude": -66.86946699952472, "folder_path": "Amazonian Geoglyphs"},
    {"name": "acdc3", "type": "circle", "latitude": -10.12735399971775, "longitude": -67.03417500004319, "folder_path": "Amazonian Geoglyphs"},
    {"name": "acdc4", "type": "circle", "latitude": -10.075528, "longitude": -67.553878, "folder_path": "Amazonian Geoglyphs"},
]


def create_app():
    app = Flask(__name__)

    db_host = os.environ.get('DB_HOST', 'localhost')
    db_name = os.environ.get('DB_NAME', 'geoglypha')
    db_user = os.environ.get('DB_USER', 'geoglypha_user')
    db_pass = os.environ.get('DB_PASS', '')

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
    return app


def init_database():
    app = create_app()

    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created.")

        existing = Geoglyph.query.count()
        if existing > 0:
            print(f"Database already has {existing} records. Skipping seed.")
            return

        print(f"Seeding {len(SEED_DATA)} geoglyph records...")
        for data in SEED_DATA:
            geoglyph = Geoglyph(
                name=data['name'],
                type=data.get('type'),
                latitude=data['latitude'],
                longitude=data['longitude'],
                description=data.get('description', ''),
                folder_path=data.get('folder_path', '')
            )
            db.session.add(geoglyph)

        db.session.commit()
        print(f"Seeded {len(SEED_DATA)} records successfully.")


if __name__ == '__main__':
    init_database()

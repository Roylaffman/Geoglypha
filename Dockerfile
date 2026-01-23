FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for python-magic and psycopg2
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY models.py .
COPY init_db.py .

# Default port for Cloud Run
ENV PORT=8080

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 app:app

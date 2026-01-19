#!/bin/sh

set -e

echo "Waiting for database..."
# This waits until the postgres host is reachable on port 5432
python << END
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.environ.get('DATABASE_URL')
url = urlparse(db_url)
host = url.hostname
port = url.port or 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except socket.error:
        print("Postgres unavailable, waiting...")
        time.sleep(1)
END

# Define settings module
export DJANGO_SETTINGS_MODULE=shop_ai.settings.production

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn shop_ai.wsgi:application --bind 0.0.0.0:8000
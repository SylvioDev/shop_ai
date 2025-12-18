#!/bin/sh

set -e

echo "Waiting for database..."
python manage.py check --database default

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn shop_ai.wsgi:application --bind 0.0.0.0:8000

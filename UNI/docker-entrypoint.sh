#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for database to be ready..."
python -c "
import sys
import time
import psycopg2
import os

host = os.environ.get('DBHOST')
port = os.environ.get('PORT')
dbname = os.environ.get('DATABASE')
user = os.environ.get('DBUSER')
password = os.environ.get('DBPASSWORD')

for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
        print('Database is ready!')
        sys.exit(0)
    except psycopg2.OperationalError:
        print('Database not ready yet. Waiting...')
        time.sleep(2)

print('Could not connect to database after 30 attempts. Exiting.')
sys.exit(1)
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn KALAKSHETRA.wsgi:application --bind 0.0.0.0:8000 --timeout 120
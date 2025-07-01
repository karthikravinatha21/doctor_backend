#!/bin/bash
cd /home/ec2-user/app

source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

python manage.py collectstatic --noinput

python manage.py migrate

# Kill any existing gunicorn processes
pkill gunicorn || true

# Start Gunicorn in the background with PID file
gunicorn KALAKSHETRA.wsgi:application \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --daemon \
    --pid /home/ec2-user/app/gunicorn.pid \
    --log-file /home/ec2-user/app/logs/gunicorn.log \
    --access-logfile /home/ec2-user/app/logs/access.log \
    --error-logfile /home/ec2-user/app/logs/error.log \
    --capture-output

# Wait for Gunicorn to start
sleep 5

# Check if Gunicorn is running
if [ -f /home/ec2-user/app/gunicorn.pid ] && ps -p $(cat /home/ec2-user/app/gunicorn.pid) > /dev/null; then
    echo "Gunicorn started successfully"
    exit 0
else
    echo "Failed to start Gunicorn"
    exit 1
fi
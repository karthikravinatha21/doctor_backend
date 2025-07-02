#!/bin/bash
# Verify that the application is ready to receive traffic
cd /home/ec2-user/app

# Check if Gunicorn is running using PID file
if [ -f /home/ec2-user/app/gunicorn.pid ]; then
    pid=$(cat /home/ec2-user/app/gunicorn.pid)
    if ps -p $pid > /dev/null; then
        echo "Gunicorn process is running with PID: $pid"
    else
        echo "Gunicorn process not found"
        exit 1
    fi
else
    echo "Gunicorn PID file not found"
    exit 1
fi

# Check if the application is responding
if ! curl -s http://localhost:8000/health/ | grep -q "ok"; then
    echo "Application health check failed"
    exit 1
fi

echo "Application is healthy and ready to receive traffic"
exit 0
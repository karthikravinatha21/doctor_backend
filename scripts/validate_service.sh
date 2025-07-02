#!/bin/bash
# Wait for the application to be ready
sleep 10

# Check if the container is running
# if ! docker ps | grep -q "app-web"; then
#     echo "Container is not running"
#     exit 1
# fi

# Check if the application is responding
if ! curl -f http://localhost:8000/health/; then
    echo "Application is not responding"
    exit 1
fi

echo "Application is running and responding"
exit 0
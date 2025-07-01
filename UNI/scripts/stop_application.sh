#!/bin/bash
cd /home/ec2-user/app

# Check if PID file exists
if [ -f /home/ec2-user/app/gunicorn.pid ]; then
    pid=$(cat /home/ec2-user/app/gunicorn.pid)
    
    # Check if process is running
    if ps -p $pid > /dev/null; then
        echo "Stopping Gunicorn process with PID: $pid"
        kill $pid
        
        # Wait for process to stop
        for i in {1..30}; do
            if ! ps -p $pid > /dev/null; then
                echo "Gunicorn process stopped successfully"
                rm -f /home/ec2-user/app/gunicorn.pid
                exit 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        echo "Force killing Gunicorn process"
        kill -9 $pid || true
        rm -f /home/ec2-user/app/gunicorn.pid
    else
        echo "No running Gunicorn process found with PID: $pid"
        rm -f /home/ec2-user/app/gunicorn.pid
    fi
else
    echo "No PID file found"
fi

# Kill any remaining gunicorn processes
pkill gunicorn || true

exit 0
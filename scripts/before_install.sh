#!/bin/bash

# Stop the application if it's running
if [ -f /home/ec2-user/app/scripts/stop_application.sh ]; then
    echo "Stopping existing application..."
    bash /home/ec2-user/app/scripts/stop_application.sh
fi

# Clean up old files
rm -rf /home/ec2-user/app/*

# Install or update required packages
yum update -y
# yum install -y python3.10 python3.10-devel python3.10-pip
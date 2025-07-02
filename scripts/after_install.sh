#!/bin/bash

cd /home/ec2-user/app

python -m venv venv
export PATH="venv/bin:$PATH"

source venv/bin/activate

pip3.10 install -r requirement.txt
pip3.10 install gunicorn

# Make scripts executable
chmod +x scripts/*.sh

# Create necessary directories
mkdir -p logs
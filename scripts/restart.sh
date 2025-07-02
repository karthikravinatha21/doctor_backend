#!/bin/bash
cp /home/ubuntu/cicd/.env /home/ubuntu/Mojo/Mojo-Backend/Mojo-Backend
cp -r /home/ubuntu/cicd/logs /home/ubuntu/Mojo/Mojo-Backend/Mojo-Backend
cd /home/ubuntu/Mojo/Mojo-Backend/Mojo-Backend/
chmod 777 -R .
source ../mojoenv/bin/activate
python3 manage.py collectstatic
python3 manage.py makemigrations 
python3 manage.py migrate 
service mojo_gunicorn restart


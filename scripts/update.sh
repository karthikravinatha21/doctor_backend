#!/bin/bash
sudo cp /home/ubuntu/Mojo/Mojo-Backend/Mojo-Backend/.env /home/ubuntu/cicd/
sudo cp -r /home/ubuntu/Mojo/Mojo-Backend/Mojo-Backend/logs /home/ubuntu/cicd/
cd /home/ubuntu/Mojo/Mojo-Backend/
sudo rm -rf Mojo-Backend
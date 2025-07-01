#!/bin/bash
# Perform post-traffic routing tasks
cd /home/ec2-user/app

# Log successful deployment
echo "$(date): Deployment completed successfully - Traffic now being served by this instance" >> /var/log/deployment.log

exit 0
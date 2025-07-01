#!/bin/bash
# Install required packages
yum update -y
# yum install -y docker
yum install -y python3 python3-pip git ruby wget
dnf groupinstall "Development Tools" -y
dnf install gcc openssl-devel libffi-devel bzip2-devel zlib-devel wget make tar -y

cd /usr/src
wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz
tar xvf Python-3.10.14.tgz
cd Python-3.10.14
./configure --enable-optimizations --with-ensurepip=install
make -j$(nproc)
make altinstall
alternatives --install /usr/bin/python python /usr/local/bin/python3.10 1

# Install CodeDeploy agent
cd /home/ec2-user
wget https://aws-codedeploy-${aws_region}.s3.amazonaws.com/latest/install
chmod +x ./install
./install auto
systemctl start codedeploy-agent
systemctl enable codedeploy-agent

# Install and configure Docker
# systemctl start docker
# systemctl enable docker
# usermod -aG docker ec2-user

%{for key, value in environment_variables ~}
echo "export ${key}=${value}" >> /etc/environment
%{endfor ~}

source /etc/environment
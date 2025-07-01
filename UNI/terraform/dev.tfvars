# Project configuration
project_name = "kalakshetra"
environment  = "dev"
aws_region   = "ap-south-1"

# VPC configuration
vpc_cidr = "10.0.0.0/16"

# Database configuration
db_name           = "kaladb"
db_username       = "dbadmin"
db_instance_class = "db.t3.small"

# Container configuration
container_port = 8000

# CodePipeline configuration
repository_id         = "kalavaibhava/django"
branch_name          = "development"

# Route53 configuration
domain_name          = "api.dev.cineartery.com"
allowed_hosts        = "api.dev.cineartery.com,cineartery.com,www.cineartery.com"
hosted_zone_id       = "Z08392762B1G86G1PAFXF"
create_www_subdomain = false
record_ttl           = 300

# Tags
tags = {
  Project     = "kalakshetra"
  Environment = "dev"
  ManagedBy   = "terraform"
}

# EC2 Config
key_name = "base-key-pair"
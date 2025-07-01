variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "kalakshetra"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "kaladb"
}

variable "db_username" {
  description = "The username for the database"
  type        = string
  default     = "dbadmin"
}

variable "db_instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
  default     = "db.t3.small"
}

variable "container_port" {
  description = "The port the container exposes"
  type        = number
  default     = 8000
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {
    Project     = "kalakshetra"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

# EC2 variables
variable "key_name" {
  description = "The name of the SSH key pair to use for EC2 instances"
  type        = string
}

variable "git_repository_url" {
  description = "The URL of the Git repository to clone"
  type        = string
  default     = "https://github.com/kalavaibhava/django.git"
}

# Route53 variables
variable "domain_name" {
  description = "The domain name to map to the ALB"
  type        = string
}

variable "allowed_hosts" {
  description = "Domains for the Django app to load"
  type        = string
}

variable "hosted_zone_id" {
  description = "The ID of the Route53 hosted zone"
  type        = string
  default     = ""  # This should be provided by the user
}

variable "create_www_subdomain" {
  description = "Whether to create a www subdomain CNAME record"
  type        = bool
  default     = true
}

variable "record_ttl" {
  description = "The TTL for the CNAME record"
  type        = number
  default     = 300
}

# CodePipeline variables
variable "repository_id" {
  description = "The full GitHub repository ID (e.g., 'owner/repo')"
  type        = string
}

variable "branch_name" {
  description = "The branch name to use for deployments"
  type        = string
  default     = "main"
}

# Auto Scaling Group variables
variable "asg_desired_capacity" {
  description = "The desired number of instances in the Auto Scaling Group"
  type        = number
  default     = 1
}

variable "asg_min_size" {
  description = "The minimum number of instances in the Auto Scaling Group"
  type        = number
  default     = 1
}

variable "asg_max_size" {
  description = "The maximum number of instances in the Auto Scaling Group"
  type        = number
  default     = 2
}

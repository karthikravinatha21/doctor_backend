variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs where EC2 instances will be launched"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "ID of the ALB security group"
  type        = string
}

variable "alb_target_group_arn" {
  description = "ARN of the ALB target group"
  type        = string
}

variable "container_port" {
  description = "Port on which the application container listens"
  type        = number
  default     = 8000
}

variable "ami_id" {
  description = "ID of the AMI to use for EC2 instance"
  type        = string
  default     = "ami-0f535a71b34f2d44a"  # Amazon Linux 2 AMI in ap-south-1 # Ubuntu ami-0e35ddab05955cf57
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3a.medium"
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 30
}

variable "ssh_allowed_cidr_blocks" {
  description = "CIDR blocks allowed to SSH into the instance"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "git_repository_url" {
  description = "URL of the Git repository"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "allowed_hosts" {
  description = "List of allowed hosts for Django"
  type        = list(string)
}

variable "db_name" {
  description = "Name of the database"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_host" {
  description = "Database host"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for static files"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "db_access_sg_id" {
  description = "ID of the database access security group"
  type        = string
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in the Auto Scaling Group"
  type        = number
}

variable "asg_min_size" {
  description = "Minimum number of instances in the Auto Scaling Group"
  type        = number
}

variable "asg_max_size" {
  description = "Maximum number of instances in the Auto Scaling Group"
  type        = number
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "lt_env_variables" {
  type = object({})
}

variable "user_data" {
  type = string
}
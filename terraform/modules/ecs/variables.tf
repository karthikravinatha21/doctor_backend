variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "The IDs of the subnets to deploy the ECS tasks in"
  type        = list(string)
}

variable "alb_target_group_arn" {
  description = "The ARN of the ALB target group"
  type        = string
}

variable "alb_security_group_id" {
  description = "The ID of the ALB security group"
  type        = string
}

variable "ecr_repository_url" {
  description = "The URL of the ECR repository"
  type        = string
}

variable "container_port" {
  description = "The port the container exposes"
  type        = number
  default     = 8000
}

variable "task_cpu" {
  description = "The CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "The memory for the ECS task in MiB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "The desired number of tasks to run"
  type        = number
  default     = 1
}

variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "container_environment" {
  description = "Environment variables for the container"
  type        = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "container_secrets" {
  description = "Secrets for the container from SSM Parameter Store"
  type        = list(object({
    name      = string
    valueFrom = string
  }))
  default = []
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

variable "existing_security_group_id" {
  description = "ID of an existing security group to use for ECS tasks"
  type        = string
  default     = ""
}


variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (e.g., dev, staging, prod)"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}

variable "asg_name" {
  description = "Name of the Auto Scaling Group"
  type        = string
}

variable "target_group_arn" {
  description = "ARN of the ALB target group for traffic control"
  type        = string
}
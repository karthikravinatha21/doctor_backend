variable "domain_name" {
  description = "The domain name for the certificate"
  type        = string
}

variable "hosted_zone_id" {
  description = "The ID of the Route53 hosted zone"
  type        = string
}

variable "create_www_subdomain" {
  description = "Whether to include www subdomain in the certificate"
  type        = bool
  default     = true
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
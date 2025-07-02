variable "domain_name" {
  description = "The domain name to map to the ALB"
  type        = string
}

variable "hosted_zone_id" {
  description = "The ID of the Route53 hosted zone"
  type        = string
}

variable "alb_dns_name" {
  description = "The DNS name of the ALB"
  type        = string
}

variable "alb_zone_id" {
  description = "The canonical hosted zone ID of the ALB"
  type        = string
}

variable "record_ttl" {
  description = "The TTL for the CNAME record"
  type        = number
  default     = 300
}

variable "create_www_subdomain" {
  description = "Whether to create a www subdomain CNAME record"
  type        = bool
  default     = true
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
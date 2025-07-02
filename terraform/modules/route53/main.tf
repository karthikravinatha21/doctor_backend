# Route53 module for mapping ALB to a hosted zone

# Create an A record that points to the ALB
resource "aws_route53_record" "alb" {
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "A"
  
  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# Create a CNAME record for www subdomain (optional)
resource "aws_route53_record" "www" {
  count   = var.create_www_subdomain ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = "www.${var.domain_name}"
  type    = "CNAME"
  ttl     = var.record_ttl
  records = [var.domain_name]
}
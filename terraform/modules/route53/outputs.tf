output "domain_record_name" {
  description = "The domain name of the record"
  value       = aws_route53_record.alb.name
}

output "domain_record_fqdn" {
  description = "The FQDN of the record"
  value       = aws_route53_record.alb.fqdn
}

output "www_record_name" {
  description = "The www subdomain name of the record"
  value       = var.create_www_subdomain ? aws_route53_record.www[0].name : null
}

output "www_record_fqdn" {
  description = "The FQDN of the www record"
  value       = var.create_www_subdomain ? aws_route53_record.www[0].fqdn : null
}
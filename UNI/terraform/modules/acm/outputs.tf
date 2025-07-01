output "certificate_arn" {
  description = "The ARN of the certificate"
  value       = aws_acm_certificate.main.arn
}

output "certificate_domain_name" {
  description = "The domain name of the certificate"
  value       = aws_acm_certificate.main.domain_name
}
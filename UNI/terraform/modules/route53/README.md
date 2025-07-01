# Route53 Module

This module creates Route53 DNS records to map an Application Load Balancer (ALB) to a domain name.

## Features

- Creates an A record that points to the ALB using an alias record
- Optionally creates a CNAME record for the www subdomain
- Configurable TTL for CNAME records

## Usage

```hcl
module "route53" {
  source = "./modules/route53"

  domain_name         = "example.com"
  hosted_zone_id      = "Z1234567890ABC"
  alb_dns_name        = module.alb.alb_dns_name
  alb_zone_id         = module.alb.alb_zone_id
  create_www_subdomain = true
  record_ttl          = 300
  tags                = var.tags
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.13.0 |
| aws | >= 3.0.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| domain_name | The domain name to map to the ALB | `string` | n/a | yes |
| hosted_zone_id | The ID of the Route53 hosted zone | `string` | n/a | yes |
| alb_dns_name | The DNS name of the ALB | `string` | n/a | yes |
| alb_zone_id | The canonical hosted zone ID of the ALB | `string` | n/a | yes |
| create_www_subdomain | Whether to create a www subdomain CNAME record | `bool` | `true` | no |
| record_ttl | The TTL for the CNAME record | `number` | `300` | no |
| tags | A map of tags to add to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| domain_record_name | The domain name of the record |
| domain_record_fqdn | The FQDN of the record |
| www_record_name | The www subdomain name of the record |
| www_record_fqdn | The FQDN of the www record |

## Notes

- The hosted zone must already exist in Route53
- The domain name must be registered and managed by Route53 or delegated to Route53
- The ALB must be properly configured and accessible
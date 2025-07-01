# Domain Setup for KALAKSHETRA Application

This guide explains how to set up a custom domain for the KALAKSHETRA application deployed in AWS ECS.

## Prerequisites

1. A registered domain name
2. A Route53 hosted zone for your domain
3. AWS CLI configured with appropriate permissions

## Configuration Steps

### 1. Update Terraform Variables

Create a `terraform.tfvars` file in the terraform directory with the following domain-related variables:

```hcl
# Route53 configuration
domain_name         = "yourdomain.com"  # Replace with your actual domain name
hosted_zone_id      = "Z1234567890ABC"  # Replace with your actual hosted zone ID
create_www_subdomain = true  # Set to false if you don't want a www subdomain
```

### 2. Apply Terraform Configuration

```bash
cd terraform
terraform init
terraform apply
```

This will:
- Create an SSL/TLS certificate for your domain
- Configure the Application Load Balancer with HTTPS support
- Set up Route53 records to point your domain to the application
- Configure the ECS service with the domain information

### 3. Verify Certificate Validation

The ACM certificate validation happens automatically through DNS validation. You can check the status in the AWS Console under Certificate Manager.

### 4. Access Your Application

Once the deployment is complete and the certificate is validated, you can access your application at:

```
https://yourdomain.com
```

And if you enabled the www subdomain:

```
https://www.yourdomain.com
```

## Troubleshooting

### Certificate Validation Issues

If the certificate validation is taking too long:
1. Check that your Route53 hosted zone is correctly set up
2. Verify that the DNS validation records were created properly
3. You can manually check DNS propagation using tools like `dig` or online DNS lookup services

### HTTPS Not Working

If HTTPS is not working:
1. Ensure the certificate is fully validated
2. Check that the ALB security group allows traffic on port 443
3. Verify that the ALB listener for HTTPS is correctly configured

### Domain Not Resolving

If your domain is not resolving to the application:
1. Check the Route53 records in the AWS Console
2. Verify that your domain's name servers are correctly set to use Route53
3. DNS changes can take time to propagate (up to 48 hours in some cases)

## Additional Configuration

### Custom Domain in Django Settings

The application is configured to use the custom domain in Django settings. The following environment variables are set:

- `DOMAIN_NAME`: Your custom domain name
- `SITE_URL`: The full URL with protocol (https://yourdomain.com)
- `ALLOWED_HOSTS`: Includes your domain and www subdomain

### CSRF Protection

For security, CSRF protection is configured to work with your custom domain. The following settings are applied:

- `CSRF_COOKIE_DOMAIN`: Set to your domain name
- `CSRF_TRUSTED_ORIGINS`: Includes both https://yourdomain.com and https://www.yourdomain.com
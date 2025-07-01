# Kalakshetra Infrastructure

This directory contains the Terraform configuration for deploying the Kalakshetra application infrastructure on AWS.

## Architecture

The infrastructure consists of the following components:

- VPC with public and private subnets
- Application Load Balancer (ALB)
- ECS Cluster and Service
- RDS PostgreSQL database
- S3 bucket for static files
- ECR repository for Docker images
- CodePipeline for CI/CD
- Route53 DNS records for custom domain

## Modules

The infrastructure is organized into the following modules:

- `alb`: Application Load Balancer configuration
- `ecs`: ECS cluster, service, and task definition
- `rds`: RDS PostgreSQL database
- `s3`: S3 bucket for static files
- `vpc`: VPC and networking resources
- `codepipeline`: CI/CD pipeline for building and deploying the application
- `route53`: DNS records for mapping the ALB to a domain name

## Usage

1. Initialize Terraform:

```bash
terraform init
```

2. Review the execution plan:

```bash
terraform plan
```

3. Apply the configuration:

```bash
terraform apply
```

4. After deployment, you need to manually activate the CodeStar connection in the AWS Console:
   - Go to Developer Tools > Settings > Connections
   - Find the connection created by this module
   - Click "Update pending connection" and follow the instructions

## Variables

The main variables are defined in `variables.tf`. You can override them by creating a `terraform.tfvars` file or by passing them on the command line.

Key variables include:

- `project_name`: The name of the project (default: "kalakshetra")
- `environment`: The environment (dev, staging, prod) (default: "dev")
- `aws_region`: The AWS region to deploy resources (default: "ap-south-1")
- `repository_id`: The ID of the GitHub repository (e.g., "username/kalakshetra")
- `branch_name`: The branch name to use for the source code (default: "main")
- `domain_name`: The domain name to map to the ALB (default: "example.com")
- `hosted_zone_id`: The ID of the Route53 hosted zone

## Outputs

After deployment, Terraform will output various resource identifiers, including:

- VPC ID
- Subnet IDs
- RDS endpoint
- S3 bucket name
- ECR repository URL
- ALB DNS name
- ECS cluster and service names
- CodePipeline name and artifacts bucket
- CodeBuild project name
- CodeStar connection ARN
- Domain record name and FQDN

## Notes

- The database password and Django secret key are generated randomly and stored in AWS SSM Parameter Store.
- The CodeStar connection requires manual activation in the AWS Console after deployment.
- The buildspec.yml file must be present in the root of your repository for CodeBuild to work properly.
- The Route53 hosted zone must already exist in your AWS account before deploying this infrastructure.
- You must provide a valid `hosted_zone_id` for the Route53 module to work properly.
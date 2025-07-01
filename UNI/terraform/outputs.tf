output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "The IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "The IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "db_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = module.rds.db_endpoint
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket for static files"
  value       = module.s3.bucket_name
}

output "s3_bucket_domain_name" {
  description = "The domain name of the S3 bucket"
  value       = module.s3.bucket_domain_name
}

# output "ecr_repository_url" {
#   description = "The URL of the ECR repository"
#   value       = aws_ecr_repository.app.repository_url
# }

output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = module.alb.alb_dns_name
}

# output "ecs_cluster_name" {
#   description = "The name of the ECS cluster"
#   value       = module.ecs.cluster_name
# }

# output "ecs_service_name" {
#   description = "The name of the ECS service"
#   value       = module.ecs.service_name
# }

# CodePipeline outputs
# output "codepipeline_name" {
#   description = "The name of the CodePipeline"
#   value       = module.codepipeline.codepipeline_name
# }

# output "codepipeline_artifacts_bucket" {
#   description = "The name of the S3 bucket used to store pipeline artifacts"
#   value       = module.codepipeline.artifacts_bucket_name
# }

# output "codebuild_project_name" {
#   description = "The name of the CodeBuild project"
#   value       = module.codepipeline.codebuild_project_name
# }

# output "codestar_connection_arn" {
#   description = "The ARN of the CodeStar connection"
#   value       = aws_codestarconnections_connection.github.arn
# }

output "codestar_connection_status" {
  description = "The status of the CodeStar connection"
  value       = "The connection needs to be manually activated in the AWS Console after deployment"
}

# ACM certificate outputs
output "certificate_arn" {
  description = "The ARN of the SSL certificate"
  value       = module.acm.certificate_arn
}

output "certificate_domain_name" {
  description = "The domain name of the certificate"
  value       = module.acm.certificate_domain_name
}

# Route53 outputs
output "domain_record_name" {
  description = "The domain name of the record"
  value       = module.route53.domain_record_name
}

output "domain_record_fqdn" {
  description = "The FQDN of the record"
  value       = module.route53.domain_record_fqdn
}

output "www_record_name" {
  description = "The www subdomain name of the record"
  value       = module.route53.www_record_name
}

output "www_record_fqdn" {
  description = "The FQDN of the www record"
  value       = module.route53.www_record_fqdn
}

output "application_url" {
  description = "The URL to access the application"
  value       = "https://${var.domain_name}"
}

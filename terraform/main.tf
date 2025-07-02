terraform {
  backend "s3" {
    bucket       = "terraform-states-cineartery"
    key          = "terraform.tfstate"
    region       = "ap-south-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  allowed_hosts = [
    "*.amazonaws.com",
    "localhost",
    "127.0.0.1",
    var.domain_name,
    "www.${var.domain_name}",
    var.allowed_hosts
  ]
}

# Create a random string for the RDS password
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Create a random string for Django secret key
resource "random_string" "django_secret_key" {
  length  = 50
  special = true
}

# Store sensitive values in SSM Parameter Store
resource "aws_ssm_parameter" "db_password" {
  name        = "/${var.project_name}/${var.environment}/db_password"
  description = "Database password for ${var.project_name}"
  type        = "SecureString"
  value       = random_password.db_password.result
  tags        = var.tags
}

resource "aws_ssm_parameter" "django_secret_key" {
  name        = "/${var.project_name}/${var.environment}/django_secret_key"
  description = "Django secret key for ${var.project_name}"
  type        = "SecureString"
  value       = random_string.django_secret_key.result
  tags        = var.tags
}

# Create VPC and networking resources
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  cidr_block   = var.vpc_cidr
  tags         = var.tags
}

# Create S3 bucket for static files
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
  tags         = var.tags
}

# Create ACM certificate for the domain
module "acm" {
  source = "./modules/acm"

  project_name         = var.project_name
  environment          = var.environment
  domain_name          = var.domain_name
  hosted_zone_id       = var.hosted_zone_id
  create_www_subdomain = var.create_www_subdomain
  tags                 = var.tags
}

# Create Application Load Balancer
module "alb" {
  source = "./modules/alb"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.public_subnet_ids
  certificate_arn = module.acm.certificate_arn
  tags            = var.tags
}

# Create security groups
module "security_groups" {
  source = "./modules/security_groups"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  tags         = var.tags
}

# Create RDS PostgreSQL instance
module "rds" {
  source = "./modules/rds"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = var.environment == "prod" ? module.vpc.private_subnet_ids : module.vpc.public_subnet_ids
  db_access_sg_id   = module.security_groups.db_access_sg_id
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = random_password.db_password.result
  db_instance_class = var.db_instance_class
  tags              = var.tags
}

# Store RDS endpoint in SSM Parameter Store
resource "aws_ssm_parameter" "db_endpoint" {
  name        = "/${var.project_name}/${var.environment}/db_endpoint"
  description = "RDS endpoint for ${var.project_name}"
  type        = "String"
  value       = module.rds.db_endpoint
  tags        = var.tags
  depends_on  = [module.rds]
}

# Create EC2 instances with Auto Scaling Group
module "ec2" {
  source = "./modules/ec2"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.public_subnet_ids
  alb_security_group_id = module.alb.alb_security_group_id
  alb_target_group_arn  = module.alb.target_group_arn
  container_port        = var.container_port
  key_name              = var.key_name
  git_repository_url    = var.git_repository_url
  ecr_repository_url    = module.ecr.repository_url
  db_access_sg_id       = module.security_groups.db_access_sg_id

  allowed_hosts = local.allowed_hosts

  db_name           = var.db_name
  db_username       = var.db_username
  db_host           = module.rds.db_endpoint
  db_password       = random_password.db_password.result
  django_secret_key = random_string.django_secret_key.result
  s3_bucket_name    = module.s3.bucket_name
  aws_region        = var.aws_region
  domain_name       = var.domain_name

  asg_desired_capacity = var.asg_desired_capacity
  asg_min_size         = var.asg_min_size
  asg_max_size         = var.asg_max_size

  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    environment_variables = {
      "DEBUG"                   = "False"
      "ALLOWED_HOSTS"           = join(",", local.allowed_hosts)
      "DBENGINE"                = "django.db.backends.postgresql_psycopg2"
      "DATABASE"                = var.db_name
      "DBUSER"                  = var.db_username
      "DBHOST"                  = module.rds.db_endpoint
      "PORT"                    = 5432
      "DBPASSWORD"              = "${random_password.db_password.result}"
      "SECRET_KEY"              = "${random_string.django_secret_key.result}"
      "USE_S3"                  = "True"
      "AWS_STORAGE_BUCKET_NAME" = module.s3.bucket_name
      "AWS_S3_REGION_NAME"      = var.aws_region
      "DOMAIN_NAME"             = var.domain_name
      "SITE_URL"                = "https://${var.domain_name}"
    }
    aws_region = var.aws_region
  }))
  lt_env_variables = {}

  tags = var.tags

  depends_on = [module.rds, module.alb]
}

# Create Route53 records for the ALB
module "route53" {
  source = "./modules/route53"

  domain_name          = var.domain_name
  hosted_zone_id       = var.hosted_zone_id
  alb_dns_name         = module.alb.alb_dns_name
  alb_zone_id          = module.alb.alb_zone_id
  create_www_subdomain = var.create_www_subdomain
  record_ttl           = var.record_ttl
  tags                 = var.tags

  depends_on = [module.alb]
}

# Create CodeDeploy resources
module "codedeploy" {
  source = "./modules/codedeploy"

  project_name     = var.project_name
  environment      = var.environment
  asg_name         = module.ec2.asg_name
  target_group_arn = module.alb.target_group_arn
  tags             = var.tags

  depends_on = [module.ec2]
}

locals {

}

# Create CodeBuild resources
module "codebuild" {
  source = "./modules/codebuild"

  project_name       = "${var.project_name}-${var.environment}-build"
  environment        = var.environment
  ecr_repository_url = module.ecr.repository_url
  tags               = var.tags
}

# Create ECR repository
module "ecr" {
  source = "./modules/ecr"

  repository_name      = "${var.project_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"
  scan_on_push         = false
  tags                 = var.tags
}

# Create CodePipeline resources
module "codepipeline" {
  source = "./modules/codepipeline"

  project_name           = var.project_name
  environment            = var.environment
  repository_name        = var.repository_id
  branch_name            = var.branch_name
  codebuild_project_name = module.codebuild.project_name
  codebuild_project_arn  = module.codebuild.project_arn
  codedeploy_app_name    = module.codedeploy.app_name
  codedeploy_group_name  = module.codedeploy.deployment_group_name
  tags                   = var.tags

  depends_on = [module.codedeploy, module.codebuild]
}

output "name" {
  value = module.ecr.repository_url
}

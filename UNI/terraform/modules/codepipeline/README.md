# AWS CodePipeline Terraform Module

This module creates an AWS CodePipeline for continuous integration and deployment of the Kalakshetra application.

## Features

- Creates an S3 bucket for storing pipeline artifacts
- Sets up a CodeBuild project for building Docker images
- Configures a CodePipeline with Source, Build, and Deploy stages
- Integrates with ECS for deployment
- Uses CodeStar connections for source code integration

## Usage

```hcl
module "codepipeline" {
  source = "./modules/codepipeline"

  project_name           = "kalakshetra"
  environment            = "dev"
  aws_region             = "ap-south-1"
  ecr_repository_url     = aws_ecr_repository.app.repository_url
  ecs_cluster_name       = module.ecs.cluster_name
  ecs_service_name       = module.ecs.service_name
  codestar_connection_arn = aws_codestarconnections_connection.github.arn
  repository_id          = "username/kalakshetra"
  branch_name            = "main"
  buildspec_path         = "buildspec.yml"
  tags                   = {
    Project     = "kalakshetra"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
```

## Requirements

- A CodeStar connection to your source code repository (GitHub, BitBucket, etc.)
- An existing ECR repository for storing Docker images
- An existing ECS cluster and service for deployment
- A buildspec.yml file in your source code repository

## Important Notes

After deploying this module, you need to manually activate the CodeStar connection in the AWS Console:

1. Go to the AWS Console
2. Navigate to Developer Tools > Settings > Connections
3. Find the connection created by this module
4. Click "Update pending connection" and follow the instructions to complete the connection

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| project_name | The name of the project | `string` | n/a | yes |
| environment | The environment (dev, staging, prod) | `string` | n/a | yes |
| aws_region | The AWS region to deploy resources | `string` | n/a | yes |
| ecr_repository_url | The URL of the ECR repository | `string` | n/a | yes |
| ecs_cluster_name | The name of the ECS cluster | `string` | n/a | yes |
| ecs_service_name | The name of the ECS service | `string` | n/a | yes |
| codestar_connection_arn | The ARN of the CodeStar connection | `string` | n/a | yes |
| repository_id | The ID of the repository (e.g., 'username/repository') | `string` | n/a | yes |
| branch_name | The branch name to use for the source code | `string` | `"main"` | no |
| buildspec_path | The path to the buildspec file | `string` | `"buildspec.yml"` | no |
| tags | A map of tags to add to all resources | `map(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| codepipeline_name | The name of the CodePipeline |
| codepipeline_arn | The ARN of the CodePipeline |
| artifacts_bucket_name | The name of the S3 bucket used to store pipeline artifacts |
| codebuild_project_name | The name of the CodeBuild project |
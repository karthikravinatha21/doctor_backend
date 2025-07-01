#!/bin/bash
set -e

# Configuration
PROJECT_NAME="kalakshetra"
ENVIRONMENT="prod"
AWS_REGION="ap-south-1"
ECR_REPOSITORY="${PROJECT_NAME}-${ENVIRONMENT}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install it first."
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]; then
    echo "Failed to get AWS account ID. Make sure you have the correct AWS credentials configured."
    exit 1
fi

# Destroy Terraform resources
echo "Destroying Terraform resources..."
cd terraform
terraform destroy -auto-approve

# Delete ECR repository
echo "Deleting ECR repository..."
aws ecr delete-repository --repository-name ${ECR_REPOSITORY} --force --region ${AWS_REGION} || true

echo "Resources destroyed successfully!"

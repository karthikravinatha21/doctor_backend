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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
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

# Build and push Docker image
echo "Building Docker image..."
docker build -t ${PROJECT_NAME}:latest .

# Log in to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_REGION} || \
    aws ecr create-repository --repository-name ${ECR_REPOSITORY} --region ${AWS_REGION}

# Tag and push the image
echo "Tagging and pushing image to ECR..."
docker tag ${PROJECT_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Initialize and apply Terraform
echo "Initializing Terraform..."
cd terraform
terraform init

echo "Applying Terraform configuration..."
terraform apply -auto-approve

# Get the ALB DNS name
ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
echo "Application deployed successfully!"
echo "You can access the application at: http://${ALB_DNS_NAME}"

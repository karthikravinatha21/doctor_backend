output "app_name" {
  description = "Name of the CodeDeploy application"
  value       = aws_codedeploy_app.app.name
}

output "deployment_group_name" {
  description = "Name of the CodeDeploy deployment group"
  value       = aws_codedeploy_deployment_group.deployment_group.deployment_group_name
}

output "codedeploy_role_arn" {
  description = "ARN of the IAM role used by CodeDeploy"
  value       = aws_iam_role.codedeploy.arn
}
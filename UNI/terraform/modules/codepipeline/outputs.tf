output "pipeline_arn" {
  description = "ARN of the CodePipeline"
  value       = aws_codepipeline.pipeline.arn
}

output "artifacts_bucket_name" {
  description = "Name of the S3 bucket used to store pipeline artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "pipeline_role_arn" {
  description = "ARN of the IAM role used by the pipeline"
  value       = aws_iam_role.codepipeline.arn
}
# Create an S3 bucket for static files
resource "aws_s3_bucket" "static" {
  bucket = "${var.project_name}-${var.environment}-static-files"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-static-files"
    }
  )
}

# Configure bucket ownership controls
resource "aws_s3_bucket_ownership_controls" "static" {
  bucket = aws_s3_bucket.static.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# Configure public access block
resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Configure bucket ACL
resource "aws_s3_bucket_acl" "static" {
  depends_on = [
    aws_s3_bucket_ownership_controls.static,
    aws_s3_bucket_public_access_block.static,
  ]

  bucket = aws_s3_bucket.static.id
  acl    = "public-read"
}

# Configure CORS for the bucket
resource "aws_s3_bucket_cors_configuration" "static" {
  bucket = aws_s3_bucket.static.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Configure bucket policy to allow public read access
resource "aws_s3_bucket_policy" "static" {
  bucket = aws_s3_bucket.static.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.static.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.static]
}
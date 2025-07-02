# Create a security group for database access
resource "aws_security_group" "db_access" {
  name        = "${var.project_name}-${var.environment}-db-access-sg"
  description = "Security group for database access"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-access-sg"
    }
  )
}

# Create rules for the security group
resource "aws_security_group_rule" "db_access_prod" {
  count = var.environment == "prod" ? 1 : 0

  type                     = "ingress"
  from_port               = 5432
  to_port                 = 5432
  protocol                = "tcp"
  source_security_group_id = aws_security_group.db_access.id
  security_group_id       = aws_security_group.db_access.id
}

resource "aws_security_group_rule" "db_access_non_prod" {
  count = var.environment != "prod" ? 1 : 0

  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.db_access.id
}
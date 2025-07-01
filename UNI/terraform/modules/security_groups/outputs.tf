output "db_access_sg_id" {
  description = "ID of the database access security group"
  value       = aws_security_group.db_access.id
}
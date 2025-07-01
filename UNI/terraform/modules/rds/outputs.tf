output "db_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = split(":", aws_db_instance.main.endpoint)[0]
}

output "db_name" {
  description = "The name of the database"
  value       = aws_db_instance.main.db_name
}

output "db_username" {
  description = "The username for the database"
  value       = aws_db_instance.main.username
}

output "db_port" {
  description = "The port of the RDS instance"
  value       = aws_db_instance.main.port
}
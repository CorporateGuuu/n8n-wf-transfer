output "vpc_id" {
  description = "Reference VPC identifier."
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "Public subnet identifiers intended for edge/load-balancer resources."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet identifiers intended for application and data services."
  value       = aws_subnet.private[*].id
}

output "alb_security_group_id" {
  description = "Security group for the public load-balancer boundary."
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "Security group for private application workloads."
  value       = aws_security_group.app.id
}

output "database_security_group_id" {
  description = "Security group for PostgreSQL workloads."
  value       = aws_security_group.database.id
}

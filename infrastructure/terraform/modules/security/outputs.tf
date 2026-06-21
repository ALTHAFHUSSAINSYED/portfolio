output "security_group_id" {
  value       = aws_security_group.portfolio_sg.id
  description = "The ID of the security group"
}

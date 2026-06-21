output "vpc_id" {
  value       = data.aws_vpc.default.id
  description = "The ID of the default VPC"
}

output "subnet_ids" {
  value       = data.aws_subnets.default.ids
  description = "The IDs of the subnets inside the default VPC"
}

variable "instance_type" {
  type        = string
  description = "The EC2 instance type"
}

variable "key_name" {
  type        = string
  description = "Key pair name for EC2 instance"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID to launch the EC2 instance in"
}

variable "security_group_ids" {
  type        = list(string)
  description = "List of security group IDs to associate with the EC2 instance"
}

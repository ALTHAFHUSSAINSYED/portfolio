variable "aws_region" {
  type        = string
  description = "AWS provider configuration"

}

variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"

}

variable "key_name" {
  type        = string
  description = "Key pair name for EC2 instance"
}




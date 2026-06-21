module "networking" {
  source = "./modules/networking"
}

module "security" {
  source        = "./modules/security"
  vpc_id        = module.networking.vpc_id
  ingress_rules = var.ingress_rules
}

module "compute" {
  source             = "./modules/compute"
  instance_type      = var.instance_type
  key_name           = var.key_name
  subnet_id          = module.networking.subnet_ids[0]
  security_group_ids = [module.security.security_group_id]
}

# Declarative moved blocks to preserve state without recreation
moved {
  from = aws_security_group.portfolio_sg
  to   = module.security.aws_security_group.portfolio_sg
}

moved {
  from = aws_instance.portfolio_instance
  to   = module.compute.aws_instance.portfolio_instance
}
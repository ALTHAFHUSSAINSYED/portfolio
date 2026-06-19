terraform {
  backend "s3" {
    bucket  = "althaf-blogs-storage"
    key     = "terraform.tfstate"
    region  = "ap-south-1"
    encrypt = true
  }
}
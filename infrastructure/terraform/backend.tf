terraform {
  backend "s3" {
    bucket       = "althaf-blogs-storage"
    key          = "terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true # Enables native S3 state locking (supported in Terraform v1.10+)

    # State Locking via DynamoDB (Alternative for Terraform < v1.10):
    # To use DynamoDB state locking instead of native S3 locking, comment out use_lockfile and use:
    # dynamodb_table = "your-dynamodb-table-name"
    # Note: The DynamoDB table must already exist and have a primary partition key named "LockID" (type String).
  }
}
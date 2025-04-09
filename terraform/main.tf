provider "aws" {
    region = "us-east-1"
}

variable "bucket_name" {
    description = "Enter a name for the s3 bucket."
    type = string
  
}

module "s3" {
  source = "./s3"
  bucket_name = var.bucket_name
}
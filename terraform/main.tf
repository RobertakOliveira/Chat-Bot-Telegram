provider "aws" {
    region = "us-east-1"
}

variable "stage_name" {
    description = "Enter a stage name."
    type = string  
}

variable "bucket_name" {
    description = "Enter a name for the s3 bucket."
    type = string
  
}

module "s3" {
  source = "./s3"
  bucket_name = var.bucket_name
}

module "ec2" {
    source = "./ec2"
}

module "ecr" {
    source = "./ecr" 
}

output "ecr_url" {
    value = module.ecr.ecr_repository_url
}
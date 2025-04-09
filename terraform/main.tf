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

module "apigw" {
    source = "./api-gateway"
    stage_name = var.stage_name
    bucket_name = var.bucket_name
}

module "s3" {
  source = "./s3"
  bucket_name = var.bucket_name
}
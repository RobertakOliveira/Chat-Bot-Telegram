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

variable "ssh_ip" {
    description = "IP to allow for SSH connections to the EC2 instance."
    type = string
}

variable "key_name" {
    description = "Key to connect to instance via SSH."
    type = string
}

module "ec2" {
    source = "./ec2"
    ssh_ip = var.ssh_ip
    key_name = var.key_name
}
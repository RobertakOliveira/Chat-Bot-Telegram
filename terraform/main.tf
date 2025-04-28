provider "aws" {
    region = "us-east-1"
}

variable "bucket_name" {
    description = "Enter a name for the s3 bucket."
    type = string
  
}

variable "key_name" {
    description = "Key to connect to instance via SSH."
    type = string
}

variable "ssh_ip" {
    description = "IP to allow for SSH connections to the EC2 instance."
    type = string
}


module "s3" {
  source = "./s3"
  bucket_name = var.bucket_name
}

module "ec2" {
    source = "./ec2"
    key_name = var.key_name
    ssh_ip = var.ssh_ip
}
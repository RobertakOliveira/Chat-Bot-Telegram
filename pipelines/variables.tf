variable "aws_region" {
  description = "The AWS region to deploy"
  type        = string
  default     = "us-east-1"
}
variable "bucket_name" {}
variable "lambda_name" {}
variable "telegram_token" {}
variable "log_group_name" {}
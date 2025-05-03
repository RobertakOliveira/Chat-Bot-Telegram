output "start_lambda_arn" {
  description = "ARN da Lambda de start"
  value       = aws_lambda_function.start_ec2.arn
}

output "stop_lambda_arn" {
  description = "ARN da Lambda de stop"
  value       = aws_lambda_function.stop_ec2.arn
}
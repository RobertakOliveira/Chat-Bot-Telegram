output "workflow_arn" {
  description = "ARN da máquina de estados (Step Function)"
  value       = aws_sfn_state_machine.workflow.arn
}

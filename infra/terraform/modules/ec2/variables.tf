variable "ami" {
  description = "AMI ID para a instância"
  type        = string
}

variable "instance_type" {
  description = "Tipo da instância EC2"
  type        = string
}

variable "subnet_id" {
  description = "ID da subnet"
  type        = string
}

variable "security_group_id" {
  description = "ID do security group"
  type        = string
}

variable "log_group_name" {
  description = "Nome do grupo de logs vindo do módulo cloudwatch"
  type        = string
}

variable "iam_instance_profile_name" {
  description = "Nome do IAM Instance Profile"
  type        = string
}

variable "s3_bucket_name" {
  description = "Nome do bucket S3 onde estão os arquivos da aplicação"
  type        = string
}

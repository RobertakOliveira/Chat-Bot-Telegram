variable "aws_region" {
  description = "Região AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "owner_tag" {
  description = "Identificador do dono/dono dos recursos"
  type        = string

}

variable "instance_type" {
  description = "Tipo de instância EC2"
  type        = string
  default     = "t2.micro"
}

variable "vpc_cidr" {
  description = "Bloco CIDR para a VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "project_name" {
  description = "Nome do projeto para tagging"
  type        = string
  default     = "consultor-juridico"
}

variable "aws_assume_role_arn" {
  description = "ARN da IAM Role para assumir"
  type        = string


}

variable "common_tags" {
  description = "Tags comuns aplicadas a todos os recursos"
  type        = map(string)
  default = {
    ManagedBy  = "Terraform"
    Repository = "https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro"
    CostCenter = "TI"

  }
}


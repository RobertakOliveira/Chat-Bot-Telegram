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

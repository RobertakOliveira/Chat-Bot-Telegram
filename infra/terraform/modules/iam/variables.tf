variable "role_name" {
  description = "Nome da IAM Role a ser criada"
  type        = string
}

variable "service" {
  description = "Serviço que terá permissão para assumir esta role"
  type        = string
  default     = "ec2.amazonaws.com"
}

variable "policy_name" {
  description = "Nome da política a ser criada e associada à role"
  type        = string
}

variable "policy_json" {
  description = "Documento JSON com a definição da política"
  type        = string
  default     = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

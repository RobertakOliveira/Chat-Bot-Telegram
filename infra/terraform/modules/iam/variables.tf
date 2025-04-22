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
      "Sid": "S3ReadWrite",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "*"
    },
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:GetModel",
        "bedrock:ListModels",
        "bedrock:DescribeModel",
        "bedrock:List*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

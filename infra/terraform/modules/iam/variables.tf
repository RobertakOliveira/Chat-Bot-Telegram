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
  description = "Template da política IAM com placeholders"
  type        = string
  default     = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Permissions",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Sid": "BedrockPermissions",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:GetModel",
        "bedrock:ListModels"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchPermissions",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
        "cloudwatch:PutMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DescribeAlarms",
        "cloudwatch:DeleteAlarms"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}
EOF
}

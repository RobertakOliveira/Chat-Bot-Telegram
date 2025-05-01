resource "aws_iam_role" "chatbot_role" {
  name = "chatbot-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })

  tags = merge(var.common_tags, {
    Name = "Chatbot-Role-${var.environment}"
  })

   lifecycle {
    ignore_changes = [name]  # Evita conflitos se a role já existir
}
}

resource "aws_iam_role_policy_attachment" "ssm_managed_instance" {
  role       = aws_iam_role.chatbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "chatbot_policy" {
  name = "chatbot-policy-${var.environment}"
  role = aws_iam_role.chatbot_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["bedrock:*"],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action = ["s3:*"],
        Effect = "Allow",
        Resource = [
           "${var.s3_bucket_arn}",
          "${var.s3_bucket_arn}/*"
        ]
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action = [
          "ec2:RunInstances",
          "ec2:DescribeInstances",
          "ec2:TerminateInstances",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:CreateSecurityGroup",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:DescribeSecurityGroups",
          "ec2:CreateTags",
          "ec2:AllocateAddress",
          "ec2:AssociateAddress",
          "ec2:DescribeVolumes",
          "ec2:AttachVolume",
          "ec2:DetachVolume"
        ],
        Effect   = "Allow",
        Resource = "*",
        Condition = {
          StringEquals = {
            "aws:RequestTag/CostCenter" = "TI"
          }
        }
      },
      {
        Action   = ["iam:PassRole"],
        Effect   = "Allow",
        Resource = aws_iam_role.chatbot_role.arn
      },
      {
        Action = [
          "ec2:CreateVpc",
          "ec2:DescribeVpcs",
          "ec2:DeleteVpc",
          "iam:CreateRole",
          "iam:PutRolePolicy"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "chatbot_profile" {
  name = "chatbot-profile-${var.environment}"
  role = aws_iam_role.chatbot_role.name

  lifecycle {
    ignore_changes = [name]
  }
}


resource "aws_iam_role_policy_attachment" "ec2_read_only" {
  role       = aws_iam_role.chatbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}
# Policies com least privilege, significa que as permissões concedidas são as mínimas necessárias para realizar as operações necessárias.
# Isso é importante para garantir a segurança e a conformidade, minimizando o risco de acesso não autorizado ou ações indesejadas.

resource "random_id" "policy_suffix" {
  byte_length = 4
}

resource "aws_iam_policy" "bedrock_access" {
  name        = "bedrock-access-${random_id.policy_suffix.hex}"
  description = "Permissões mínimas para Bedrock"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })
}
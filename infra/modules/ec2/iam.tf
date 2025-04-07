# Policies com least privilege, significa que as permissões concedidas são as mínimas necessárias para realizar as operações necessárias.
# Isso é importante para garantir a segurança e a conformidade, minimizando o risco de acesso não autorizado ou ações indesejadas.

resource "aws_iam_policy" "bedrock_access" {
  name        = "bedrock-${random_id.policy_suffix.hex}"  # Nome não descritivo
  description = "Permissões mínimas para Bedrock"

  policy = jsonencode({       # Aplicar a politica de IAM
    Version = "2012-10-17",
    Statement = [{
      Action   = ["bedrock:InvokeModel"],  # Escopo restrito
      Effect   = "Allow",
      Resource = "*"
    }]
  })
}
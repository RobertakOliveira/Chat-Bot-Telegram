# ARQUIVO .terraform.lock.hcl
# ==========================
# Este arquivo é GERADO AUTOMATICAMENTE pelo Terraform e DEVE SER COMITADO no Git.
# Ele serve para "travar" as versões exatas dos providers usados no projeto,
# garantindo que todos os ambientes e membros da equipe usem as mesmas versões.

# Bloco do provider AWS
# ---------------------
provider "registry.terraform.io/hashicorp/aws" {
  # Versão exata do provider AWS sendo usada
  version     = "5.94.1"
  
  # Restrição de versão definida na configuração (aceita qualquer 5.x.x >= 5.0.0)
  constraints = "~> 5.0"
  
  # Hashes de verificação para diferentes plataformas (garantem integridade do provider)
  hashes = [
    # Hash principal (usado para verificação)
    "h1:/BQk0OxJ3bsdISapaAe+AKeEH/ZUr1BBZo41qUvJ81c=",
    
    # Hashes específicos para diferentes sistemas operacionais/arquiteturas:
    "zh:14fb41e50219660d5f02b977e6f786d8ce78766cce8c2f6b8131411b087ae945", # Linux AMD64
    "zh:3bc5d12acd5e1a5f1cf78a7f05d0d63f988b57485e7d20c47e80a0b723a99d26", # Linux ARM64
    "zh:4835e49377f80a37c6191a092f636e227a9f086e3cc3f0c9e1b554da8793cfe8", # Windows AMD64
    # ... (outras plataformas)
  ]
}

# Bloco do provider Random
# ------------------------
provider "registry.terraform.io/hashicorp/random" {
  # Versão exata do provider Random
  version = "3.7.1"
  
  # Hashes de verificação:
  hashes = [
    "h1:Jvr+8mqBJlxSOF8R862ZtezBlCb9pVwNMNc1sYsDeYg=", # Hash principal
    "zh:3193b89b43bf5805493e290374cdda5132578de6535f8009547c8b5d7a351585", # Linux AMD64
    "zh:3218320de4be943e5812ed3de995946056db86eb8d03aa3f074e0c7316599bef", # Linux ARM64
    # ... (outras plataformas)
  ]
}

# POR QUE ISSO É IMPORTANTE?
# =========================
# 1. EVITA "MAS NO MEU COMPUTADOR FUNCIONA":
#    - Garante que todos usem as MESMAS versões dos providers
#
# 2. SEGURANÇA:
#    - Os hashes verificam se o provider baixado é autêntico e não foi alterado
#
# 3. REPRODUTIBILIDADE:
#    - Seu projeto continuará funcionando mesmo se novas versões dos providers saírem
#
# QUANDO ATUALIZAR?
# =================
# Se você rodar:
# - `terraform init` → Mantém as versões travadas
# - `terraform init -upgrade` → Atualiza para as versões mais novas dentro das constraints
#
# LEMBRE-SE:
# Sempre comite as mudanças neste arquivo quando:
# - Adicionar novos providers
# - Atualizar versões existentes
# - Modificar constraints de versão
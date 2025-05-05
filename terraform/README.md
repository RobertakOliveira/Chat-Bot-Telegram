<div align="justify">

# ⚖️ AdvogaBot - Infraestrutura (AWS + Terraform)

<div align="center">
  <img src="../assets/ChatBot.png" alt="AdvogaBot" width="300" height="300">
</div>

Este módulo provisiona toda a infraestrutura necessária para o funcionamento do **AdvogaBot**, incluindo instâncias EC2, buckets S3, repositórios de logs e permissões de segurança, utilizando **Terraform** como IaC (Infrastructure as Code).

---
## 📖 Índice

1. [Tecnologias Utilizadas](#⚙️-tecnologias-utilizadas)
2. [Estrutura de Pastas](#📂-estrutura-de-pastas)
3. [Pré-requisitos](#📋-pré-requisitos)
4. [Recursos Criados](#📦-recursos-criados)
5. [Instalação da AWS CLI](#☁️-instalação-da-aws-cli)
6. [Configuração do AWS CLI com SSO](#🔐-configuração-do-aws-cli-com-sso)
7. [Instalação do Terraform no WSL](#🧱-instalação-do-terraform-no-wsl)
8. [Provisionamento com Terraform](#🚀-provisionamento-com-terraform)

## ⚙️ Tecnologias Utilizadas

- [Terraform](https://www.terraform.io/)
- [AWS EC2](https://aws.amazon.com/ec2/)
- [AWS S3](https://aws.amazon.com/s3/)
- [AWS IAM](https://aws.amazon.com/iam/)
- [AWS CloudWatch Logs e Metrics](https://aws.amazon.com/cloudwatch/)
- [AWS VPC](https://aws.amazon.com/vpc/)

## 📂 Estrutura de Pastas

```
terraform/
├── 🗂️ .terraform/                                      # Diretório interno do Terraform
│   └── 📂 providers/registry.terraform.io/hashicorp/
│       ├── 📦 aws/                                     # Plugin AWS
│       ├── 📄 local/                                   # Plugin local
│       └── 🔐 tls/                                     # Plugin TLS
├── 📂 aws/                                             # Artefatos do provider AWS
│   ├── ⚙️ install                                      # Script/instruções de instalação
│   ├── 📄 README.md                                    # Documentação do provider AWS
│   └── 📄 THIRD_PARTY_LICENSES                         # Licenças de terceiros
├── 🔒 .terraform.lock.hcl                              # Lock de versão dos providers
├── 📄 ec2.tf                                           # Definições de instâncias EC2
├── 📄 iam.tf                                           # Roles e policies IAM
├── 🔑 key_par.tf                                       # Par de chaves SSH
├── 📄 main.tf                                          # Arquivo principal (chama módulos)
├── 📄 monitoring_budget_alert.tf                       # Alarme de orçamento
├── 📄 monitoring_cpu.tf                                # Alarme de CPU
├── 📄 outputs.tf                                       # Outputs (IPs, IDs etc.)
├── ⚙️ provider.tf                                      # Configuração do provider AWS
├── 📄 s3.tf                                            # Buckets S3
├── 📄 security_groups.tf                               # Security Groups
├── 📦 terraform_1.6.6_linux_amd64.zip                  # (remover do repositório)
├── 💾 terraform.tfstate                                # Estado local (não versionar)
├── 💾 terraform.tfstate.backup                         # Backup automático do estado
├── 📄 variables.tf                                     # Declaração de variáveis
├── 📄 volumes.tf                                       # Volumes EBS adicionais
└── 📄 vpc.tf                                           # VPC, subnets, roteamento
```

## 📋 Pré-requisitos

- Conta AWS com permissões para EC2, S3, IAM e CloudWatch.

- AWS CLI v2 instalado e configurado (via SSO ou credenciais).

- Terraform instalado no seu ambiente.
> Abaixo estão todos os passos necessários para atender aos requisitos

## 📦 Recursos Criados

- 📁 Bucket S3 para armazenamento de documentos jurídicos
- 🖥️ Instância EC2 para rodar o bot em produção
- 🔒 IAM Roles para permissões seguras
- 📊 Alarmes de monitoramento no CloudWatch
- 🌐 VPC personalizada para segurança de rede

--- 

## ☁️ Instalação da AWS CLI 

### 🛠️ Passo a passo para instalar a AWS CLI v2 no Ubuntu (via WSL)

1. **Atualize seu sistema**

```bash
sudo apt update && sudo apt upgrade -y
```

2. **Instale dependências**

```bash
sudo apt install -y unzip curl
```

3. **Baixe o instalador da AWS CLI v2**

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
```

4. **Extraia o arquivo**

```bash
unzip awscliv2.zip
```

5. **Execute o instalador**

```bash
sudo ./aws/install
```

6. **Verifique a instalação**

```bash
aws --version
```
Saída esperada:

```
aws-cli/2.x.x Python/3.x Linux/x86_64
```

---

### 🧹 Limpeza (opcional)

Após a instalação, você pode apagar os arquivos baixados:

```bash
rm -rf aws awscliv2.zip
```
---

### 🔐 Configuração  do AWS CLI com SSO

Se sua conta AWS utiliza autenticação via SSO (Single Sign-On), siga os passos abaixo:

```bash
aws configure sso --profile <nome-do-perfil>
```

Durante o processo, você informará:

```
SSO session name (Recommended): seu-usuario
SSO start URL [None]: https...
SSO region [None]: us-east-1
SSO registration scopes [sso:account:access]: (pressione Enter)
```

Após isso, o terminal tentará abrir o navegador. **Se estiver no WSL e não funcionar automaticamente**, copie o link exibido no terminal e cole no navegador do Windows para autorizar o acesso.

---

### 💡 Dica: Login manual (caso o navegador não abra automaticamente)

Se estiver usando o WSL, é comum que o navegador **não abra sozinho**. Nesse caso, você tem duas opções:

### 🔁 Opção 1: Login interativo (recomendado para WSL)

Use o comando:

```bash
aws sso login --profile seu-usuario --no-browser
```
Esse comando exibirá um **link** e um **código de verificação** como este:

```
To sign in, use a web browser to open the page https://device.sso.us-east-1.amazonaws.com/
```

Copie o link e cole no navegador do **Windows**. A sessão será iniciada com sucesso.

### ✅ Teste sua sessão

---

Para confirmar que o login está funcionando, execute:

```bash
aws s3 ls --profile seu-usuario
```

Você verá a lista de buckets (caso tenha permissão).

### 🔐 Configuração inicial (se você já tiver chaves da AWS)

```bash
aws configure --profile seu-usuario
```

Você vai preencher:

- AWS Access Key ID
- AWS Secret Access Key
- Region (ex: `us-east-1`)
- Output format (ex: `json`)

---

A AWS CLI está instalada e configurada no seu Ubuntu WSL. Você já pode testar comandos como:

```bash
aws s3 ls
```

### 🧱 Instalação do Terraform no WSL

### ✅ Pré-requisitos

- WSL instalado com Ubuntu (ex: `Ubuntu 24.04 LTS`)
- Acesso ao terminal do Ubuntu (`wsl` ou `wsl -d Ubuntu`)
- Conexão com a internet

### 🛠️ Passo a passo

1. **Atualize os pacotes do sistema**
    
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
    
2. **Instale dependências necessárias**
    
    ```bash
    sudo apt install -y gnupg software-properties-common curl
    ```
    
3. **Adicione a chave GPG da HashiCorp**
    
    ```bash
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    ```
    
4. **Adicione o repositório oficial do Terraform**
    
    ```bash
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    ```
    
5. **Atualize a lista de pacotes**
    
    ```bash
    sudo apt update
    ```
    
6. **Instale o Terraform**
    
    ```bash
    sudo apt install terraform -y
    ```
    
7. **Verifique se a instalação foi bem-sucedida**
    
    ```bash
    terraform -v
    ```
    
    Saída esperada:
    
    ```
    Terraform v1.x.x
    ```  
---

## 🚀 Provisionamento com o Terraform
> Antes de iniciar, **edite os arquivos `provider.tf` e `variables.tf`**:
> - Em `provider.tf`, substitua `<seu_usuario>` pelo nome do seu perfil AWS.
> - Em `variables.tf`, defina o nome desejado para o bucket S3.

1. Navegue até a pasta de infraestrutura:
```bash
    cd terraform
```
2. Inicialize o Terraform:
```bash
    terraform init
```
3. Revise o plano:
```bash
    terraform plan
```
4. Aplique as mudanças:
```bash
    terraform apply
```
</div>
# Avaliação das Sprints 7 e 8 - Programa de Bolsas Compass UOL / AWS - turma janeiro/2025

Avaliação das sétima e oitava sprints do programa de bolsas Compass UOL para formação em Inteligência Artificial para AWS.

# 🌐 Integração: Bot de Telegram + API de Chatbot com RAG

Este documento descreve o processo de criação e configuração da comunicação entre o bot do Telegram e a API formulada para a avaliação.

---

## 🎯 Objetivo

Criar um bot no Telegram que faça uso de uma API para consultar documentos jurídicos e responder sobre eles.

## ⚒️ Infraestrutura

- API em EC2, rodando com Flask, servida por Gunicorn e com Nginx como proxy reverso.
- Bucket S3 para armazenamento dos documentos jurídicos on-line.

A aplicação é Dockerizada e pode ser subida para a AWS com uso de Terraform.

---

## Subindo e Rodando a API

> Pré-requisitos: para testes locais, tenha instalado em sua máquina Docker. Para subir para a AWS, é necessário ter instalado Terraform.

1. Faça download do repositório, seja manualmente ou com uso de `git`.

2. Obtenha um *key pair* na AWS. Ele será usado pela EC2 para permitir conexões SSH.
  
    Para isso, vá em `EC2 > Network & Security > Key Pairs`. Clique em `Create Key Pair`. Escolha um nome, o tipo como "RSA" e o formato como ".pem". Clique, novamente em `Create Key Pair`. **Será feito o download de um arquivo .pem**. Guarde-o, pois será necessário usá-lo para acessar a instância EC2.

3. No diretório onde for feito o download, mova para a pasta de `terraform/`:

    ```bash
    terraform init
    terraform plan
    ```
    Várias perguntas serão feitas para preencher os dados necessários para subir a infraestrutura. Entre eles, o nome do Key Pair criado anteriormente! Também, o nome do Bucket - o qual deve ser único - e o endereço IP a que permitir conexões SSH.
    > Obs.: o endereço IP próprio pode ser visualizado no próprio console da AWS ao editar uma inbound ou outbound rule, em um Security Group e selecionar "My IP" em "Source". Cuidado, entretanto, para não realizar modificações indesejadas. Na dúvida, cancele.
    
    Caso toda a infraestrutura esteja adequada, podem-se aplicar as mudanças com:
    ```bash
    terraform apply
    ```
  
  4. Se as mudanças foram corretamente aplicadas, deve ter sido criado um bucket em sua conta AWS com o nome especificado. Faça upload dos documentos jurídicos desejados para ele.
  
  5. Mova de volta para o diretório raiz (onde estiver o repositório). Crie o arquivo `.env`, com base em `.env.example`:
  
      ```bash
      cp .env.example .env
      ```
      Preencha o arquivo `.env` gerado com as informações desejadas. Faça uso do que desejar do exemplo.

  6. Copie o código para a EC2:

      ```bash 
      rsync -avrz -e "ssh -i <CAMINHO_ARQUIVO_PEM>" <CAMINHO_DIRETORIO_ATUAL> ec2-user@<IP_PUBLICO_DA_EC2>:/home/ec2-user/api/ --exclude-from=copy-ignore.txt
      ```
      > Obs.: Troque os valores entre '<' e '>' pelos dados correspondentes.
    
  7. Por último, entre na EC2 com SSH e vá para /api/:
      ```bash 
      ssh -i "<CAMINHO_ARQUIVO_PEM>" ec2-user@<IP_PUBLICO_DA_EC2>
      ```
      ```bash 
        cd api/
      ```
      E, se não houver sido feito automaticamente, rode o script de inicialização na EC2. Ele se encontra em `terraform/ec2/start-script.sh`.
      ```bash 
      <comandos_do_script>
      ```

Após esses passos, é espero que o servidor esteja rodando normalmente. Isso ficará evidente pelos logs emitidos após execução do script de inicialização.
Caso não rode automaticamente, use `docker compose up --build`.

---

## Como configurar o Bot do Telegram?

### 1. Criação do Bot no Telegram
- Foi utilizado o **@BotFather** para criar o bot.
- Comando: `/newbot`
- O bot gerado recebeu um **TOKEN**, que foi salvo para uso posterior.
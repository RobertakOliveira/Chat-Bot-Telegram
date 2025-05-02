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

## ⚙️ Como criar e configurar o Bot do Telegram?

### 1. Criação do Bot no Telegram

1. Abra o app do Telegram e procure por [@BotFather](https://t.me/BotFather).
2. Envie o comando `/start` e depois `/newbot`.
3. Escolha o nome de exibição do seu bot.
4. Escolha um nome de usuário para o seu bot (deve terminar em `bot` - ex: `Chatbot_Juridico_bot`).
5. Copie e salve o **token** que o BotFather fornecer, pois ele será usado no `.env`.

### 2. Configurações possíveis com o BotFather:

* `/setdescription` – Define a descrição do seu bot.
* `/setabouttext` – Define o texto "Sobre" exibido no perfil do bot.
* `/setuserpic` – Define uma foto de perfil.
* `/deletebot` – Remove permanentemente o bot.
* `/setcommands` – Define comandos personalizados visíveis no menu do bot.

  **Exemplos de uso do `/setcommands`:**

  ```
  start - Inicia o bot
  ajuda - Mostra informações sobre o funcionamento do bot
  sobre - Exibe informações sobre o projeto
  ```
---

## ❗Problemas encontrados durante o desenvolvimento do projeto

Durante o processo de desenvolvimento e implantação do chatbot, nos deparamos com alguns obstáculos que exigiram mudanças estratégicas na arquitetura do projeto. Abaixo estão alguns dos principais empecilhos encontrados:

---

### 🔹 Limite de tamanho das bibliotecas na AWS Lambda

Logo no início da atividade, ao tentar implementar o chatbot em uma função AWS Lambda, foi identificado que o **tamanho das bibliotecas necessárias ultrapassava o limite máximo** permitido para as layers, impossibilitando a execução da lógica do bot nesse formato.

✅ **Solução:**
Foi adotada a abordagem com **EC2 + Docker**, permitindo rodar o bot com todas as dependências necessárias sem restrições de tamanho.

---

### 🔹 Exigência de certificado HTTPS válido pelo Telegram

Para utilizar Webhook com a API do Telegram, o endpoint do servidor precisa obrigatoriamente estar acessível via **HTTPS, com um certificado digital válido**. Portanto, seria necessário configurar um domínio público e certificado SSL, o que aumentaria a complexidade e o custo da infraestrutura.

✅ **Solução:**
Foi adotado o modelo com **Polling**, onde o próprio bot consulta periodicamente o Telegram, em vez de receber requisições sempre que chega uma nova mensagem. Essa abordagem **elimina a necessidade de HTTPS**, facilitando o desenvolvimento do projeto.

---
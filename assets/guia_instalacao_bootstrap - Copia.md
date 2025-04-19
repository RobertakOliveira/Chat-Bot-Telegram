# 📦 Guia de Instalação do Projeto via Script `bootstrap.sh`

Este tutorial vai te guiar passo a passo para clonar e instalar o projeto de forma segura, mesmo que o repositório seja privado. Cada integrante do time vai usar um token próprio, garantindo segurança e rastreabilidade.

---

## 🚀 Passo a passo

### 1. 📋 Gerar um Personal Access Token (PAT)

1. Acesse: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Preencha com:
   - **Note**: `Token Chatbot EC2`
   - **Expiration**: 90 days (recomendado)
   - **Scopes**: Marque apenas `repo`
4. Clique em **Generate token**
5. Copie e **salve em lugar seguro**

---

### 2. 🔐 Criar arquivo `.env_bootstrap`

Na sua máquina (ou na EC2), crie o arquivo oculto com seu token:

```bash
nano ~/.env_bootstrap
```

Cole dentro:

```bash
GITHUB_TOKEN=seu_token_aqui
```

Salve com `CTRL + O` e saia com `CTRL + X`.

> 🧠 Esse arquivo será lido automaticamente pelo script `bootstrap.sh`.

---

### 3. ⚙️ Rodar o script de provisionamento

Depois que o arquivo `.env_bootstrap` estiver criado, execute:

```bash
chmod +x bootstrap.sh
sudo ./bootstrap.sh
```

O script vai:
- Verificar a internet
- Clonar o repositório privado
- Instalar dependências
- Criar ambiente Python e `.env`
- Configurar e iniciar o serviço + nginx

---

### ✅ Tudo certo!

Você verá a mensagem:

```
[INFO] Provisionamento concluído com sucesso!
```

Agora é só acessar a aplicação via IP público da EC2! 🎉

---

## 💬 Dúvidas?

Fale com @Kat no grupo do projeto!
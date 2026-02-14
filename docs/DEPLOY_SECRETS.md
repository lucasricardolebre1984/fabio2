# 🔐 Geração de Secrets para Produção

**Projeto:** FC Soluções Financeiras  
**Data:** 14/02/2026  
**Importância:** 🔴 CRÍTICA - Não fazer deploy sem trocar secrets!

---

## ⚠️ ATENÇÃO

**NUNCA use os valores de exemplo em produção!**

Os valores presentes em `.env.example` e `docker-compose.yml` são apenas para desenvolvimento local. Em produção, todos os secrets devem ser únicos e fortes.

---

## 🔑 Secrets Obrigatórios

### 1. SECRET_KEY (Backend JWT)

**Descrição:** Chave secreta para assinatura de tokens JWT  
**Requisitos:** Mínimo 32 caracteres, alta entropia

**Gerar:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Exemplo de saída:**
```
vK3x8mN9pQ4rT7wY2zB5cF6gH1jL0kM_4dE8fG9hI
```

---

### 2. EVOLUTION_API_KEY (WhatsApp)

**Descrição:** Chave de autenticação da Evolution API  
**Requisitos:** Mínimo 32 caracteres

**Gerar:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 3. OPENAI_API_KEY

**Descrição:** Chave da API OpenAI para o modelo da VIVA  
**Onde obter:** https://platform.openai.com/api-keys

**Formato:**
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ Importante:**
- Use uma chave de PRODUÇÃO (não a de desenvolvimento)
- Configure limits de uso no dashboard da OpenAI
- Monitore consumo regularmente

---

### 4. MINIMAX_API_KEY e MINIMAX_GROUP_ID

**Descrição:** Credenciais para voz institucional da VIVA (TTS)  
**Onde obter:** Dashboard MiniMax (se aplicável)

---

### 5. DATABASE_URL

**Descrição:** String de conexão do PostgreSQL  
**Formato:**
```
postgresql+asyncpg://usuario:senha@host:porta/database
```

**Gerar senha forte:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

**Exemplo completo:**
```
postgresql+asyncpg://fabio2_user:AbC123xYz456mNo@localhost:5432/fabio2_prod
```

---

## 📝 Configuração no Servidor EC2

### Opção 1: Arquivo .env (Recomendado)

```bash
# No servidor EC2
cd /opt/fabio2

# Criar arquivo .env de produção
nano backend/.env
```

**Conteúdo do backend/.env:**
```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://fabio2_user:<SENHA_FORTE>@postgres:5432/fabio2

# Redis
REDIS_URL=redis://redis:6379/0

# Security (MUDE!)
SECRET_KEY=<SECRET_KEY_GERADO>

# WhatsApp
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=<EVOLUTION_KEY_GERADO>

# OpenAI
OPENAI_API_KEY=<SUA_CHAVE_OPENAI_PRODUCAO>

# MiniMax (opcional)
MINIMAX_API_KEY=<SUA_CHAVE_MINIMAX>
MINIMAX_GROUP_ID=<SEU_GROUP_ID>

# Storage
STORAGE_MODE=local
STORAGE_LOCAL_PATH=/app/storage

# Frontend
FRONTEND_BASE_URL=https://seudominio.com.br
```

### Opção 2: Variáveis de Ambiente Diretas

```bash
# Exportar variáveis (não persistente após reboot)
export SECRET_KEY="<secret_gerado>"
export EVOLUTION_API_KEY="<evolution_gerado>"
# ... etc
```

### Opção 3: Docker Secrets (Produção Avançada)

Para setups mais seguros, use Docker Secrets:

```bash
# Criar secrets
echo "<secret_key>" | docker secret create secret_key -
echo "<evolution_key>" | docker secret create evolution_key -

# Referenciar no docker-compose-prod.yml
secrets:
  secret_key:
    external: true
```

---

## ✅ Checklist de Validação

Antes de fazer deploy, confirmar:

- [ ] Todos os secrets foram trocados (não usar valores de .env.example)
- [ ] SECRET_KEY tem > 32 caracteres
- [ ] OPENAI_API_KEY é da conta de produção
- [ ] DATABASE_URL usa senha forte (não "fabio2_pass")
- [ ] EVOLUTION_API_KEY não é "default_key_change_in_production"
- [ ] Arquivo backend/.env tem permissões restritas (chmod 600)
- [ ] Secrets não estão commitados no git
- [ ] .gitignore inclui *.env

---

## 🔒 Boas Práticas de Segurança

### 1. Rotação de Secrets

Troque secrets regularmente:
- **SECRET_KEY:** A cada 90 dias ou após incidente
- **OPENAI_API_KEY:** Se suspeitar de vazamento
- **Database passwords:** Anualmente

### 2. Controle de Acesso

```bash
# Restringir permissões do arquivo .env
chmod 600 backend/.env
chown root:root backend/.env
```

### 3. Backup Seguro

**NÃO** fazer backup de secrets em plain text.

Use ferramentas como:
- AWS Secrets Manager
- HashiCorp Vault
- Ansible Vault

### 4. Monitoramento

- Configure alertas de uso anômalo da OPENAI_API_KEY
- Monitore logs de autenticação falha (SECRET_KEY comprometido?)
- Audite acessos ao banco regularmente

---

## 🚨 Em Caso de Vazamento

Se um secret foi exposto:

### 1. SECRET_KEY vazado

```bash
# 1. Gerar novo
NEW_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# 2. Atualizar .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_KEY/" backend/.env

# 3. Reiniciar backend
docker-compose restart backend

# 4. Invalidar todas as sessões antigas (usuários precisam fazer login de novo)
```

### 2. OPENAI_API_KEY vazado

```bash
# 1. Revogar chave comprometida no dashboard OpenAI
# 2. Gerar nova chave
# 3. Atualizar backend/.env
# 4. Reiniciar backend
```

### 3. DATABASE password vazado

```bash
# 1. Conectar ao Postgres
docker exec -it fabio2-postgres psql -U postgres

# 2. Trocar senha
ALTER USER fabio2_user WITH PASSWORD 'nova_senha_forte';

# 3. Atualizar DATABASE_URL no .env
# 4. Reiniciar stack
docker-compose restart
```

---

## 📞 Suporte

Em caso de dúvidas sobre secrets:
- Consulte a documentação oficial de cada serviço
- Evite enviar secrets por email/slack/whatsapp
- Use canais seguros (1Password, LastPass, etc)

---

*Documento criado em: 14/02/2026*  
*Última atualização: 14/02/2026*

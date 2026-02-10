# DEPLOY UBUNTU - Docker 100%

> **Projeto:** FC Soluções Financeiras SaaS  
> **Data:** 2026-02-05  
> **Objetivo:** Subir o sistema completo em um Ubuntu virgem, usando apenas Docker.

---

## Visão Geral

Este roteiro cobre o deploy completo (frontend, backend, banco, redis e Evolution API) em um servidor Ubuntu, com foco em ambiente limpo e institucional.

Etapas macro
1. **Etapa 1**: Roteiro de deploy 100% Docker (este documento).
2. **Etapa 2**: WhatsApp funcional e integrado ao backend.
3. **Etapa 3**: Protocolo final de produção (DNS, SSL, hardening).

---

## Arquivos de Compose (Fonte de Verdade)

Existem múltiplos arquivos no repositório. Para produção, use:

- **Canônico:** `docker-compose.prod.yml`  
- **Local:** `docker-compose.local.yml`  
- **Desenvolvimento:** `docker-compose.yml`  
- **Legado:** `docker-compose-prod.yml` (contém segredos e IPs fixos, não usar em produção)

**Observação:** a consolidação definitiva dos arquivos será feita na Etapa 3.

---

## Pré-requisitos do Servidor

- Ubuntu 22.04+ (limpo)
- Acesso SSH com usuário sudo
- DNS configurado para `fabio.automaniaai.com.br` apontando para o IP do servidor
- Portas liberadas no firewall: 80 e 443  
  Porta 8080 somente se quiser acessar o Evolution Manager externamente.

---

## Variáveis de Ambiente (Produção)

Crie um arquivo `.env.prod` no servidor (não commitar).

Obrigatórias
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `SECRET_KEY`
- `NEXT_PUBLIC_API_URL`
- `EVOLUTION_API_KEY`
- `ZAI_API_KEY`

Recomendadas
- `CORS_ORIGINS` (domínio e variações)

Exemplo mínimo
```
DB_USER=fabio2_user
DB_PASSWORD=troque_esta_senha
DB_NAME=fabio2
SECRET_KEY=troque_esta_chave
NEXT_PUBLIC_API_URL=https://fabio.automaniaai.com.br/api/v1
EVOLUTION_API_KEY=troque_esta_chave
ZAI_API_KEY=troque_esta_chave
CORS_ORIGINS=https://fabio.automaniaai.com.br
```

---

## Passo a Passo (Ubuntu)

1. Instalar Docker e Docker Compose Plugin
```
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

2. Clonar repositório
```
git clone https://github.com/lucasricardolebre1984/fabio2.git
cd fabio2
```

3. Preparar Nginx (baseado no nginx.conf existente)
```
mkdir -p nginx
cp nginx.conf nginx/nginx.conf
```

4. Criar `.env.prod` com as variáveis de produção
```
nano .env.prod
```

5. Subir stack completa
```
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

6. Verificar serviços
```
docker ps
curl http://localhost/health
```

---

## Checklist de Validação

- Frontend acessa `https://fabio.automaniaai.com.br`
- Backend responde em `/health`
- DB e Redis em execução
- Evolution API ativa em `/evolution/`
- VIVA operando e sem erros nos logs

---

## Etapa 2 - WhatsApp Funcional (Próxima)

Objetivo: ligar a integração no backend usando a instância já criada no container.

Checklist
- Garantir `EVOLUTION_API_URL=http://evolution-api:8080` no backend
- Garantir `EVOLUTION_API_KEY` igual ao configurado no Evolution
- Configurar webhook no Evolution Manager para `https://fabio.automaniaai.com.br/api/v1/webhook/evolution`
- Validar envio e recebimento de mensagens via `/whatsapp` e `/whatsapp/conversas`

---

## Etapa 3 - Protocolo Final de Produção

Objetivo: finalizar com DNS, SSL e hardening.

Checklist
- DNS apontando para o IP correto
- SSL via Lets Encrypt no Nginx
- Remover exposição direta das portas 8000 e 8080
- Revisar CORS e `NEXT_PUBLIC_API_URL`
- Garantir backups e política de logs

---

*Documento criado em: 2026-02-05*

---

## Status de Validade (2026-02-10)

- Este documento permanece como referencia de deploy futuro.
- Nesta sessao, **nao** deve ser usado como evidencia de ambiente ativo.
- Fonte de verdade operacional atual: ambiente local `c:\projetos\fabio2`.

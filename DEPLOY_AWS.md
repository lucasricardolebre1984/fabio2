# Deploy AWS EC2 - Guia Completo

## 🎯 Resumo

Deploy completo do sistema na AWS EC2 (Ubuntu).

---

## 📋 Pré-requisitos AWS

1. **EC2 Instance** (recomendado: t3.small ou superior)
   - Ubuntu 22.04 LTS
   - 2 vCPU, 2GB RAM (mínimo)
   - Portas liberadas: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API), 8080 (WhatsApp)

2. **Elastic IP** (fixo)

3. **Domínio** (opcional): api.seudominio.com

---

## 🚀 Passo a Passo Deploy

### 1. Conectar na EC2

```bash
# Gerar chave SSH (local)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/fabio2-aws

# Conectar (substitua pelo IP da sua EC2)
ssh -i ~/.ssh/fabio2-aws ubuntu@SEU_IP_EC2
```

### 2. Instalar Docker (na EC2)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo apt install docker-compose -y

# Verificar
docker --version
docker-compose --version
```

### 3. Clonar Repositório

```bash
cd ~
git clone https://github.com/lucasricardolebre1984/fabio2.git
cd fabio2
```

### 4. Configurar Variáveis de Ambiente

```bash
# Criar .env para produção
cat > .env << 'EOF'
ENVIRONMENT=production
DEBUG=false

# Banco (usando localhost pois está no mesmo servidor)
DATABASE_URL=postgresql+asyncpg://fabio2_prod:senha_forte_aqui@localhost:5432/fabio2_prod

# Redis
REDIS_URL=redis://localhost:6379/0

# Segurança (GERE UMA CHAVE FORTE!)
SECRET_KEY=sua_chave_secreta_aqui_minimo_32_caracteres

# CORS (seu domínio)
CORS_ORIGINS=https://www.automaniaai.com.br,http://localhost:3000

# WhatsApp
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=chave_segura_whatsapp

# Storage
STORAGE_MODE=local
STORAGE_LOCAL_PATH=./storage
EOF
```

### 5. Deploy com Docker Compose

```bash
# Subir tudo (PostgreSQL, Redis, Backend, Frontend, Evolution)
docker-compose up -d --build

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 6. Configurar Nginx (Reverse Proxy)

```bash
# Instalar nginx
sudo apt install nginx -y

# Configurar site
sudo tee /etc/nginx/sites-available/fabio2 << 'EOF'
server {
    listen 80;
    server_name SEU_IP_EC2;

    # Frontend (Next.js exportado)
    location / {
        root /home/ubuntu/fabio2/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Evolution API (WhatsApp)
    location /whatsapp/ {
        proxy_pass http://localhost:8080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Ativar config
sudo ln -s /etc/nginx/sites-available/fabio2 /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Criar Usuário Admin

```bash
# Entrar no container do backend
docker-compose exec backend bash

# Abrir Python
python
```

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        user = User(
            email="fabio@fcsolucoes.com",
            hashed_password=get_password_hash("senha_segura_aqui"),
            nome="Fábio",
            role="admin",
            ativo=True
        )
        db.add(user)
        await db.commit()
        print("✅ Admin criado!")

asyncio.run(create_admin())
exit()
```

### 8. SSL (HTTPS) - Opcional mas recomendado

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx -y

# Gerar certificado (substitua pelo seu domínio)
sudo certbot --nginx -d api.seudominio.com
```

---

## 📁 Estrutura na EC2

```
/home/ubuntu/fabio2/
├── docker-compose.yml      # Config produção
├── backend/                # Código backend
├── frontend/               # Código frontend
├── contratos/              # Templates
├── storage/                # PDFs gerados
└── .env                    # Variáveis de ambiente
```

---

## 🔄 Comandos Úteis

```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f
docker-compose logs -f backend

# Reiniciar
docker-compose restart

# Atualizar (após git pull)
docker-compose down
docker-compose up -d --build

# Backup banco
docker-compose exec postgres pg_dump -U fabio2_prod fabio2_prod > backup.sql

# Acessar banco
docker-compose exec postgres psql -U fabio2_prod -d fabio2_prod
```

---

## 🔗 URLs Após Deploy

| Serviço | URL |
|---------|-----|
| Frontend | http://SEU_IP_EC2 |
| API Docs | http://SEU_IP_EC2/api/docs |
| Evolution API | http://SEU_IP_EC2:8080 |

---

## 💰 Custo Estimado AWS

| Recurso | Custo/mês |
|---------|-----------|
| EC2 t3.small | ~$15-20 |
| Elastic IP | Grátis (se em uso) |
| Transferência | ~$5-10 |
| **Total** | **~$20-30/mês** |

---

## ⚠️ Checklist Segurança

- [ ] Trocar todas as senhas padrão
- [ ] Configurar Security Group (firewall AWS)
- [ ] Habilitar UFW (firewall Ubuntu)
- [ ] Configurar SSL/HTTPS
- [ ] Desativar DEBUG mode
- [ ] Criar backup automático do banco

---

## 🆘 Troubleshooting

### Problema: Porta 8000 não acessível
```bash
# Verificar Security Group AWS (liberar porta 8000)
# Verificar UFW
sudo ufw allow 8000
```

### Problema: Permissão negada no Docker
```bash
sudo usermod -aG docker ubuntu
# Fazer logout e login novamente
```

### Problema: Banco não conecta
```bash
# Verificar se PostgreSQL está rodando
docker-compose logs postgres

# Resetar banco (CUIDADO - apaga dados!)
docker-compose down -v
docker-compose up -d
```

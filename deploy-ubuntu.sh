#!/bin/bash
# DEPLOY FABIO2 - Servidor Ubuntu
# Script a ser executado NO SERVIDOR UBUNTU
# Data: 2026-02-03

set -e  # Para em caso de erro

echo "🚀 INICIANDO DEPLOY FABIO2 - Ubuntu Server"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# 1. VERIFICAÇÕES INICIAIS
# ============================================
echo -e "${YELLOW}[1/8] Verificando pré-requisitos...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git não instalado${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não encontrado. Instalando...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose não encontrado. Instalando...${NC}"
    sudo apt update
    sudo apt install docker-compose -y
fi

echo -e "${GREEN}✅ Pré-requisitos OK${NC}"

# ============================================
# 2. BACKUP (se existe instalação anterior)
# ============================================
echo -e "${YELLOW}[2/8] Verificando instalação anterior...${NC}"

if [ -d "~/fabio2" ]; then
    echo -e "${YELLOW}📦 Backup da instalação anterior...${NC}"
    sudo mv ~/fabio2 ~/fabio2.backup.$(date +%Y%m%d_%H%M%S)
fi

echo -e "${GREEN}✅ Backup OK${NC}"

# ============================================
# 3. CLONAR REPOSITÓRIO
# ============================================
echo -e "${YELLOW}[3/8] Clonando repositório...${NC}"

cd ~
git clone https://github.com/lucasricardolebre1984/fabio2.git
cd fabio2

echo -e "${GREEN}✅ Repositório clonado${NC}"

# ============================================
# 4. CONFIGURAR VARIÁVEIS DE AMBIENTE
# ============================================
echo -e "${YELLOW}[4/8] Configurando variáveis de ambiente...${NC}"

# Verificar se já existe .env
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# ============================================
# FABIO2 - PRODUÇÃO
# ============================================

# Ambiente
ENVIRONMENT=production
DEBUG=false

# Banco PostgreSQL
POSTGRES_USER=fabio2_prod
POSTGRES_PASSWORD=CHANGE_THIS_STRONG_PASSWORD
POSTGRES_DB=fabio2_prod
DATABASE_URL=postgresql+asyncpg://fabio2_prod:CHANGE_THIS_STRONG_PASSWORD@postgres:5432/fabio2_prod

# Redis
REDIS_URL=redis://redis:6379/0

# Segurança (ALTERE PARA UMA CHAVE FORTE!)
SECRET_KEY=CHANGE_THIS_TO_32_CHAR_SECRET_KEY

# CORS (domínios permitidos)
CORS_ORIGINS=https://seudominio.com,http://localhost:3000

# WhatsApp Evolution API
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=CHANGE_THIS_API_KEY
EVOLUTION_DATABASE_ENABLED=true

# Storage
STORAGE_MODE=local
STORAGE_LOCAL_PATH=/app/storage

# PGAdmin (opcional)
PGADMIN_DEFAULT_EMAIL=admin@seudominio.com
PGADMIN_DEFAULT_PASSWORD=CHANGE_THIS_PGADMIN_PASS
EOF
    
    echo -e "${YELLOW}⚠️  ARQUIVO .env CRIADO!${NC}"
    echo -e "${YELLOW}⚠️  EDITE O ARQUIVO .env E ALTERE AS SENHAS ANTES DE CONTINUAR!${NC}"
    echo ""
    read -p "Pressione ENTER após editar o .env..."
fi

echo -e "${GREEN}✅ Variáveis configuradas${NC}"

# ============================================
# 5. CRIAR BANCO EVOLUTION (se não existe)
# ============================================
echo -e "${YELLOW}[5/8] Preparando bancos de dados...${NC}"

# Subir só o postgres temporariamente para criar banco
docker-compose up -d postgres
sleep 5

# Criar banco evolution
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-fabio2_prod} -d postgres -c "CREATE DATABASE evolution;" 2>/dev/null || echo "Banco evolution já existe"

echo -e "${GREEN}✅ Bancos preparados${NC}"

# ============================================
# 6. BUILD E DEPLOY
# ============================================
echo -e "${YELLOW}[6/8] Buildando e subindo containers...${NC}"

# Subir tudo
docker-compose down 2>/dev/null || true
docker-compose up -d --build

echo -e "${GREEN}✅ Containers em execução${NC}"

# ============================================
# 7. VERIFICAÇÃO
# ============================================
echo -e "${YELLOW}[7/8] Verificando serviços...${NC}"

sleep 10  # Aguardar inicialização

# Verificar PostgreSQL
if docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-fabio2_prod} > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL OK${NC}"
else
    echo -e "${RED}❌ PostgreSQL falhou${NC}"
fi

# Verificar Evolution API
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Evolution API OK${NC}"
else
    echo -e "${RED}❌ Evolution API falhou${NC}"
fi

# Verificar Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend OK${NC}"
else
    echo -e "${RED}❌ Backend falhou${NC}"
fi

echo -e "${GREEN}✅ Verificação concluída${NC}"

# ============================================
# 8. INFORMAÇÕES FINAIS
# ============================================
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO!${NC}"
echo "=========================================="
echo ""
echo "Serviços disponíveis:"
echo "  • Frontend:    http://SEU_IP:3000"
echo "  • Backend:     http://SEU_IP:8000"
echo "  • API Docs:    http://SEU_IP:8000/docs"
echo "  • Evolution:   http://SEU_IP:8080"
echo "  • PGAdmin:     http://SEU_IP:5050"
echo ""
echo "Próximos passos:"
echo "  1. Configure o proxy reverso (nginx)"
echo "  2. Configure SSL (Let's Encrypt)"
echo "  3. Conecte o WhatsApp na Evolution API"
echo ""
echo "Comandos úteis:"
echo "  docker-compose logs -f     # Ver logs"
echo "  docker-compose ps          # Status containers"
echo "  docker-compose down        # Parar tudo"
echo "  docker-compose up -d       # Iniciar tudo"
echo ""

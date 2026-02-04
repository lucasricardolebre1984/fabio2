# SESSION - Contexto Atual da Sessão

> **Sessão Ativa:** 2026-02-03  
> **Status:** ✅ AWS BACKEND ONLINE | Aguardando KingHost Frontend  
> **Branch:** main  
> **Último Commit:** 1e38720 - config: prepara para deploy hibrido

---

## 🎯 ESTADO ATUAL DO SISTEMA

### Ambiente de Desenvolvimento (Windows Local)
| Componente | Status | URL |
|------------|--------|-----|
| Frontend | ✅ Rodando | http://localhost:3000 |
| Backend | ✅ Rodando | http://localhost:8000 |
| PostgreSQL | ✅ Docker | localhost:5432 |
| Redis | ✅ Docker | localhost:6379 |

### Ambiente de Produção (AWS + KingHost)
| Componente | Status | URL |
|------------|--------|-----|
| Backend API | ✅ **ONLINE** | http://56.124.101.16:8000 |
| PostgreSQL | ✅ Container | 56.124.101.16:5432 |
| Redis | ✅ Container | 56.124.101.16:6379 |
| Evolution API | ✅ **ONLINE** | http://56.124.101.16:8080 |
| Frontend | ⏳ Pendente (KingHost) | https://fabio.automaniaai.com.br |

**✅ Backend AWS 100% funcional!** Testado em 2026-02-03 23:20

---

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### Contratos
- [x] Template Bacen completo (11 cláusulas)
- [x] Layout institucional com faixa azul
- [x] Fonte Times New Roman
- [x] Cálculo automático de valores por extenso
- [x] Geração de PDF via browser print
- [x] Visualização de contratos
- [x] Edição de contratos
- [x] Exclusão de contratos
- [x] Listagem com busca

### Autenticação
- [x] Login JWT funcionando
- [x] Usuário: fabio@fcsolucoes.com / 1234
- [x] Workaround security_stub para dev

### Integrações
- [x] Evolution API configurada (AWS)
- [x] WhatsApp pronto para uso

---

## 🏗️ ARQUITETURA DE DEPLOY

### AWS EC2 (Backend + Banco)
```
Servidor: 56.124.101.16
├── fabio2-backend (porta 8000)
├── fabio2-postgres (porta 5432)
├── fabio2-redis (porta 6379)
├── fabio2-evolution (porta 8080)
└── fabio2-pgadmin (porta 5050)
```

### KingHost (Frontend)
```
Domínio: fabio.automaniaai.com.br
Pasta: /www/fabio
├── index.html (Next.js export)
├── _next/ (assets)
└── static/ (imagens)
```

### Comunicação
```
Usuário → fabio.automaniaai.com.br (KingHost/Cloudflare)
       → HTML/JS/CSS carregado
       → Chamadas API para 56.124.101.16:8000
```

---

## 🔧 CONFIGURAÇÕES ATIVAS

### Frontend (next.config.js)
```javascript
{
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: 'http://56.124.101.16:8000/api/v1'
  }
}
```

### Backend (CORS)
```python
CORS_ORIGINS = [
    "http://56.124.101.16",
    "https://fabio.automaniaai.com.br",
    "http://localhost:3000"
]
```

---

## 📋 CHECKLIST DEPLOY PRODUÇÃO

### Fase 1: AWS Backend (✅ CONCLUÍDO)
- [x] Instalar Docker no Ubuntu
- [x] Clonar repositório
- [x] Configurar .env
- [x] Subir containers
- [x] **REINICIAR containers** (feito em 2026-02-03)
- [x] **Adicionar validate-docbr ao requirements**
- [x] Testar API
- [x] Liberar portas no Security Group

### Fase 2: KingHost Frontend (⏳ EM ANDAMENTO)
- [ ] Gerar build do Next.js
- [ ] Subir arquivos via FTP para /www/fabio
- [ ] Configurar DNS fabio.automaniaai.com.br
- [ ] Testar acesso
- [ ] Validar comunicação com API

### Fase 3: Validação (⏳ PENDENTE)
- [ ] Login funcionando
- [ ] Criar contrato
- [ ] Visualizar contrato
- [ ] Gerar PDF
- [ ] WhatsApp integrado

---

## 🐛 WORKAROUNDS ATIVOS

| Workaround | Motivo | Arquivo |
|------------|--------|---------|
| security_stub.py | Bcrypt 72 bytes no Windows | backend/app/core/security_stub.py |
| PDF via browser | WeasyPrint precisa GTK+ | frontend/src/lib/pdf.ts |

---

## ⚠️ AÇÃO NECESSÁRIA - AWS ACCESS

### Problema
O servidor AWS (56.124.101.16) não está respondendo nas portas 8000/8080.
Containers Docker provavelmente pararam após falta de acesso SSH.

### Solução
Precisamos acessar o servidor via SSH para reiniciar os containers:

```bash
# Comando para reiniciar (executar no servidor)
cd ~/fabio2
sudo docker-compose -f docker-compose-prod.yml down
sudo docker-compose -f docker-compose-prod.yml up -d

# Verificar status
sudo docker-compose -f docker-compose-prod.yml ps
```

### Pré-requisito
- Arquivo da chave SSH: `fabio-aws.pem` ou similar
- Comando: `ssh -i ~/fabio-aws.pem ubuntu@56.124.101.16`

---

## 📝 PRÓXIMOS PASSOS IMEDIATOS

1. **Gerar build do frontend**
   ```powershell
   cd frontend
   npm run build
   ```

2. **Subir no KingHost via FTP**
   - Host: webftp.kinghost.com.br
   - Pasta: /www/fabio
   - Arquivos: .next/standalone ou export estático

3. **Testar produção**
   - Acessar https://fabio.automaniaai.com.br
   - Validar login
   - Criar contrato de teste

---

## 🔗 LINKS IMPORTANTES

| Recurso | URL |
|---------|-----|
| Repositório | https://github.com/lucasricardolebre1984/fabio2 |
| API AWS | http://56.124.101.16:8000/docs |
| KingHost FTP | webftp.kinghost.com.br |
| Produção | https://fabio.automaniaai.com.br |

---

## 💾 COMANDOS ÚTEIS

### AWS (Servidor)
```bash
# Ver containers rodando
docker-compose -f docker-compose-prod.yml ps

# Ver logs
docker-compose -f docker-compose-prod.yml logs -f

# Restart
docker-compose -f docker-compose-prod.yml restart
```

### Windows (Local)
```powershell
# Iniciar backend
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload

# Iniciar frontend (novo terminal)
cd frontend
npm run dev
```

---

*Atualizado em: 2026-02-03 23:00*  
*Autor: DEV DEUS*  
*Status: 🟡 Deploy em andamento*

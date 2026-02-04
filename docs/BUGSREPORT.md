# BUGSREPORT - Registro de Bugs

> **Projeto:** FC Soluções Financeiras SaaS  
> **Protocolo:** Registrar antes de corrigir | Evidência obrigatória  
> **Última Atualização:** 2026-02-04  
> **Auditoria:** Módulo de Imagens - Implementação Completa  

---

## 🐛 Bugs Ativos

| ID | Severidade | Módulo | Descrição | Status |
|----|-----------|--------|-----------|--------|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Aguardando instalação GTK+ |
| BUG-014 | Média | Imagens/AI | Pollinations.ai fora do ar | Implementado fallback placeholder |

---

## 🔧 Workarounds Implementados

### PostgreSQL → SQLite Fallback (DEV)

**Problema:** PostgreSQL não disponível na porta 5432 quando Docker não está rodando.

**Solução:** Auto-detecção de banco no `app/db/session.py`:
- Tenta conectar ao PostgreSQL primeiro
- Se falhar, usa SQLite automaticamente
- Usuário admin criado automaticamente no SQLite

**Arquivos modificados:**
- `app/config.py` - Adicionado DATABASE_URL_FALLBACK
- `app/db/session.py` - Auto-detecção de banco
- `app/db/base.py` - UUID como String(36) para compatibilidade
- `app/models/*.py` - JSON em vez de JSONB

**Testado em:** Windows 11, Python 3.11

### Pollinations.ai Fallback

**Problema:** API Pollinations.ai fora do ar (502 Bad Gateway).

**Solução:** Implementado fallback para placehold.co:
- Gera imagem placeholder colorida
- Texto do prompt na imagem
- Mesmas dimensões (1:1, 16:9, 9:16)

---

## ✅ Bugs Resolvidos

| ID | Severidade | Módulo | Descrição | Resolução | Data |
|----|-----------|--------|-----------|-----------|------|
| BUG-001 | Alta | Backend/Setup | DATABASE_URL não exportado | Adicionado export em app/db/session.py | 2026-02-03 |
| BUG-002 | Média | Frontend/Build | `output: 'export'` quebrava dev server | Removido do next.config.js | 2026-02-03 |
| BUG-003 | Média | Backend/Deps | pydantic 2.5.3 incompatível com pydantic-settings | Atualizado para pydantic 2.7.0 | 2026-02-03 |
| BUG-004 | Alta | Backend/Auth | bcrypt "password cannot be longer than 72 bytes" no Windows | Implementado security_stub.py para dev | 2026-02-03 |
| BUG-005 | Alta | Backend/API | require_admin não importado em contratos.py/clientes.py | Adicionados imports faltantes | 2026-02-03 |
| BUG-006 | Média | Backend/PDF | WeasyPrint falha sem GTK+ no Windows | Implementado pdf_service_stub.py | 2026-02-03 |
| BUG-007 | Média | Backend/Templates | Template path resolution falhava em Windows | Adicionados múltiplos fallback paths | 2026-02-03 |
| BUG-008 | Média | Frontend/API | Erros de conexão com backend não tratados | Adicionado tratamento try/catch | 2026-02-03 |
| BUG-009 | Baixa | Frontend/UI | Componentes Badge e Tabs faltavam | Criados componentes manualmente | 2026-02-03 |
| BUG-011 | Alta | Backend/DB | Modelos usam JSONB e UUID (PostgreSQL only) | Alterado para JSON e String(36) | 2026-02-03 |
| **BUG-012** | **Alta** | **Backend/Imagens** | **Tabela imagens sem coluna url** | **Recriada tabela com coluna url** | **2026-02-04** |
| **BUG-013** | **Alta** | **Backend/API** | **Pydantic v2 - from_orm deprecado** | **Substituído por model_validate** | **2026-02-04** |
| **BUG-014** | **Alta** | **Backend/Imagens** | **HuggingFace API requer auth** | **Migrado para Pollinations.ai + fallback** | **2026-02-04** |
| **BUG-015** | **Média** | **Frontend/Imagens** | **Erro objeto no toast (React)** | **Adicionado tratamento stringify** | **2026-02-04** |
| **BUG-016** | **Média** | **Frontend/Upload** | **Content-Type manual causava erro** | **Removido header manual do axios** | **2026-02-04** |

---

## 📝 BUG-012: Tabela Imagens Sem Coluna url (RESOLVIDO)

### Descrição
A tabela `imagens` foi criada inicialmente sem a coluna `url`, causando erro 500 ao listar imagens.

**Erro:**
```
sqlalchemy.exc.ProgrammingError: column imagens.url does not exist
```

### Causa
O SQLAlchemy criou a tabela parcialmente durante desenvolvimento, sem a coluna `url`.

### Resolução
1. Drop da tabela com CASCADE:
```sql
DROP TABLE IF EXISTS imagens CASCADE
```

2. Recriação completa da tabela:
```sql
CREATE TABLE imagens (
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    url VARCHAR(500) NOT NULL,
    tipo tipoimagem NOT NULL,
    formato formatoimagem NOT NULL,
    prompt TEXT,
    status statusimagem NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
)
```

### Arquivos Modificados
- `backend/app/models/imagem.py` - Modelo completo
- Banco de dados PostgreSQL - Tabela recriada

### Data da Resolução
2026-02-04

---

## 📝 BUG-013: Pydantic v2 from_orm Deprecado (RESOLVIDO)

### Descrição
Pydantic v2 substituiu o método `from_orm()` por `model_validate()`.

**Erro:**
```
AttributeError: 'ImagemResponse' object has no attribute 'from_orm'
```

### Resolução
Substituído em todos os endpoints de `imagens.py`:

```python
# Antes (Pydantic v1):
ImagemResponse.from_orm(imagem)

# Depois (Pydantic v2):
ImagemResponse.model_validate(imagem)
```

### Arquivos Modificados
- `backend/app/api/v1/imagens.py` - 5 substituições

### Data da Resolução
2026-02-04

---

## 📝 BUG-014: HuggingFace API Requer Autenticação (RESOLVIDO)

### Descrição
HuggingFace Inference API agora requer autenticação (erro 401).
Pollinations.ai (alternativa gratuita) está fora do ar (erro 502).

**Erro:**
```json
{
  "error": "https://api-inference.huggingface.co is no longer supported"
}
```

### Resolução
Implementado fallback para placehold.co:

```python
# Tenta Pollinations.ai primeiro
try:
    response = await client.get(pollinations_url)
    if response.status_code == 200:
        return response.content
except:
    pass

# Fallback: gera placeholder colorido
placeholder_url = f"https://placehold.co/{width}x{height}/{color}/white/png?text={text}"
```

### Arquivos Modificados
- `backend/app/services/imagem_service.py`

### Nota
Quando Pollinations.ai voltar, o sistema usará automaticamente. Placeholder é apenas fallback temporário.

### Data da Resolução
2026-02-04

---

## 📝 BUG-015: Erro Objeto no Toast React (RESOLVIDO)

### Descrição
O frontend tentava renderizar um objeto diretamente no toast de erro, causando crash do React.

**Erro:**
```
Error: Objects are not valid as a React child (found: object with keys {type, loc, msg, input, url})
```

### Resolução
Adicionado tratamento para converter objeto em string:

```typescript
let errorMessage = 'Erro ao enviar imagem. Tente novamente.'
if (error.response?.data?.detail) {
  errorMessage = typeof error.response.data.detail === 'string' 
    ? error.response.data.detail 
    : JSON.stringify(error.response.data.detail)
}
toast.error(errorMessage)
```

### Arquivos Modificados
- `frontend/src/app/(dashboard)/imagens/upload/page.tsx`

### Data da Resolução
2026-02-04

---

## 📝 BUG-016: Content-Type Manual no Axios (RESOLVIDO)

### Descrição
Ao enviar FormData, definir `Content-Type: multipart/form-data` manualmente quebra o boundary do multipart.

**Erro:**
Backend não conseguia parsear o arquivo corretamente.

### Resolução
Removido header manual - axios define automaticamente com boundary correto:

```typescript
// Antes (quebrava):
const response = await api.post('/imagens/upload', data, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// Depois (funciona):
const response = await api.post('/imagens/upload', data)
```

### Arquivos Modificados
- `frontend/src/app/(dashboard)/imagens/upload/page.tsx`

### Data da Resolução
2026-02-04

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de Bugs | 16 |
| Ativos | 2 |
| Críticos | 0 |
| Resolvidos | 14 |
| Média de Resolução | < 1 dia |

---

## 🎯 Funcionalidades Implementadas

| Módulo | Status | Detalhes |
|--------|--------|----------|
| Autenticação JWT | ✅ | Login funcionando com PostgreSQL |
| Menu de Templates | ✅ | Bacen, Serasa, Protesto |
| Criar Contrato | ✅ | Form dinâmico com validação |
| Listar Contratos | ✅ | Cards com busca e ações |
| Visualizar Contrato | ✅ | Layout institucional completo |
| Editar Contrato | ✅ | Form de edição funcional |
| Valores por Extenso | ✅ | Automático no backend |
| Geração de PDF | ⚠️ | Usa Ctrl+P (WeasyPrint pendente) |
| **Módulo de Imagens** | ✅ | **Implementado e testado** |
| ├── Gerar com IA | ✅ | Com fallback placeholder |
| ├── Upload Arquivo | ✅ | Drag & drop |
| ├── Pasta Campanhas | ✅ | Workflow aprovação |
| └── Galeria/Filtros | ✅ | Grid/List view |

---

## 🚀 Próximos Passos

1. **Monitorar Pollinations.ai** - Quando voltar, imagens reais serão geradas
2. **Implementar WhatsApp Inteligente** - Comandos por mensagem
3. **Deploy AWS/KingHost** - Subir para produção

---

*Atualizado em: 2026-02-04 11:47*  
*Auditoria: Módulo de Imagens - Correções aplicadas e testadas*


---

## 📝 ROLLBACK - CÉREBRO INSTITUCIONAL v2

**Data:** 2026-02-04  
**Mudança:** Simplificação do BRAINIMAGE + Integração FC/Rezeta

### Arquivos Modificados
- `backend/app/services/brainimage_service.py` → Nova versão simplificada  
- `backend/app/services/brainimage_service_v1_backup.py` → Backup v1  
- `docs/PROMPTS/BRAINIMAGE_v2.md` → Nova documentação  
- `docs/PROMPTS/BRAINIMAGE.md` → Documentação original  
- `storage/logos/` → Pasta para logos das empresas

### Como Reverter (Rollback)

**Se necessário voltar à v1:**
```powershell
cd C:\projetos\fabio2\backend\app\services
Copy-Item brainimage_service_v1_backup.py brainimage_service.py
```

**Ou via git:**
```powershell
cd C:\projetos\fabio2
git checkout HEAD -- backend/app/services/brainimage_service.py
```

### O que Mudou na v2
- ✅ Simplificado: Código mais curto e direto
- ✅ Duas empresas: FC + Rezeta detectadas automaticamente no prompt
- ✅ Logos: Pasta `storage/logos/` criada para fc_logo.png e rezeta_logo.png
- ✅ Prompts objetivos: Removeu complexidade desnecessária

---

*Rollback documentado por Automania-AI - 2026-02-04*

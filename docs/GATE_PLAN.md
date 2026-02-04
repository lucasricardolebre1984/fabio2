# GATE PLAN - Implementação Módulo de Imagens

> **Projeto:** FC Soluções Financeiras SaaS  
> **Feature:** Módulo de Imagens com HuggingFace + CÉREBRO INSTITUCIONAL  
> **Data:** 2026-02-04  
> **Status:** AGUARDANDO APROVAÇÃO PARA GATE 1  

---

## 🎯 OBJETIVO

Implementar módulo completo de geração e gestão de imagens usando:
- **HuggingFace Inference API** (gratuito - 1k req/mês)
- **CÉREBRO INSTITUCIONAL** (docs/PROMPTS/BRAINIMAGE.md)
- **Pasta Campanhas** (organização automática)

---

## 📋 GATES ESTRUTURADOS

---

## 🔷 GATE 0: Documentação Auditoria ✅

**Status:** CONCLUÍDO  
**Tempo:** 15 minutos

### Entregáveis
- [x] docs/PROJECT_CONTEXT.md
- [x] docs/GATE_PLAN.md (este arquivo)
- [ ] docs/SESSION.md (atualizar ao final)

### Checklist
- [x] Contexto do projeto documentado
- [x] Arquitetura atual mapeada
- [x] Estrutura de diretórios definida
- [x] Rollback estruturado documentado

---

## 🔷 GATE 1: Backend - API HuggingFace + Model Imagem

**Status:** AGUARDANDO APROVAÇÃO  
**Tempo Estimado:** 1.5 horas  
**Risco:** Médio (integração externa)

### Arquivos Criados/Modificados

#### 1.1 Model (backend/app/models/imagem.py)
```python
# SQLAlchemy model para tabela 'imagens'
- id: UUID (PK)
- nome: str
- descricao: str (opcional)
- url: str (caminho arquivo)
- tipo: enum (gerada/upload)
- formato: enum (1:1, 16:9, 9:16)
- prompt: str (se gerada por IA)
- status: enum (rascunho/aprovada)
- created_at: datetime
- updated_at: datetime
```

#### 1.2 Schema (backend/app/schemas/imagem.py)
```python
# Pydantic schemas
- ImagemCreate
- ImagemUpdate
- ImagemResponse
```

#### 1.3 Service (backend/app/services/imagem_service.py)
```python
# HuggingFace Integration
class ImagemService:
    - HuggingFace_API_URL = "https://api-inference.huggingface.co/models/"
    - DEFAULT_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    
    async def gerar_imagem(prompt: str, formato: str) -> bytes
    async def salvar_upload(file: UploadFile) -> str
    async def mover_para_campanhas(imagem_id: UUID) -> str
    - Métodos auxiliares de formatação de prompt
```

#### 1.4 Router (backend/app/api/v1/imagens.py)
```python
# Endpoints REST
GET    /imagens              # Listar imagens
POST   /imagens/gerar        # Gerar imagem HuggingFace
POST   /imagens/upload       # Upload arquivo
POST   /imagens/{id}/aprovar # Mover para campanhas/
DELETE /imagens/{id}         # Remover imagem
```

#### 1.5 Router Principal (backend/app/api/router.py)
```python
# Adicionar linha:
from app.api.v1 import imagens
api_router.include_router(imagens.router, prefix="/imagens", tags=["Imagens"])
```

#### 1.6 Pastas de Storage
```bash
mkdir -p storage/imagens
mkdir -p storage/campanhas
```

### Dependências
```bash
# requirements.txt (adicionar se não existir)
aiofiles>=23.0.0
httpx>=0.25.0
python-multipart>=0.0.6
```

### Critérios de Aceite GATE 1
- [ ] `GET /api/v1/imagens` retorna lista vazia (200)
- [ ] `POST /api/v1/imagens/gerar` gera imagem (prompt teste)
- [ ] `POST /api/v1/imagens/upload` salva arquivo
- [ ] Arquivos aparecem em storage/imagens/
- [ ] Sem erros no console do backend

### Rollback GATE 1
```bash
git checkout backend/app/api/router.py
Remove-Item backend/app/api/v1/imagens.py -Force
Remove-Item backend/app/models/imagem.py -Force
Remove-Item backend/app/schemas/imagem.py -Force
Remove-Item backend/app/services/imagem_service.py -Force
```

---

## 🔷 GATE 2: Frontend - Botão Menu + Página Imagens

**Status:** PENDENTE  
**Tempo Estimado:** 1 hora  
**Risco:** Baixo (UI apenas)

### Arquivos Modificados/Criados

#### 2.1 Sidebar (frontend/src/components/layout/Sidebar.tsx)
```typescript
// Adicionar no menuItems:
{ href: '/imagens', label: 'Imagens', icon: ImageIcon }

// Importar:
import { Image as ImageIcon } from 'lucide-react'
```

#### 2.2 Página Imagens (frontend/src/app/(dashboard)/imagens/page.tsx)
```typescript
// Nova página completa
- Grid de imagens (visualização em cards)
- Botão "Gerar Nova Imagem" (abre modal)
- Botão "Upload" (abre file picker)
- Filtros: Todas / Geradas / Uploads / Campanhas
- Preview de imagens
```

### Critérios de Aceite GATE 2
- [ ] Botão "Imagens" aparece no menu lateral
- [ ] Clicar navega para /imagens
- [ ] Página carrega sem erros
- [ ] Layout grid visualmente correto
- [ ] Botões "Gerar" e "Upload" visíveis

### Rollback GATE 2
```bash
git checkout frontend/src/components/layout/Sidebar.tsx
Remove-Item frontend/src/app/(dashboard)/imagens -Recurse -Force
```

---

## 🔷 GATE 3: Frontend - Modal Gerador + Integração

**Status:** PENDENTE  
**Tempo Estimado:** 1.5 horas  
**Risco:** Médio (integração API)

### Arquivos Criados

#### 3.1 Modal Gerador (frontend/src/components/imagens/GeradorImagemModal.tsx)
```typescript
// Modal completo
- Tabs: "Criar do Zero" / "Editar Imagem"
- Campo de prompt (textarea)
- Seletor de formato (1:1, 16:9, 9:16)
- Botão "Gerar com IA" (chama API)
- Preview da imagem gerada
- Botão "Salvar" / "Descartar"
- Botão "Aprovar para Campanha"
```

#### 3.2 Integração API (frontend/src/lib/api.ts - adicionar)
```typescript
// Métodos para imagens
- getImagens(): Promise<Imagem[]>
- gerarImagem(prompt, formato): Promise<Imagem>
- uploadImagem(file): Promise<Imagem>
- aprovarImagem(id): Promise<void>
- deletarImagem(id): Promise<void>
```

### Critérios de Aceite GATE 3
- [ ] Modal abre ao clicar "Gerar Nova Imagem"
- [ ] Prompt é enviado para backend
- [ ] Imagem é gerada e exibida no preview
- [ ] Imagem aparece na lista após salvar
- [ ] Upload de arquivo funciona
- [ ] Erros são tratados (toast)

### Rollback GATE 3
```bash
Remove-Item frontend/src/components/imagens/GeradorImagemModal.tsx -Force
```

---

## 🔷 GATE 4: Pasta Campanhas + Workflow Aprovação

**Status:** PENDENTE  
**Tempo Estimado:** 45 minutos  
**Risco:** Baixo (lógica de arquivos)

### Funcionalidades

#### 4.1 Workflow Aprovação
```
1. Usuário gera/upload imagem → storage/imagens/
2. Usuário clica "Aprovar para Campanha"
3. Backend move arquivo → storage/campanhas/
4. Renomeia: {YYYYMMDD}_{nome_original}.{ext}
5. Atualiza status no banco: 'aprovada'
```

#### 4.2 Backend (imagem_service.py)
```python
async def aprovar_para_campanha(imagem_id: UUID):
    # 1. Buscar imagem no banco
    # 2. Mover arquivo de imagens/ para campanhas/
    # 3. Renomear com data
    # 4. Atualizar caminho no banco
    # 5. Atualizar status para 'aprovada'
```

### Critérios de Aceite GATE 4
- [ ] Botão "Aprovar para Campanha" funciona
- [ ] Arquivo é movido para storage/campanhas/
- [ ] Nome inclui data (YYYYMMDD)
- [ ] Status atualizado no banco
- [ ] Filtro "Campanhas" mostra apenas aprovadas

### Rollback GATE 4
```bash
# Reverter código do service
# Limpar pastas campanhas/ se necessário
```

---

## 🔷 GATE 5: Testes + Documentação + Commit

**Status:** PENDENTE  
**Tempo Estimado:** 1 hora  
**Risco:** Baixo (validação)

### Testes Obrigatórios

#### Teste 1: Geração HuggingFace
```bash
curl -X POST http://localhost:8000/api/v1/imagens/gerar \
  -H "Content-Type: application/json" \
  -d '{"prompt": "professional business flyer, finance services", "formato": "1:1"}'
```
**Esperado:** Retorna imagem PNG válida

#### Teste 2: Upload Arquivo
```bash
curl -X POST http://localhost:8000/api/v1/imagens/upload \
  -F "file=@teste.jpg"
```
**Esperado:** Arquivo salvo em storage/imagens/

#### Teste 3: Aprovação
```bash
curl -X POST http://localhost:8000/api/v1/imagens/{id}/aprovar
```
**Esperado:** Arquivo movido para storage/campanhas/YYYYMMDD_nome.jpg

### Documentação

#### Atualizar docs/MANUAL_DO_CLIENTE.md
```markdown
## Módulo de Imagens

### Gerar Imagem com IA
1. Clique em "Imagens" no menu
2. Clique "Gerar Nova Imagem"
3. Digite o prompt desejado
4. Escolha o formato (1:1, 16:9, 9:16)
5. Clique "Gerar"
6. Aguarde a geração (~5-10 segundos)
7. Clique "Salvar" ou "Aprovar para Campanha"

### Upload de Imagem
1. Clique "Upload"
2. Selecione o arquivo
3. Clique "Salvar"

### Pasta Campanhas
Imagens aprovadas são movidas automaticamente para a pasta campanhas/
com nome formatado: {data}_{nome_imagem}.{extensao}
```

### Commit
```bash
git add .
git commit -m "feat: implementa módulo de imagens com HuggingFace + CÉREBRO INSTITUCIONAL

- Adiciona API /imagens com HuggingFace Inference
- Implementa gerador TXT→IMG e IMG→IMG
- Cria pasta campanhas/ para imagens aprovadas
- Adiciona botão Imagens no menu lateral
- Integra CÉREBRO INSTITUCIONAL (BRAINIMAGE.md)
- Documenta uso no MANUAL_DO_CLIENTE.md

Closes: GATE 1-5 completo
Auditoria: 2026-02-04"
```

### Critérios de Aceite GATE 5
- [ ] Todos os testes passam
- [ ] MANUAL_DO_CLIENTE.md atualizado
- [ ] SESSION.md atualizado
- [ ] Commit realizado
- [ ] Push para origin/main

---

## 📊 RESUMO EXECUTIVO

| GATE | Descrição | Tempo | Risco | Status |
|------|-----------|-------|-------|--------|
| 0 | Documentação | 15min | Baixo | ✅ Concluído |
| 1 | Backend API | 1.5h | Médio | ⏳ Aguardando |
| 2 | Frontend Menu | 1h | Baixo | ⏳ Pendente |
| 3 | Modal Gerador | 1.5h | Médio | ⏳ Pendente |
| 4 | Campanhas | 45min | Baixo | ⏳ Pendente |
| 5 | Testes + Commit | 1h | Baixo | ⏳ Pendente |

**Tempo Total Estimado:** ~6 horas

---

## 🚦 PRÓXIMA AÇÃO

**Para iniciar GATE 1, diga:**
- "APROVADO GATE 1" → Inicia implementação backend
- "APROVADO TUDO" → Executa todos os gates sequencialmente

---

*Plano criado para auditoria institucional*  
*Protocolo GODMOD ativado*  
*Rollback estruturado em cada gate*

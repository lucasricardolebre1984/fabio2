# 🎯 PLANO DE EXECUÇÃO EM GATES - Finalização de Pendências

**Data:** 14/02/2026  
**Projeto:** FC Soluções Financeiras  
**Objetivo:** Resolver todas as pendências críticas e preparar para deploy AWS  
**Metodologia:** Execução em gates com validação entre cada etapa

---

## 📋 METODOLOGIA DE GATES

```
Gate N → Execução → Validação Cliente → ✅ Passou → Commit + Push → Rollback Segurança → Gate N+1
                                      ↓ ❌ Falhou
                                      Rollback + Ajuste → Revalidação
```

---

## 🚀 GATE 1 - SEGURANÇA E DEPENDÊNCIAS (BLOQUEADORES CRÍTICOS)

**Duração Estimada:** 1-2 horas  
**Prioridade:** 🔴 CRÍTICA  
**Bloqueador de Deploy:** SIM

### Objetivo
Resolver vulnerabilidades de segurança e dependências faltantes que impedem testes e deploy seguro.

### Tarefas

#### 1.1 - Adicionar validate-docbr ao requirements.txt
```bash
# Adicionar dependência faltante
echo "" >> backend/requirements.txt
echo "# Document validation (CPF/CNPJ)" >> backend/requirements.txt  
echo "validate-docbr==1.10.0" >> backend/requirements.txt
```

**Validação:**
```bash
cd backend
python -m pytest -v --tb=short
# Esperado: Testes executam (mesmo que falhem, não deve dar ModuleNotFoundError)
```

#### 1.2 - Adicionar checagem de ambiente no security_stub.py
```python
# backend/app/security_stub.py
from app.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # SECURITY: Stub only works in development
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("security_stub.py must not be used in production!")
    
    # Accept test password in dev/staging only
    if plain_password == "1234":
        return True
    # ... resto do código
```

**Validação:**
- Verificar que login com `1234` ainda funciona em dev
- Adicionar variável `ENVIRONMENT=production` e verificar erro

#### 1.3 - Documentar processo de secrets para produção
Criar `docs/DEPLOY_SECRETS.md` com instruções claras:

```markdown
# Geração de Secrets para Produção

## Antes do Deploy

```bash
# 1. Gerar SECRET_KEY forte (32+ caracteres)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Gerar EVOLUTION_API_KEY forte
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Configurar no servidor EC2
cat > /opt/fabio2/.env.prod << EOF
SECRET_KEY=<secret_gerado_1>
EVOLUTION_API_KEY=<secret_gerado_2>
OPENAI_API_KEY=<chave_openai_producao>
MINIMAX_API_KEY=<chave_minimax>
MINIMAX_GROUP_ID=<group_id_minimax>
DATABASE_URL=postgresql+asyncpg://...
EOF
```

### Critérios de Aceitação (Gate 1)

- [ ] `validate-docbr` instalado e testes executando
- [ ] `security_stub.py` com proteção de ambiente
- [ ] Documentação de secrets criada
- [ ] Smoke test: `pytest` executa sem erro de import
- [ ] Smoke test: Login dev ainda funciona

### Entregáveis
- `backend/requirements.txt` atualizado
- `backend/app/security_stub.py` com checagem
- `docs/DEPLOY_SECRETS.md` criado
- Commit: "feat(security): adiciona proteção de secrets e valida dependências"

---

## ⚡ GATE 2 - PERFORMANCE VIVA (STREAMING)

**Duração Estimada:** 2-3 horas  
**Prioridade:** 🔴 ALTA  
**Bloqueador de Deploy:** NÃO (mas impacta UX crítico)

### Objetivo
Implementar streaming no chat VIVA para reduzir latência percebida e melhorar experiência do usuário.

### Tarefas

#### 2.1 - Implementar streaming no backend
```python
# backend/app/api/v1/viva.py (ou novo arquivo viva_chat_routes.py)

from fastapi.responses import StreamingResponse
import json

@router.post("/chat/stream")
async def chat_stream(
    request: VivaChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat VIVA com streaming de resposta."""
    
    async def generate():
        # Preparar contexto
        messages = await orchestrator.prepare_context(
            user_id=current_user.id,
            session_id=request.session_id,
            message=request.message
        )
        
        # Stream OpenAI
        full_response = ""
        async for chunk in openai_service.chat_stream(messages):
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Persistir resposta completa
        await orchestrator.save_message(
            user_id=current_user.id,
            session_id=request.session_id,
            content=full_response,
            role="assistant"
        )
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

#### 2.2 - Atualizar frontend para consumir streaming
```typescript
// frontend/src/app/viva/page.tsx

const handleSendStream = async (message: string) => {
  setLoading(true);
  
  // Adicionar mensagem do usuário
  const userMsg = { role: 'user', content: message };
  setMessages(prev => [...prev, userMsg]);
  
  // Preparar mensagem do assistente
  const assistantMsgId = Date.now();
  setMessages(prev => [...prev, { 
    id: assistantMsgId,
    role: 'assistant', 
    content: '',
    streaming: true 
  }]);
  
  try {
    const response = await fetch('/api/v1/viva/chat/stream', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.content) {
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMsgId 
                ? { ...msg, content: msg.content + data.content }
                : msg
            ));
          }
          
          if (data.done) {
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMsgId 
                ? { ...msg, streaming: false }
                : msg
            ));
          }
        }
      }
    }
  } catch (error) {
    console.error('Stream error:', error);
    // Fallback para endpoint não-streaming
    handleSendFallback(message);
  } finally {
    setLoading(false);
  }
};
```

#### 2.3 - Limitar contexto de mensagens
```python
# backend/app/services/viva_chat_orchestrator_service.py

MAX_CONTEXT_MESSAGES = 10  # Últimas 10 mensagens
MAX_CONTEXT_TOKENS = 4000   # ~3000 palavras

async def prepare_context(
    self, 
    user_id: int, 
    session_id: str, 
    message: str
) -> List[dict]:
    """Prepara contexto otimizado para o modelo."""
    
    # Buscar mensagens recentes da sessão
    recent_messages = await self.chat_repo.get_session_messages(
        user_id=user_id,
        session_id=session_id,
        limit=MAX_CONTEXT_MESSAGES
    )
    
    # Montar contexto
    context = [{"role": "system", "content": self.get_system_prompt()}]
    
    # Adicionar mensagens do histórico (mais recentes primeiro, depois inverter)
    for msg in reversed(recent_messages):
        context.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Adicionar mensagem atual
    context.append({"role": "user", "content": message})
    
    # TODO: Implementar truncagem por tokens se exceder MAX_CONTEXT_TOKENS
    
    return context
```

### Critérios de Aceitação (Gate 2)

- [ ] Endpoint `/viva/chat/stream` implementado
- [ ] Frontend consumindo streaming (SSE)
- [ ] Contexto limitado a 10 mensagens
- [ ] Fallback para modo não-streaming em caso de erro
- [ ] Latência percebida < 1s (primeiro token)
- [ ] Smoke test: Chat responde com streaming visível

### Entregáveis
- Backend com streaming
- Frontend com UI de streaming
- Commit: "feat(viva): implementa streaming de chat para reduzir latência"

---

## 🖼️ GATE 3 - OTIMIZAÇÃO FRONTEND (PERFORMANCE)

**Duração Estimada:** 2-3 horas  
**Prioridade:** 🟡 MÉDIA  
**Bloqueador de Deploy:** NÃO

### Objetivo
Otimizar performance do frontend resolvendo warnings de lint e melhorando Core Web Vitals.

### Tarefas

#### 3.1 - Substituir <img> por next/image
Arquivos a atualizar:
- `src/app/(dashboard)/campanhas/page.tsx` (2 ocorrências)
- `src/app/(dashboard)/contratos/[id]/page.tsx` (1 ocorrência)
- `src/app/(dashboard)/whatsapp/page.tsx` (1 ocorrência)
- `src/app/viva/page.tsx` (5 ocorrências)

```tsx
// Antes
<img src="/logo.png" alt="Logo" className="h-12" />

// Depois
import Image from 'next/image'

<Image 
  src="/logo.png" 
  alt="Logo" 
  width={200} 
  height={48} 
  className="h-12 w-auto"
  priority // se for LCP element
/>
```

**Observação:** Para imagens dinâmicas (URLs de campanhas), usar `unoptimized`:
```tsx
<Image 
  src={campaign.image_url} 
  alt={campaign.title}
  width={400}
  height={400}
  unoptimized // URLs externas ou geradas dinamicamente
/>
```

#### 3.2 - Corrigir warnings de exhaustive-deps
```tsx
// src/app/(dashboard)/campanhas/page.tsx

const loadCampanhas = useCallback(async () => {
  // ... lógica existente
}, []); // Sem dependências se não usar nenhuma

useEffect(() => {
  loadCampanhas();
}, [loadCampanhas]); // Agora inclui a dependência
```

```tsx
// src/app/(dashboard)/contratos/[id]/editar/page.tsx

const carregarContrato = useCallback(async () => {
  // ... lógica existente
}, [id]); // Incluir dependências usadas

useEffect(() => {
  if (id) {
    carregarContrato();
  }
}, [id, carregarContrato]);
```

#### 3.3 - Validar build de produção
```bash
cd frontend
npm run build

# Verificar warnings/erros
# Verificar tamanho dos bundles
```

### Critérios de Aceitação (Gate 3)

- [ ] Todos os `<img>` substituídos por `<Image />`
- [ ] Warnings de `exhaustive-deps` corrigidos
- [ ] `npm run lint` sem warnings
- [ ] `npm run build` com sucesso
- [ ] Bundle size aceitável (<1MB first load JS)

### Entregáveis
- 11 substituições de imagem
- 2 correções de hooks
- Commit: "perf(frontend): otimiza imagens e corrige warnings de hooks"

---

## 🎨 GATE 4 - UX VIVA (UI/RESPONSIVIDADE)

**Duração Estimada:** 2-3 horas  
**Prioridade:** 🟡 MÉDIA  
**Bloqueador de Deploy:** NÃO

### Objetivo
Melhorar experiência visual da VIVA resolvendo BUG-096 e BUG-097.

### Tarefas

#### 4.1 - Ajustar escala da UI VIVA (BUG-096)
```tsx
// frontend/src/app/viva/page.tsx

// Ajustar tamanhos de fonte e containers
<div className="max-w-4xl mx-auto"> {/* Era 5xl ou 6xl */}
  <div className="text-base"> {/* Era text-lg */}
    {/* Conteúdo do chat */}
  </div>
</div>

// Modal de preview de imagem
<Dialog>
  <DialogContent className="max-w-3xl max-h-[85vh]"> {/* Limites razoáveis */}
    <img 
      src={previewImage} 
      className="max-w-full max-h-[70vh] object-contain"
    />
  </DialogContent>
</Dialog>
```

#### 4.2 - Ajustar overlay de "Arte Final" (BUG-097)
```tsx
// frontend/src/app/viva/page.tsx

// Função de composição do overlay
const composeArteFinal = (imageUrl: string, copy: CampanhaCopy) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Dimensões baseadas no formato
  const aspectRatios = {
    '1:1': { width: 1080, height: 1080 },
    '4:5': { width: 1080, height: 1350 },
    '16:9': { width: 1920, height: 1080 },
    '9:16': { width: 1080, height: 1920 }
  };
  
  const dimensions = aspectRatios[copy.formato] || aspectRatios['1:1'];
  canvas.width = dimensions.width;
  canvas.height = dimensions.height;
  
  // Carregar imagem de fundo
  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    // Desenhar imagem de fundo (cover, centralizada)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    // Overlay topo (20% da altura máximo)
    const topHeight = Math.min(canvas.height * 0.2, 200);
    const gradientTop = ctx.createLinearGradient(0, 0, 0, topHeight);
    gradientTop.addColorStop(0, 'rgba(0,0,0,0.8)');
    gradientTop.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gradientTop;
    ctx.fillRect(0, 0, canvas.width, topHeight);
    
    // Headline no topo
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    wrapText(ctx, copy.headline, canvas.width / 2, 60, canvas.width * 0.9, 60);
    
    // Overlay rodapé (25% da altura máximo)
    const bottomHeight = Math.min(canvas.height * 0.25, 300);
    const bottomY = canvas.height - bottomHeight;
    const gradientBottom = ctx.createLinearGradient(0, bottomY, 0, canvas.height);
    gradientBottom.addColorStop(0, 'rgba(0,0,0,0)');
    gradientBottom.addColorStop(1, 'rgba(0,0,0,0.9)');
    ctx.fillStyle = gradientBottom;
    ctx.fillRect(0, bottomY, canvas.width, bottomHeight);
    
    // CTA e textos no rodapé
    const ctaY = canvas.height - bottomHeight + 40;
    ctx.font = 'bold 36px Arial';
    ctx.fillStyle = '#FFD700';
    wrapText(ctx, copy.cta, canvas.width / 2, ctaY, canvas.width * 0.9, 50);
    
    // ... resto do código
  };
  img.src = imageUrl;
};

// Função auxiliar para quebrar texto
function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(' ');
  let line = '';
  let lines = [];
  
  for (let word of words) {
    const testLine = line + word + ' ';
    const metrics = ctx.measureText(testLine);
    
    if (metrics.width > maxWidth && line !== '') {
      lines.push(line);
      line = word + ' ';
    } else {
      line = testLine;
    }
  }
  lines.push(line);
  
  // Desenhar linhas
  lines.forEach((line, i) => {
    ctx.fillText(line.trim(), x, y + (i * lineHeight));
  });
}
```

#### 4.3 - Preview por formato
```tsx
// Adicionar seletor de formato no preview
<div className="flex gap-2 mb-4">
  <Button 
    variant={formato === '1:1' ? 'default' : 'outline'}
    onClick={() => setFormato('1:1')}
  >
    1:1 (Feed)
  </Button>
  <Button 
    variant={formato === '4:5' ? 'default' : 'outline'}
    onClick={() => setFormato('4:5')}
  >
    4:5 (Feed vertical)
  </Button>
  {/* ... outros formatos */}
</div>
```

### Critérios de Aceitação (Gate 4)

- [ ] UI VIVA confortável em zoom 100%
- [ ] Overlay de arte final proporcional à imagem
- [ ] Preview respeita formato selecionado
- [ ] Textos não "comem" a foto
- [ ] Responsivo em mobile (>= 375px)

### Entregáveis
- UI VIVA otimizada
- Overlay de arte final ajustado
- Preview por formato
- Commit: "fix(viva): ajusta UI para zoom 100% e overlay de campanhas"

---

## 🔊 GATE 5 - VOZ INSTITUCIONAL (MINIMAX TTS)

**Duração Estimada:** 2-3 horas  
**Prioridade:** 🟡 MÉDIA  
**Bloqueador de Deploy:** NÃO

### Objetivo
Estabilizar voz institucional da VIVA e adicionar diagnóstico claro de falhas (BUG-098).

### Tarefas

#### 5.1 - Adicionar endpoint de status da voz
```python
# backend/app/api/v1/viva_media_routes.py

@router.get("/tts/status")
async def tts_status(current_user: User = Depends(get_current_user)):
    """Diagnóstico do status do TTS."""
    
    minimax_configured = bool(
        settings.MINIMAX_API_KEY and 
        settings.MINIMAX_GROUP_ID
    )
    
    status = {
        "provider": "minimax",
        "configured": minimax_configured,
        "missing_vars": []
    }
    
    if not settings.MINIMAX_API_KEY:
        status["missing_vars"].append("MINIMAX_API_KEY")
    if not settings.MINIMAX_GROUP_ID:
        status["missing_vars"].append("MINIMAX_GROUP_ID")
    
    if minimax_configured:
        try:
            # Testar chamada básica
            test_result = await minimax_service.test_connection()
            status["test"] = "success" if test_result else "failed"
        except Exception as e:
            status["test"] = "failed"
            status["error"] = str(e)
    
    return status
```

#### 5.2 - Melhorar mensagens de erro no frontend
```typescript
// frontend/src/app/viva/page.tsx

const checkTTSStatus = async () => {
  try {
    const response = await api.get('/viva/tts/status');
    const status = response.data;
    
    if (!status.configured) {
      setTtsError(`Voz institucional indisponível. Variáveis faltando: ${status.missing_vars.join(', ')}`);
      return false;
    }
    
    if (status.test === 'failed') {
      setTtsError(`Erro ao testar voz: ${status.error || 'Desconhecido'}`);
      return false;
    }
    
    return true;
  } catch (error) {
    setTtsError('Erro ao verificar status da voz');
    return false;
  }
};

// Chamar ao ativar modo Conversa VIVA
const handleConversaMode = async () => {
  const ttsOk = await checkTTSStatus();
  
  if (!ttsOk) {
    toast.error('Voz institucional indisponível. Usando voz do navegador.');
    // Fallback para speechSynthesis
  }
  
  setConversaMode(true);
};
```

#### 5.3 - Implementar retry e timeout
```python
# backend/app/services/minimax_tts_service.py

import asyncio

async def text_to_speech(
    self, 
    text: str,
    max_retries: int = 2,
    timeout: int = 30
) -> bytes:
    """Gera áudio com retry e timeout."""
    
    for attempt in range(max_retries + 1):
        try:
            response = await asyncio.wait_for(
                self._call_minimax_api(text),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            if attempt < max_retries:
                await asyncio.sleep(1)  # Backoff
                continue
            raise Exception("TTS timeout após retries")
        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(1)
                continue
            raise
```

### Critérios de Aceitação (Gate 5)

- [ ] Endpoint `/tts/status` retorna diagnóstico claro
- [ ] Frontend exibe mensagem específica em caso de falha
- [ ] Retry implementado (2 tentativas)
- [ ] Timeout de 30s por tentativa
- [ ] Fallback gracioso para voz do navegador

### Entregáveis
- Diagnóstico de TTS
- Mensagens de erro claras
- Retry e timeout
- Commit: "feat(viva): adiciona diagnóstico e retry para voz institucional"

---

## 📅 GATE 6 - GOOGLE CALENDAR (OPCIONAL)

**Duração Estimada:** 3-4 horas  
**Prioridade:** 🟢 BAIXA  
**Bloqueador de Deploy:** NÃO

### Objetivo
Validar ou remover integração Google Calendar (BUG-095).

### Opção A - Implementar Integração Completa

#### 6.1 - OAuth Flow
```python
# backend/app/api/v1/google_calendar.py

@router.get("/auth")
async def google_auth_start(current_user: User = Depends(get_current_user)):
    """Inicia fluxo OAuth Google Calendar."""
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=[settings.GOOGLE_CALENDAR_SCOPE]
    )
    
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=str(current_user.id)  # Para vincular depois
    )
    
    return {"authorization_url": authorization_url}

@router.get("/callback")
async def google_auth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Callback OAuth Google Calendar."""
    
    flow = Flow.from_client_config(...)
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    user_id = int(state)
    
    # Salvar tokens no banco
    await google_calendar_service.save_credentials(
        user_id=user_id,
        credentials=credentials,
        db=db
    )
    
    return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/agenda?google_linked=true")
```

#### 6.2 - Sincronização Bidirecional
```python
# backend/app/services/google_calendar_sync_service.py

async def sync_event_to_google(
    self,
    user_id: int,
    event: AgendaItem,
    db: AsyncSession
):
    """Sincroniza evento local para Google Calendar."""
    
    credentials = await self.get_user_credentials(user_id, db)
    if not credentials:
        return None
    
    service = build('calendar', 'v3', credentials=credentials)
    
    google_event = {
        'summary': event.title,
        'description': event.description,
        'start': {
            'dateTime': event.start_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': event.end_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }
    
    result = service.events().insert(
        calendarId='primary',
        body=google_event
    ).execute()
    
    # Salvar google_event_id no evento local
    event.google_event_id = result['id']
    db.add(event)
    await db.commit()
    
    return result

async def sync_from_google(self, user_id: int, db: AsyncSession):
    """Importa eventos do Google Calendar."""
    # ... implementação
```

### Opção B - Remover Integração (Mais Rápido)

Se não for prioridade, remover:
- Variáveis de `backend/.env.example` relacionadas ao Google
- Comentários/código placeholder em `backend/app/config.py`
- Documentar remoção em `docs/DECISIONS.md`

### Critérios de Aceitação (Gate 6)

**Se implementar:**
- [ ] OAuth flow funcional
- [ ] Sincronização bidirecional
- [ ] Eventos locais vão para Google
- [ ] Eventos Google vêm para local
- [ ] Desconexão funcional

**Se remover:**
- [ ] Variáveis removidas de `.env.example`
- [ ] Documentado em `DECISIONS.md`
- [ ] Código placeholder removido

### Entregáveis
- Integração completa OU remoção documentada
- Commit: "feat(agenda): implementa sincronização Google Calendar" OU "docs: remove placeholder Google Calendar"

---

## 🧪 GATE 7 - TESTES E QUALIDADE

**Duração Estimada:** 4-6 horas  
**Prioridade:** 🟡 MÉDIA  
**Bloqueador de Deploy:** NÃO (mas recomendado)

### Objetivo
Implementar cobertura mínima de testes para garantir estabilidade.

### Tarefas

#### 7.1 - Testes de Autenticação
```python
# backend/tests/test_auth.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "fabio@fcsolucoes.com", "password": "1234"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "fabio@fcsolucoes.com", "password": "wrong"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "fabio@fcsolucoes.com"

@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
```

#### 7.2 - Testes de Contratos
```python
# backend/tests/test_contratos.py

@pytest.mark.asyncio
async def test_create_contrato(client: AsyncClient, auth_headers):
    payload = {
        "template_id": "bacen",
        "cliente": {
            "nome": "Teste Cliente",
            "documento": "12345678900",
            "tipo_pessoa": "F"
        },
        "valor": 1000.0,
        "parcelas": 3
    }
    
    response = await client.post(
        "/api/v1/contratos",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["template_id"] == "bacen"
    assert data["numero"].startswith("CNT-2026-")

@pytest.mark.asyncio
async def test_list_contratos(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/contratos", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_contrato_pdf(client: AsyncClient, auth_headers, sample_contrato_id):
    response = await client.get(
        f"/api/v1/contratos/{sample_contrato_id}/pdf",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
```

#### 7.3 - Testes de VIVA Chat
```python
# backend/tests/test_viva_chat.py

@pytest.mark.asyncio
async def test_viva_chat_basic(client: AsyncClient, auth_headers):
    payload = {
        "message": "Olá VIVA, tudo bem?",
        "session_id": "test-session-123"
    }
    
    response = await client.post(
        "/api/v1/viva/chat",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "resposta" in data
    assert "session_id" in data
    assert len(data["resposta"]) > 0

@pytest.mark.asyncio
async def test_viva_session_continuity(client: AsyncClient, auth_headers):
    session_id = "test-session-continuity"
    
    # Primeira mensagem
    response1 = await client.post(
        "/api/v1/viva/chat",
        json={"message": "Meu nome é João", "session_id": session_id},
        headers=auth_headers
    )
    assert response1.status_code == 200
    
    # Segunda mensagem
    response2 = await client.post(
        "/api/v1/viva/chat",
        json={"message": "Qual é o meu nome?", "session_id": session_id},
        headers=auth_headers
    )
    assert response2.status_code == 200
    assert "joão" in response2.json()["resposta"].lower()
```

#### 7.4 - Fixtures e Configuração
```python
# backend/tests/conftest.py

import pytest
from httpx import AsyncClient
from app.main import app
from app.db import get_db

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "fabio@fcsolucoes.com", "password": "1234"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def sample_contrato_id(client: AsyncClient, auth_headers):
    # Criar contrato de teste
    response = await client.post(
        "/api/v1/contratos",
        json={...},
        headers=auth_headers
    )
    return response.json()["id"]
```

### Critérios de Aceitação (Gate 7)

- [ ] 15+ testes implementados
- [ ] Cobertura > 50% dos endpoints críticos
- [ ] Todos os testes passando
- [ ] `pytest` executando sem erros
- [ ] Documentação de como rodar testes

### Entregáveis
- Suite de testes funcional
- README com instruções de teste
- Commit: "test: adiciona cobertura de testes para auth, contratos e viva"

---

## 📦 GATE 8 - BUILD E DEPLOY PREPARATION

**Duração Estimada:** 2-3 horas  
**Prioridade:** 🔴 ALTA  
**Bloqueador de Deploy:** SIM

### Objetivo
Validar builds de produção e preparar ambiente para deploy AWS.

### Tarefas

#### 8.1 - Validar Build Frontend
```bash
cd frontend

# Build de produção
npm run build

# Verificar saída
ls -lh .next/static
ls -lh .next/server

# Verificar tamanho dos bundles
du -sh .next

# Testar servidor de produção localmente
npm run start
# Acessar http://localhost:3000 e validar todas as rotas principais
```

#### 8.2 - Validar Build Backend (Docker)
```bash
cd backend

# Build da imagem
docker build -t fabio2-backend:test .

# Testar imagem
docker run -d \
  --name fabio2-backend-test \
  -p 8001:8000 \
  -e DATABASE_URL="..." \
  -e REDIS_URL="..." \
  -e SECRET_KEY="..." \
  fabio2-backend:test

# Validar endpoints
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/auth/login -X POST -d '{"email":"...","password":"..."}'

# Parar e remover
docker stop fabio2-backend-test
docker rm fabio2-backend-test
```

#### 8.3 - Atualizar Documentação de Deploy
```markdown
# docs/DEPLOY_AWS_CHECKLIST.md

## Pré-requisitos

- [ ] Instância EC2 Ubuntu 22.04 (t3.medium mínimo)
- [ ] Domínio configurado (A record para IP da EC2)
- [ ] Secrets gerados (SECRET_KEY, EVOLUTION_API_KEY, etc)
- [ ] Chaves OpenAI e MiniMax válidas

## Passos

1. **Conectar na EC2**
   ```bash
   ssh ubuntu@<IP_EC2>
   ```

2. **Instalar Docker e Docker Compose**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   # Relogar
   ```

3. **Clonar Repositório**
   ```bash
   git clone https://github.com/lucasricardolebre1984/fabio2.git
   cd fabio2
   ```

4. **Configurar Secrets**
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env
   # Preencher todas as variáveis de produção
   ```

5. **Subir Containers**
   ```bash
   docker-compose up -d --build
   ```

6. **Verificar Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f postgres
   ```

7. **Configurar Nginx + SSL**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   # Configurar reverse proxy
   # Obter certificado SSL
   ```

8. **Validação**
   - [ ] https://seudominio.com.br (frontend)
   - [ ] https://seudominio.com.br/api/v1/health (backend)
   - [ ] Login funcional
   - [ ] Contrato funcionando ponta a ponta
   - [ ] WhatsApp conectado
```

#### 8.4 - Dockerfile Frontend Correção
```dockerfile
# frontend/Dockerfile

FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json next.config.js tailwind.config.ts components.json postcss.config.js ./
COPY src ./src
COPY public ./public

RUN npm ci
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**Atualizar `next.config.js`:**
```js
module.exports = {
  output: 'standalone', // Necessário para Docker production
  // ... resto da config
}
```

### Critérios de Aceitação (Gate 8)

- [ ] `npm run build` sem erros
- [ ] Build Docker backend funcional
- [ ] Build Docker frontend funcional (standalone)
- [ ] Documentação de deploy atualizada
- [ ] Checklist de deploy criado
- [ ] Smoke test: Todos os containers sobem juntos

### Entregáveis
- Builds validados
- Dockerfile frontend corrigido
- Documentação de deploy completa
- Commit: "build: valida builds de produção e prepara deploy"

---

## 🎬 GATE FINAL - DOCUMENTAÇÃO E ROLLBACK

**Duração Estimada:** 1 hora  
**Prioridade:** 🔴 ALTA  
**Bloqueador de Deploy:** NÃO

### Objetivo
Consolidar documentação e criar rollback de segurança da versão final.

### Tarefas

#### 9.1 - Atualizar STATUS.md
Adicionar seção final:

```markdown
## Estado Pós-Auditoria (2026-02-14)

### Gates Executados
1. ✅ Segurança e Dependências (validate-docbr, security_stub)
2. ✅ Performance VIVA (streaming implementado)
3. ✅ Otimização Frontend (next/image, hooks)
4. ✅ UX VIVA (UI responsiva, overlay ajustado)
5. ✅ Voz Institucional (diagnóstico MiniMax TTS)
6. ⏭️ Google Calendar (opcional - removido)
7. ✅ Testes e Qualidade (cobertura básica)
8. ✅ Build e Deploy Preparation (validado)
9. ✅ Documentação Final

### Bugs Resolvidos nesta Rodada
- Dependência validate-docbr ausente
- BUG-099: Latência alta (streaming)
- BUG-096: UI zoom 100%
- BUG-097: Overlay arte final
- BUG-098: Diagnóstico TTS
- Warnings lint frontend (11 itens)

### Status Atual
- **Resolvidos:** 67 bugs (+7 desta rodada)
- **Ativos:** 0 bugs críticos
- **Pronto para deploy:** ✅ SIM

### Próximos Passos
1. Deploy staging em EC2
2. Testes de aceitação com cliente
3. Deploy produção com monitoramento
```

#### 9.2 - Atualizar BUGSREPORT.md
Mover bugs resolvidos desta rodada para seção de resolvidos:

```markdown
## Bugs Resolvidos nesta Auditoria (2026-02-14)

| ID | Módulo | Descrição | Data |
|----|--------|-----------|------|
| - | Backend | Dependência validate-docbr ausente | 2026-02-14 |
| BUG-099 | VIVA | Latência alta (streaming implementado) | 2026-02-14 |
| BUG-096 | VIVA/Frontend | UI grande demais zoom 100% | 2026-02-14 |
| BUG-097 | VIVA/Campanhas | Overlay arte final cobre foto | 2026-02-14 |
| BUG-098 | VIVA/TTS | Voz MiniMax sem diagnóstico | 2026-02-14 |
| - | Frontend | 11 warnings de <img> e hooks | 2026-02-14 |
```

#### 9.3 - Criar Rollback Final
```bash
# Criar tag de versão
git tag -a v1.0.0-pre-deploy -m "Versão auditada e pronta para deploy"

# Criar rollback completo
mkdir -p docs/ROLLBACK
git diff > docs/ROLLBACK/rollback-20260214-$(date +%H%M%S)-pos-auditoria.patch
git status > docs/ROLLBACK/rollback-20260214-$(date +%H%M%S)-status.txt

# Backup de arquivos críticos
tar -czf docs/ROLLBACK/backup-20260214-criticos.tar.gz \
  backend/requirements.txt \
  backend/app/config.py \
  backend/app/security_stub.py \
  frontend/package.json \
  docker-compose.yml
```

#### 9.4 - Atualizar README.md
```markdown
## 🎉 Status: PRONTO PARA DEPLOY

**Última Auditoria:** 14/02/2026  
**Bugs Críticos:** 0  
**Cobertura de Testes:** 50%+  
**Build de Produção:** ✅ Validado

### Deploy AWS

Siga o guia completo em [DEPLOY_AWS_CHECKLIST.md](docs/DEPLOY_AWS_CHECKLIST.md).

**Resumo:**
1. Configure secrets em `/opt/fabio2/.env`
2. Execute `docker-compose up -d --build`
3. Configure Nginx + SSL
4. Valide endpoints críticos

### Rollback

Em caso de problemas, aplicar rollback:
```bash
git checkout v1.0.0-pre-deploy
docker-compose down
docker-compose up -d --build
```
```

### Critérios de Aceitação (Gate Final)

- [ ] `STATUS.md` atualizado
- [ ] `BUGSREPORT.md` atualizado
- [ ] Tag `v1.0.0-pre-deploy` criada
- [ ] Rollback completo gerado
- [ ] `README.md` atualizado com status de deploy
- [ ] Documentação de auditoria completa

### Entregáveis
- Documentação consolidada
- Tag de versão
- Rollback de segurança
- Commit: "docs: consolida auditoria e prepara versão v1.0.0-pre-deploy"

---

## 📊 RESUMO DE EXECUÇÃO

### Timeline Estimado

| Gate | Duração | Acumulado | Prioridade |
|------|---------|-----------|------------|
| Gate 1 - Segurança | 1-2h | 2h | 🔴 Crítica |
| Gate 2 - Streaming | 2-3h | 5h | 🔴 Alta |
| Gate 3 - Frontend Perf | 2-3h | 8h | 🟡 Média |
| Gate 4 - UX VIVA | 2-3h | 11h | 🟡 Média |
| Gate 5 - Voz TTS | 2-3h | 14h | 🟡 Média |
| Gate 6 - Google Cal | 3-4h | 18h | 🟢 Baixa (opcional) |
| Gate 7 - Testes | 4-6h | 24h | 🟡 Média |
| Gate 8 - Build/Deploy | 2-3h | 27h | 🔴 Alta |
| Gate 9 - Documentação | 1h | 28h | 🔴 Alta |

**Total Estimado:** 24-28 horas de trabalho  
**Distribuído em:** 3-4 dias úteis

### Fluxo de Validação

```
┌──────────────────────────────────────────────────────────┐
│                     GATE N                                │
│                                                            │
│  1. Executar tarefas                                      │
│  2. Validação técnica (testes/build)                     │
│  3. Apresentar ao cliente                                 │
│     ↓                                                      │
│  4. Cliente valida                                        │
│     ├─ ✅ Aprovado ─→ Commit + Push ─→ Rollback ─→ GATE N+1│
│     └─ ❌ Rejeitado ─→ Rollback ─→ Ajuste ─→ Revalidação │
└──────────────────────────────────────────────────────────┘
```

### Ordem de Prioridade Recomendada

1. **Obrigatórios antes de deploy:**
   - Gate 1 (Segurança)
   - Gate 8 (Build/Deploy)
   - Gate 9 (Documentação)

2. **Altamente recomendados:**
   - Gate 2 (Streaming VIVA)
   - Gate 7 (Testes básicos)

3. **Melhorias de UX:**
   - Gate 3 (Frontend Performance)
   - Gate 4 (UX VIVA)
   - Gate 5 (Voz TTS)

4. **Opcional:**
   - Gate 6 (Google Calendar) - pode ser fase 2

---

## 🔒 PROTOCOLO DE SEGURANÇA ENTRE GATES

Após cada gate aprovado:

```bash
# 1. Commit local
git add .
git commit -m "feat(gateN): [descrição]"

# 2. Push para remoto
git push origin main

# 3. Criar rollback de segurança
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
git diff HEAD~1 > docs/ROLLBACK/rollback-$TIMESTAMP-gate-N.patch
git log -1 > docs/ROLLBACK/rollback-$TIMESTAMP-gate-N-commit.txt

# 4. Validar que push foi bem-sucedido
git fetch origin
git diff main origin/main  # Deve estar vazio

# 5. Prosseguir para próximo gate
```

---

## ✅ CHECKLIST FINAL DE DEPLOY

Antes de fazer deploy em produção, validar:

### Segurança
- [ ] Todos os secrets trocados
- [ ] `security_stub.py` com proteção de ambiente
- [ ] HTTPS/SSL configurado
- [ ] Rate limiting ativo

### Funcionalidade
- [ ] Login funcional
- [ ] Contratos (criar/visualizar/PDF)
- [ ] Clientes (CRUD)
- [ ] Agenda (criar/listar)
- [ ] VIVA chat responde
- [ ] WhatsApp webhook ativo
- [ ] Streaming funcionando

### Performance
- [ ] Latência chat < 2s (primeiro token)
- [ ] Build frontend < 3MB first load
- [ ] Imagens otimizadas (next/image)

### Monitoramento
- [ ] Logs centralizados
- [ ] Alertas de erro configurados
- [ ] Backup automatizado ativo

---

*Plano criado em: 14/02/2026*  
*Responsável: Warp AI Agent (Oz)*  
*Aprovação Cliente: Pendente*

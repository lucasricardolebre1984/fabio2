# ARQUITETURA - Visao Geral

Projeto: FC Solucoes Financeiras SaaS
Versao documental: 2.0
Data de revisao: 2026-02-16

## Visao macro

```text
Browser (Next.js)
  -> /api/v1
FastAPI
  -> PostgreSQL
  -> Redis
  -> Evolution API (WhatsApp)
```

## Dominios funcionais

- VIVA (chat interno do SaaS)
- Contratos
- Clientes
- Agenda
- Campanhas
- WhatsApp
- COFRE (persona, skills, memorias)

## Fonte canonica da VIVA

- Persona principal: `backend/COFRE/persona-skills/viva/AGENT.md`
- Skills operacionais: `backend/COFRE/persona-skills/*.md`
- Memorias por tabela: `backend/COFRE/memories/<tabela>/`

Compatibilidade:
- `agents/AGENT.md` existe apenas como ponte para o AGENT canonico do COFRE.

## Fluxo de chat VIVA

1. Front envia mensagem para `POST /api/v1/viva/chat`
2. Backend persiste sessao/mensagem
3. Backend aplica roteamento por intencao (skills)
4. Backend consulta dados reais de modulos quando necessario
5. Backend devolve resposta + metadados
6. Persistencia espelha eventos relevantes no COFRE

## Regra de memoria institucional

- Evento funcional no SaaS deve refletir em banco e no espelho COFRE.
- Exclusao funcional deve apagar registro funcional e artefato de memoria correspondente.

Exemplo ja aplicado:
- Campanhas: delete por ID e reset total removem banco + espelho COFRE + tentativa de asset local.

## Rotas frontend principais

- `/`
- `/viva`
- `/contratos`
- `/clientes`
- `/agenda`
- `/campanhas`
- `/whatsapp`

## Rotas backend principais

- Auth: `/api/v1/auth/*`
- Contratos: `/api/v1/contratos*`
- Clientes: `/api/v1/clientes*`
- Agenda: `/api/v1/agenda*`
- Google Calendar: `/api/v1/google-calendar/*`
- VIVA: `/api/v1/viva/*`
- WhatsApp: `/api/v1/whatsapp*`, `/api/v1/whatsapp-chat/*`
- COFRE: `/api/v1/cofre/memories/*`, `/api/v1/cofre/system/*`

## Integridade menu -> API -> banco -> COFRE

Matriz oficial desta rodada:
- `docs/AUDIT/menu-endpoint-matrix.md`

Status da matriz: todos os menus em `ok` no mapeamento tecnico desta auditoria.

## Diretriz de deploy

- Producao institucional: Ubuntu AWS com Docker
- Vercel fora do escopo institucional atual

Atualizado em: 2026-02-16


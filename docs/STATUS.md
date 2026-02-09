# STATUS do projeto - FC Solucoes Financeiras

Data: 09/02/2026
Sessao: estabilizacao de unicidade clientes + fluxo de contratos (cpf/cnpj)
Status: V1.7 local com contratos/clientes saneados (OpenAI + Evolution estavel)

## Objetivo atual
Consolidar operacao comercial da Viviane no WhatsApp com regras de negocio,
qualificacao de lead, politica de preco e governanca de atendimento humano.

## Funcionalidades operacionais
- Contratos com templates dinamicos
- Clientes e agenda
- Chat interno VIVA em `/viva`
- Conexao WhatsApp em `/whatsapp`
- Gestao de conversas em `/whatsapp/conversas`

## Estado WhatsApp/VIVA
- Instancia Evolution definitiva: `fc-solucoes`
- Instancia de teste removida: `tmp-fc-8601`
- Persona comercial aprovada: Viviane, consultora da Rezeta
- Fontes de conhecimento organizadas em `frontend/src/app/viva/REGRAS`
- Provedor IA ativo: OpenAI (`gpt-5-mini`)

## Estado Contratos/PDF
- `GET /api/v1/contratos/{id}/pdf` reabilitado com sucesso (sem `500`)
- Fallback de renderizacao aplicado: Playwright -> WeasyPrint
- Dependencia fixada: `pydyf==0.10.0` (compatibilidade com WeasyPrint 60.2)

## Estado Clientes/Contratos (2026-02-09)
- Unicidade operacional por CPF/CNPJ normalizado estabilizada.
- Bug de `500` ao criar contrato com cliente duplicado eliminado.
- Endpoint admin para saneamento de base:
  - `POST /api/v1/clientes/deduplicar-documentos`
- Tela `/clientes` com acoes de:
  - cadastro manual
  - edicao
  - exclusao (admin)
  - saneamento de duplicados
- Tela `/contratos/novo` com busca de cliente por documento e autopreenchimento.

## Decisoes validadas com cliente
- Modo B (VIVA conduz; humano por excecao)
- Tom hibrido (consultivo + acolhedor)
- Fluxo 1 (objetivo -> perfil -> urgencia -> proximo passo)
- SLA 24/7 com callback em ate 15 min
- Coleta obrigatoria: nome, telefone, servico, cidade, urgencia
- Diagnostico 360 como recomendacao inicial
- Venda direta sem 360: Limpa Nome, Score e Rating
- Oferta inicial com margem de 15% sobre tabela
- Negociacao fina de preco somente com humano
- Objecao financeira registrada para follow-up

## Proximo gate
Iniciar ciclo de melhoria incremental (etiquetas de lead, scripts PF/PJ e painel de metricas),
fechando os bugs ativos de experiencia da VIVA (`BUG-012`, `BUG-015`, `BUG-016`)
sem regressao no fluxo comercial homologado.

## Documentos de referencia
- `docs/WHATSAPP_VIVA_PACOTE_DEFINITIVO.md`
- `docs/INTEGRACAO_WHATSAPP_VIVA.md`
- `docs/DECISIONS.md`
- `docs/SESSION.md`
- `docs/API.md`

---

Atualizado em: 09/02/2026

## Estado Contratos/Layout (2026-02-09)
- Logo oficial `logo2.png` padronizada no fluxo de contratos (preview + PDF frontend + PDF backend).
- Novo template operacional `CADIN PF/PJ` adicionado ao sistema.
- Menu de contratos com CADIN habilitado.
- Tela de novo contrato agora respeita `template` na URL (`/contratos/novo?template=cadin`).
- Template base criado em `contratos/templates/cadin.json`.


## Estado Contratos/Layout (2026-02-09 - logo transparente + CADIN completo)
- Logo oficial do cabecalho atualizada para `logo2.png` (transparente) no preview e nos dois fluxos de PDF.
- Template CADIN corrigido com clausulas completas e acentuacao conforme `cadinpfpjmodelo.docx`.
- Pipeline backend Playwright ajustado para usar marca transparente e subtitulo/template CADIN com texto canonico.

## Estado Contratos/Layout (2026-02-09 - acentuacao e legibilidade)
- Corrigido bug de acentuacao corrompida (mojibake) na visualizacao de contratos.
- Corrigido texto no PDF frontend/backend para manter acentos institucionais.
- Layout ampliado levemente (preview + PDF) para melhorar leitura operacional.

## Estado Contratos/Layout (2026-02-09 - ajuste final de assinatura)
- Rollback local adicional registrado:
  - `docs/ROLLBACK/rollback-20260209-131517.patch`
- Normalizacao de `local_assinatura` legado aplicada em:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
  - `frontend/src/lib/pdf.ts`
  - `backend/app/services/pdf_service_playwright.py`
- Correcao preventiva no cadastro de novo contrato:
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` agora usa `Ribeirao Preto/SP` no default de `local_assinatura`.
- Resultado esperado: rodape da assinatura com local exibido corretamente para registros novos e legados.

## Estado Clientes/Contratos (2026-02-09 - fechamento rodada)
- `/contratos` sem texto corrompido no menu de templates.
- `/clientes` com historico de contratos por cliente no proprio card.
- Contagem exibida em `/clientes` calculada por agregacao real de contratos no backend.
- Rollback desta rodada registrado em `docs/ROLLBACK/rollback-20260209-164001.patch`.

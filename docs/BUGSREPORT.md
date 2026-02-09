# BUGSREPORT - Registro de Bugs

> **Projeto:** FC Soluções Financeiras SaaS  
> **Última Atualização:** 2026-02-09

---

## Bugs Ativos

| ID | Severidade | Módulo | Descrição | Status |
|---|---|---|---|---|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Resolvido (runtime Docker) |
| BUG-012 | Média | VIVA | Botão de áudio no chat não funciona | Ativo |
| BUG-013 | Média | VIVA | Erro `StackOverflowError` ao gerar imagem com prompt extra longo (REZETA/FC) | Resolvido |
| BUG-014 | Média | VIVA | Upload de imagem falha quando a imagem é PNG (MIME assumido como JPEG) | Resolvido |
| BUG-015 | Alta | VIVA | Fundo da imagem não respeita paleta/brief do prompt (resultado genérico) | Ativo |
| BUG-016 | Média | VIVA | Arte final perde partes do texto (overlay truncado) | Ativo |
| BUG-017 | Alta | WhatsApp Chat API | Endpoints `/api/v1/whatsapp-chat/*` retornam 500 por incompatibilidade de modelagem (`SQLEnum`) com schema real (`VARCHAR`) | Resolvido |
| BUG-018 | Alta | WhatsApp Evolution | Backend consulta instância/chave divergentes do runtime (instância ativa `Teste`), causando falso desconectado (`Status 404`) | Resolvido |
| BUG-019 | Média | Frontend WhatsApp | `/whatsapp/conversas` usa token incorreto (`localStorage.token`) e base URL hardcoded em `localhost:8000` | Resolvido |
| BUG-020 | Alta | Webhook WhatsApp | Resposta da VIVA não é enviada ao WhatsApp no webhook (envio real marcado como TODO) | Resolvido |
| BUG-021 | Alta | Webhook WhatsApp | Mensagem de áudio recebida no WhatsApp não era transcrita para o fluxo da VIVA (áudio obrigatório) | Resolvido |
| BUG-022 | Média | Webhook WhatsApp | Intermitência de envio (`400 Text is required` e `exists:false`) por payload vazio/JID não entregável no retorno da IA | Resolvido |
| BUG-023 | Alta | VIVA/OpenAI | `OPENAI_API_KEY` vazio no container por override do `docker-compose` bloqueava respostas da IA | Resolvido |
| BUG-024 | Média | VIVA/OpenAI | Geração de imagem falhava com `Unknown parameter: response_format` no endpoint OpenAI Images | Resolvido |
| BUG-025 | Alta | Contratos | Criação de contrato em `/contratos/novo` falhava com `Network Error` porque `POST /api/v1/contratos` retornava `500` (`Template bacen não encontrado`) | Resolvido |
| BUG-027 | Alta | Clientes/Contratos | Contratos criados sem vínculo de cliente não apareciam na tela de clientes | Resolvido |
| BUG-028 | Alta | Contratos | Geração de número por contagem anual permitia duplicidade (`ix_contratos_numero`) quando havia gaps | Resolvido |
| BUG-026 | Alta | PDF | Endpoint `GET /api/v1/contratos/{id}/pdf` falhava com `500` por cadeia de dependencias inconsistente (Playwright ausente + incompatibilidade WeasyPrint/PyDyf) | Resolvido |
| BUG-029 | Alta | Clientes/Contratos | Duplicidade de cliente por CPF/CNPJ normalizado gerava `500` em `POST /api/v1/contratos` (`MultipleResultsFound`) e quebrava fluxo de fechamento de contrato | Resolvido |
| BUG-030 | Média | Clientes/Contratos | Campo `total_contratos` em `/clientes` ficava desatualizado após excluir contratos, mesmo após sincronização de órfãos | Resolvido |
| BUG-031 | Média | Contratos/Layout | Cabeçalho institucional do contrato estava com logo desatualizada/arte inadequada para faixa azul no preview e nos geradores de PDF, divergindo da marca oficial `logo2.png` | Resolvido |
| BUG-032 | Alta | Contratos/CADIN | Texto jurídico do CADIN estava incompleto (cláusulas ausentes) e com perda de acentuação no preview/PDF/template, divergindo do `cadinpfpjmodelo.docx` | Resolvido |
| BUG-033 | Alta | Contratos/Layout | Texto do preview de contrato apresentou caracteres corrompidos de acentuação (mojibake), afetando leitura jurídica e identidade visual | Resolvido |
| BUG-034 | Baixa | Contratos/Layout | Campo `local_assinatura` legado (ex.: texto com encoding quebrado) ainda aparecia quebrado no rodapé da assinatura em preview/PDF | Resolvido |

---

## Workarounds Ativos

- Autenticação em dev aceita senha `1234` (`security_stub.py`)
- PDF via browser print no frontend (`frontend/src/lib/pdf.ts`)
- Download de PDF pelo backend reabilitado em `GET /api/v1/contratos/{id}/pdf`

---

## Validacao Read-only (2026-02-08)

- `BUG-013`: validado com `POST /api/v1/viva/chat` usando `prompt_extra` longo; endpoint respondeu `200` e retornou `resposta` + `midia`, sem `StackOverflowError`.
- `BUG-014`: validado com `POST /api/v1/viva/vision/upload` enviando arquivo `image/png`; endpoint respondeu `200` com análise da imagem.
- `BUG-017`: validado com autenticação real e chamadas `GET /api/v1/whatsapp-chat/status` e `GET /api/v1/whatsapp-chat/conversas`; ambos `200`.
- `BUG-019`: validação por código + endpoint:
  - front usa `api` compartilhada (`frontend/src/lib/api.ts`) com `access_token`;
  - `/whatsapp/conversas` consome rotas relativas (`/whatsapp-chat/*`) sem URL hardcoded local no arquivo da página.
- `BUG-025`: validado com `POST /api/v1/contratos` (`template_id=bacen`) retornando `200` após fallback de template + correção de numeração.
- `BUG-027`: validado com criação de contrato e consulta `GET /api/v1/clientes?search=...`; cliente foi criado/vinculado automaticamente.
- `BUG-028`: validado com nova criação de contrato sem colisão de índice único (`CNT-2026-0006` criado com sucesso).
- `BUG-026`: validado com autenticacao real em `GET /api/v1/contratos/{id}/pdf`; retorno `200`, `Content-Type: application/pdf` e bytes iniciando com `%PDF-`.
- `BUG-029`: validado em 2026-02-09 com:
  - `GET /api/v1/clientes/documento/334.292.588-47` retornando `200`;
  - `POST /api/v1/contratos` com CPF duplicado historico retornando `201` (sem `500`);
  - `POST /api/v1/clientes` para mesmo CPF retornando `409`;
  - `POST /api/v1/clientes/deduplicar-documentos` executado com sucesso e base saneada para 1 cliente por CPF/CNPJ.
- `BUG-030`: validado em 2026-02-09 com:
  - exclusão real de contrato e atualização imediata de `total_contratos` no cliente vinculado;
  - `POST /api/v1/clientes/sincronizar-contratos` retornando `clientes_recalculados` e reconciliando cache x contagem real;
  - consulta SQL de conferência (`cache == real`) para os clientes ativos.
- `BUG-031`: validado em 2026-02-09 com:
  - troca da marca para `logo2.png` no preview (`/contratos/[id]`);
  - troca da marca para `logo2.png` na geração PDF frontend (`frontend/src/lib/pdf.ts`);
  - troca da marca para `logo2.png` na geração PDF backend (`backend/app/services/pdf_service_playwright.py`).
- `BUG-032`: validado em 2026-02-09 com:
  - cláusulas 1ª a 5ª completas no preview (`/contratos/[id]`) para template CADIN;
  - texto com acentuação correta no PDF frontend (`frontend/src/lib/pdf.ts`) e backend (`backend/app/services/pdf_service_playwright.py`);
  - `contratos/templates/cadin.json` alinhado ao conteúdo jurídico da fonte DOCX.
- `BUG-033`: validado em 2026-02-09 com:
  - preview de contrato sem mojibake (acentuação correta em cabeçalho, cláusulas e dados das partes);
  - geração de PDF frontend e backend com acentuação correta e sem caracteres quebrados;
  - aumento leve de escala visual do layout para melhor legibilidade.
- `BUG-034`: validado em 2026-02-09 com:
  - preview (`/contratos/[id]`) normalizando `local_assinatura` legado no rodapé da assinatura;
  - PDF frontend (`frontend/src/lib/pdf.ts`) normalizando `local_assinatura` antes de montar HTML;
  - PDF backend (`backend/app/services/pdf_service_playwright.py`) normalizando `local_assinatura` no render Playwright.
  - cadastro de novo contrato (`/contratos/novo`) persistindo `Ribeirao Preto/SP` como valor padrão correto.

---

## Bugs Resolvidos (Resumo)

| ID | Módulo | Descrição | Data |
|---|---|---|---|
| BUG-001 | Backend | DATABASE_URL não exportado | 2026-02-03 |
| BUG-002 | Frontend | `output: 'export'` quebrava dev | 2026-02-03 |
| BUG-003 | Backend | Pydantic incompatível | 2026-02-03 |
| BUG-004 | Auth | bcrypt 72 bytes no Windows | 2026-02-03 |
| BUG-005 | API | Import `require_admin` faltando | 2026-02-03 |
| BUG-006 | PDF | WeasyPrint sem GTK+ | 2026-02-03 |
| BUG-007 | Templates | Path em Windows | 2026-02-03 |
| BUG-008 | Frontend | Erros de API sem tratamento | 2026-02-03 |
| BUG-009 | UI | Badge e Tabs faltando | 2026-02-03 |
| BUG-011 | DB | JSONB/UUID incompatível | 2026-02-03 |
| BUG-010 | PDF | Bloqueio de GTK+ no host Windows mitigado com runtime containerizado | 2026-02-07 |
| BUG-013 | VIVA | Prompt extra longo em geração de imagem não derruba mais o fluxo com stack overflow | 2026-02-07 |
| BUG-014 | VIVA | Upload PNG em visão estabilizado sem fallback forçado para JPEG | 2026-02-07 |
| BUG-017 | WhatsApp Chat API | Endpoints `whatsapp-chat` estabilizados sem 500 por enum/schema | 2026-02-07 |
| BUG-018 | WhatsApp Evolution | Instância e chave divergentes geravam falso desconectado | 2026-02-07 |
| BUG-019 | Frontend WhatsApp | Chat de conversas passou a usar token/baseURL corretos via cliente HTTP compartilhado | 2026-02-07 |
| BUG-020 | Webhook WhatsApp | Resposta da VIVA não era enviada (TODO removido e envio ativo) | 2026-02-07 |
| BUG-021 | Webhook WhatsApp | Transcrição de áudio estabilizada no fluxo ativo da VIVA (OpenAI) | 2026-02-07 |
| BUG-022 | Webhook WhatsApp | Blindagem contra resposta vazia e JID não entregável (`exists:false`) | 2026-02-07 |
| BUG-023 | VIVA/OpenAI | Removido override vazio de `OPENAI_API_KEY` no compose | 2026-02-07 |
| BUG-024 | VIVA/OpenAI | Ajustado payload OpenAI Images sem `response_format` incompatível | 2026-02-07 |
| BUG-025 | Contratos | Criação de contrato estabilizada com fallback de template e numeração segura | 2026-02-07 |
| BUG-026 | PDF | Endpoint `/contratos/{id}/pdf` estabilizado com fallback Playwright->WeasyPrint e pin de `pydyf==0.10.0` | 2026-02-08 |
| BUG-027 | Clientes/Contratos | Reativado vínculo automático cliente<->contrato e endpoint de sincronização de órfãos | 2026-02-07 |
| BUG-028 | Contratos | Numeração alterada para sequência por maior número do ano (sem colisão por gaps) | 2026-02-07 |
| BUG-029 | Clientes/Contratos | Unicidade por CPF/CNPJ normalizado estabilizada com saneamento de duplicados e fim do `500` na criação de contrato | 2026-02-09 |
| BUG-030 | Clientes/Contratos | Recalculo de métricas de clientes após exclusão de contrato e sincronização global de contagens | 2026-02-09 |
| BUG-031 | Contratos/Layout | Marca oficial `logo2.png` padronizada no preview e nos pipelines de PDF | 2026-02-09 |
| BUG-032 | Contratos/CADIN | Texto do CADIN alinhado ao modelo oficial (cláusulas completas + acentuação) em preview/PDF/template | 2026-02-09 |
| BUG-033 | Contratos/Layout | Correção de acentuação corrompida (mojibake) + ajuste leve de escala visual no preview/PDF | 2026-02-09 |
| BUG-034 | Contratos/Layout | Normalização de `local_assinatura` legado para evitar texto corrompido no rodapé da assinatura (preview + PDF frontend/backend) | 2026-02-09 |

---

*Atualizado em: 2026-02-09*


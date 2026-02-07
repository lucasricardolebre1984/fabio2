# BUGSREPORT - Registro de Bugs

> **Projeto:** FC Soluções Financeiras SaaS  
> **Última Atualização:** 2026-02-07

---

## Bugs Ativos

| ID | Severidade | Módulo | Descrição | Status |
|---|---|---|---|---|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Aguardando instalação GTK+ |
| BUG-012 | Média | VIVA | Botão de áudio no chat não funciona | Ativo |
| BUG-013 | Média | VIVA | Erro `StackOverflowError` ao gerar imagem com prompt extra longo (REZETA/FC) | Ativo |
| BUG-014 | Média | VIVA | Upload de imagem falha quando a imagem é PNG (MIME assumido como JPEG) | Ativo |
| BUG-015 | Alta | VIVA | Fundo da imagem não respeita paleta/brief do prompt (resultado genérico) | Ativo |
| BUG-016 | Média | VIVA | Arte final perde partes do texto (overlay truncado) | Ativo |
| BUG-017 | Alta | WhatsApp Chat API | Endpoints `/api/v1/whatsapp-chat/*` retornam 500 por incompatibilidade de modelagem (`SQLEnum`) com schema real (`VARCHAR`) | Ativo |
| BUG-018 | Alta | WhatsApp Evolution | Backend consulta instância/chave divergentes do runtime (instância ativa `Teste`), causando falso desconectado (`Status 404`) | Resolvido |
| BUG-019 | Média | Frontend WhatsApp | `/whatsapp/conversas` usa token incorreto (`localStorage.token`) e base URL hardcoded em `localhost:8000` | Ativo |
| BUG-020 | Alta | Webhook WhatsApp | Resposta da VIVA não é enviada ao WhatsApp no webhook (envio real marcado como TODO) | Resolvido |
| BUG-021 | Alta | Webhook WhatsApp | Mensagem de áudio recebida no WhatsApp não era transcrita para o fluxo da VIVA (áudio obrigatório) | Em validação |
| BUG-022 | Média | Webhook WhatsApp | Intermitência de envio (`400 Text is required` e `exists:false`) por payload vazio/JID não entregável no retorno da IA | Resolvido |

---

## Workarounds Ativos

- Autenticação em dev aceita senha `1234` (`security_stub.py`)
- PDF via browser print no frontend (`frontend/src/lib/pdf.ts`)

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
| BUG-018 | WhatsApp Evolution | Instância e chave divergentes geravam falso desconectado | 2026-02-07 |
| BUG-020 | Webhook WhatsApp | Resposta da VIVA não era enviada (TODO removido e envio ativo) | 2026-02-07 |
| BUG-022 | Webhook WhatsApp | Blindagem contra resposta vazia e JID não entregável (`exists:false`) | 2026-02-07 |

---

*Atualizado em: 2026-02-07*

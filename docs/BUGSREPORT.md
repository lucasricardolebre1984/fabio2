# BUGSREPORT - Registro de Bugs

> **Projeto:** FC Soluções Financeiras SaaS  
> **Última Atualização:** 2026-02-05

---

## Bugs Ativos

| ID | Severidade | Módulo | Descrição | Status |
|---|---|---|---|---|
| BUG-010 | Baixa | PDF | WeasyPrint requer GTK+ no Windows | Aguardando instalação GTK+ |
| BUG-012 | Média | VIVA | Botão de áudio no chat não funciona | Ativo |
| BUG-013 | Média | VIVA | Erro `StackOverflowError` ao gerar imagem com prompt extra longo (REZETA/FC) | Ativo |
| BUG-014 | Média | VIVA | Upload de imagem falha quando a imagem é PNG (MIME assumido como JPEG) | Ativo |

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

---

*Atualizado em: 2026-02-05*

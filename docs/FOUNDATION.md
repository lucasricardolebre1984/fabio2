# FOUNDATION - Regras Operacionais

> **Projeto:** FC Soluções Financeiras SaaS  
> **Data:** 2026-02-05

---

## Princípios

- Documentação reflete o código real
- Nenhuma alteração em produção sem aprovação
- Não expor segredos em logs ou docs
- Não commitar `.env`

---

## Gates de Segurança

- Alterações de código exigem aprovação explícita
- Commit e push somente com autorização
- Operações destrutivas exigem aprovação dupla

---

## Padrões de Comunicação

- Respostas em pt-BR
- Evidências sempre que possível (logs, diffs, comandos)

---

## Protocolo Operacional DEV DEUS (GODMOD)

Fluxo institucional obrigatório para qualquer mudança:

1. Mapeamento (read-only)
2. Diagnóstico com evidências
3. Arquitetura proposta
4. Aprovação explícita
5. Execução em passos atômicos
6. Versionamento + documentação

Regras complementares:
- Operar em `main` (sem branch paralela)
- Toda alteração deve atualizar `docs/STATUS.md`, `docs/DECISIONS.md` e `docs/SESSION.md`
- Toda entrega deve conter plano de rollback explícito
- Commit e push apenas com autorização explícita

---

## Padrões Técnicos

- API base: `/api/v1`
- Auth: JWT Bearer
- PDF: impressão via browser
- VIVA: OpenAI como provedor institucional, com fallback local

---

*Documento atualizado em: 2026-02-05*

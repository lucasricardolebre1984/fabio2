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

## Padrões Técnicos

- API base: `/api/v1`
- Auth: JWT Bearer
- PDF: impressão via browser
- VIVA: Z.AI com fallback para OpenRouter ou modo local

---

*Documento atualizado em: 2026-02-05*

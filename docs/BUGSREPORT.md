# BUGSREPORT - Registro de Bugs

> **Projeto:** FC Soluções Financeiras SaaS  
> **Protocolo:** Registrar antes de corrigir | Evidência obrigatória  
> **Última Atualização:** 2026-02-03  

---

## 🐛 Bugs Ativos

| ID | Severidade | Módulo | Descrição | Status |
|----|-----------|--------|-----------|--------|
| - | - | - | Nenhum bug ativo | - |

---

## ✅ Bugs Resolvidos

| ID | Severidade | Módulo | Descrição | Resolução | Data |
|----|-----------|--------|-----------|-----------|------|
| BUG-001 | Alta | Backend/Setup | DATABASE_URL não exportado | Adicionado export em app/db/session.py | 2026-02-03 |
| BUG-002 | Média | Frontend/Build | `output: 'export'` quebrava dev server | Removido do next.config.js | 2026-02-03 |
| BUG-003 | Média | Backend/Deps | pydantic 2.5.3 incompatível com pydantic-settings | Atualizado para pydantic 2.7.0 | 2026-02-03 |

---

## 📝 BUG-001: ImportError DATABASE_URL (RESOLVIDO)

### Descrição
O script `init_db.py` falha ao tentar importar `DATABASE_URL` de `app.db.session`, pois a variável não está exportada no módulo.

### Resolução
Adicionado export no `app/db/session.py`:
```python
DATABASE_URL = settings.DATABASE_URL
```

Scripts atualizados:
- `init_db.py` - Cria tabelas e usuário
- `criar_usuario.py` - Cria usuário apenas

### Data da Resolução
2026-02-03

---

## 📝 BUG-002: next.config.js output export (RESOLVIDO)

### Descrição
Configuração `output: 'export'` no next.config.js impede o funcionamento do modo desenvolvimento.

### Resolução
Removido `output: 'export'` e `distDir: 'dist'` do arquivo `frontend/next.config.js`.

---

## 📝 BUG-003: pydantic vs pydantic-settings (RESOLVIDO)

### Descrição
Incompatibilidade entre pydantic 2.5.3 e pydantic-settings 2.2.1.

### Resolução
Atualizado `requirements.txt`:
- pydantic: 2.5.3 → 2.7.0
- Adicionado: pydantic-settings==2.2.1

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de Bugs | 3 |
| Ativos | 1 |
| Críticos | 0 |
| Resolvidos | 2 |
| Média de Resolução | 1 dia |

---

*Atualizado em: 2026-02-03*

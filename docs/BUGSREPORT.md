# BUGSREPORT - Registro de Bugs

> **Projeto:** FC Soluções Financeiras SaaS  
> **Protocolo:** Registrar antes de corrigir | Evidência obrigatória  
> **Última Atualização:** 2026-02-03  

---

## 🐛 Bugs Ativos

| ID | Severidade | Módulo | Descrição | Status |
|----|-----------|--------|-----------|--------|
| BUG-001 | Alta | Backend/Setup | ImportError: DATABASE_URL não exportado em app.db.session | 🔵 Análise |
| BUG-002 | Média | Frontend/Build | Configuração `output: 'export'` incompatível com modo dev | 🔵 Análise |
| BUG-003 | Média | Backend/Deps | Incompatibilidade pydantic 2.5.3 vs pydantic-settings | 🔵 Análise |

---

## ✅ Bugs Resolvidos

| ID | Severidade | Módulo | Descrição | Resolução | Data |
|----|-----------|--------|-----------|-----------|------|
| BUG-003 | Média | Backend/Deps | pydantic 2.5.3 incompatível com pydantic-settings | Atualizado para pydantic 2.7.0 | 2026-02-03 |
| BUG-002 | Média | Frontend/Build | `output: 'export'` quebrava dev server | Removido do next.config.js | 2026-02-03 |

---

## 📝 BUG-001: ImportError DATABASE_URL

### Descrição
O script `init_db.py` falha ao tentar importar `DATABASE_URL` de `app.db.session`, pois a variável não está exportada no módulo.

### Passos para Reproduzir
1. Tentar executar `python init_db.py`
2. Erro: `ImportError: cannot import name 'DATABASE_URL'`

### Comportamento Esperado
Script deve importar configurações do banco e criar tabelas

### Comportamento Atual
```
ImportError: cannot import name 'DATABASE_URL' from 'app.db.session'
```

### Ambiente
- OS: Windows 11
- Python: 3.11
- Commit: bf3622e

### Causa Raiz
O arquivo `app/db/session.py` não exporta a constante `DATABASE_URL`, apenas `engine` e `AsyncSessionLocal`.

### Fix Proposto
Adicionar export no `app/db/session.py`:
```python
from app.config import settings
DATABASE_URL = settings.DATABASE_URL
```

Ou alterar o script para importar de `app.config`:
```python
from app.config import settings
DATABASE_URL = settings.DATABASE_URL
```

### Workaround
Criar usuário manualmente via SQL ou endpoint direto no backend.

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

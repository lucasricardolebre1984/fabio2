# PLAYBOOK - SUBIR NOVOS MODELOS DE CONTRATO (.md)

> Projeto: FC Solucoes Financeiras SaaS  
> Status: Ativo  
> Ultima atualizacao: 2026-02-11  
> Objetivo: padronizar 100% o processo de entrada de novos modelos para evitar drift, regressao e erro de encoding.

---

## 1. Escopo deste playbook

Este documento define o metodo oficial para transformar um modelo de contrato em `.md` em modulo funcional no SaaS, com cobertura completa:

1. Menu de contratos
2. Criacao (`/contratos/novo`)
3. Preview (`/contratos/[id]`)
4. PDF frontend (`frontend/src/lib/pdf.ts`)
5. PDF backend (`backend/app/services/pdf_service_playwright.py`)
6. Template JSON (`contratos/templates/*.json`)

Sem este fluxo completo, o modelo e considerado incompleto.

---

## 2. Pre-condicoes obrigatorias

Antes de codar:

1. Ler `AGENTS.md`
2. Ler `docs/BUGSREPORT.md`
3. Ler `docs/CONTRATOS/CAMPOS_BACEN.md` e `docs/CONTRATOS/CAMPOS_CADIN.md`
4. Ler este playbook inteiro

Regra institucional:

1. Registrar bug/ajuste em `docs/BUGSREPORT.md` antes da correcao
2. Atualizar status do bug na mesma entrega

---

## 3. Entrada canonica do modelo

Formato de entrada recomendado: `.md` (nao `docx`).

Checklist do arquivo de origem:

1. Nome do servico
2. Clausulas completas e numeradas
3. Campos variaveis (nome, documento, valores, prazos, etc.)
4. Regras comerciais (multa, juros, rescisao, foro, LGPD)

Regra de encoding:

1. Sempre salvar conteudo em UTF-8
2. Nao copiar texto quebrado por encoding (acentos com caracteres lixo)

---

## 4. Implementacao - passos tecnicos obrigatorios

## 4.1 Criar template JSON

Arquivo:

1. `contratos/templates/<id_template>.json`

Regras:

1. `id` em minusculo (ex.: `cnh`, `serasa_pf`, `protesto_pj`)
2. `tipo` coerente com o fluxo de render
3. `campos` e `secoes` preenchidos
4. Incluir campos extras em `dados_extras` quando necessario

---

## 4.2 Habilitar fallback backend

Arquivo:

1. `backend/app/services/contrato_service.py`

Acao:

1. Adicionar o novo `id` em `FALLBACK_TEMPLATES`

Objetivo:

1. Evitar quebra de criacao de contrato se seed/base nao tiver sido carregada

---

## 4.3 Habilitar menu de contratos

Arquivo:

1. `frontend/src/app/(dashboard)/contratos/page.tsx`

Acao:

1. Adicionar card ativo do novo modelo (id, nome, categoria, descricao, icone)

---

## 4.4 Habilitar criacao do contrato

Arquivo:

1. `frontend/src/app/(dashboard)/contratos/novo/page.tsx`

Acoes minimas:

1. Incluir `template` no seletor de `selectedTemplate`
2. Definir `tituloTemplate` do novo modelo
3. Adicionar campos especificos no `formData` (se houver)
4. Enviar estes campos em `dados_extras` no payload

---

## 4.5 Habilitar preview institucional

Arquivo:

1. `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`

Acoes minimas:

1. Detectar `templateId` do novo modelo
2. Definir `subtitle` correto do contrato
3. Renderizar clausulas especificas do modelo
4. Exibir campos extras (quando aplicavel)

---

## 4.6 Habilitar PDF frontend

Arquivo:

1. `frontend/src/lib/pdf.ts`

Acoes minimas:

1. Detectar `templateId`
2. Definir subtitulo correto
3. Definir bloco `clausesHtml` do novo modelo
4. Manter cabecalho/rodape institucional padrao

---

## 4.7 Habilitar PDF backend

Arquivo:

1. `backend/app/services/pdf_service_playwright.py`

Acoes minimas:

1. Detectar `template_id`
2. Definir `subtitle` do modelo
3. Definir bloco de clausulas HTML do modelo
4. Exibir campos extras no box CONTRATANTE (se houver)
5. Manter layout institucional padrao

---

## 5. Regra critica de acentuacao (anti-mojibake)

Arquivos sensiveis:

1. `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
2. `frontend/src/lib/pdf.ts`
3. `backend/app/services/pdf_service_playwright.py`

Gate de qualidade:

1. Nao pode existir mojibake visual no preview/PDF
2. Nao pode existir string com padrao quebrado (acentos com caracteres lixo)
3. Todo texto final deve sair em UTF-8 legivel

---

## 6. Validacao tecnica obrigatoria

Executar nesta ordem:

1. `python -m py_compile backend/app/services/contrato_service.py backend/app/services/pdf_service_playwright.py`
2. `cd frontend && npm run type-check`
3. `cd frontend && npm run lint -- --file "src/app/(dashboard)/contratos/page.tsx" --file "src/app/(dashboard)/contratos/novo/page.tsx" --file "src/app/(dashboard)/contratos/[id]/page.tsx" --file "src/lib/pdf.ts"`

Observacao:

1. Warning antigo nao bloqueante pode existir
2. Erro de tipo/sintaxe e bloqueante

---

## 7. Validacao funcional obrigatoria

Checklist manual:

1. Abrir `/contratos` e confirmar card do modelo
2. Criar contrato em `/contratos/novo?template=<id>`
3. Verificar preview com texto correto
4. Gerar PDF pelo frontend e validar acentuacao
5. Gerar PDF backend (rota de contrato/pdf) e validar acentuacao

Critico:

1. Preview e PDF precisam estar semanticamente iguais
2. Nao pode haver clausula faltando entre preview e PDF

---

## 8. Encerramento da entrega

Passos finais obrigatorios:

1. Atualizar `docs/BUGSREPORT.md` (bug + status)
2. Atualizar `docs/SESSION.md` (resumo tecnico da rodada)
3. Atualizar `docs/STATUS.md` (estado atual)
4. Commit com mensagem objetiva
5. Push para `main` (quando aprovado)

---

## 9. Checklist rapido para qualquer agente

1. Recebi modelo `.md`
2. Criei `contratos/templates/<id>.json`
3. Atualizei `FALLBACK_TEMPLATES`
4. Ativei menu `/contratos`
5. Ativei fluxo `/contratos/novo`
6. Ativei preview `/contratos/[id]`
7. Ativei PDF frontend
8. Ativei PDF backend
9. Validei encoding UTF-8
10. Rodei `py_compile + type-check + lint`
11. Documentei em `BUGSREPORT + SESSION + STATUS`
12. Commit/push

Se qualquer item falhar, nao liberar o modelo.

# DECISIONS - Decisões Arquiteturais

## Data: 2026-02-03
## Projeto: FC Soluções Financeiras SaaS

---

## DECISÃO-001: Sistema de Contratos Dinâmicos com Templates

### Contexto
O sistema precisa suportar múltiplos tipos de contratos pré-definidos (Bacen, Serasa, etc.) com layout institucional fixo, mas campos variáveis que são preenchidos dinamicamente.

### Requisitos do Negócio
1. **Menu Contratos**: Exibir cards/tiles dos tipos de contratos disponíveis
2. **Seleção**: Ao clicar em um tipo (ex: Bacen), abrir o contrato no layout institucional
3. **Preenchimento Dinâmico**:
   - Campos entre `[COLCHETES]` = input do usuário
   - Campos entre `(PARÊNTESES)` = calculados automaticamente (extenso)
4. **Preview em Tempo Real**: Enquanto digita, o contrato atualiza os valores
5. **Salvamento**: Salva o contrato e cadastra o cliente automaticamente
6. **Menu Clientes**: Mostra histórico de contratos do cliente

### Arquitetura Proposta

#### Estrutura de Templates
```
contratos/templates/
├── bacen.json              # Template Bacen
├── serasa.json             # Template Serasa (futuro)
├── protesto.json           # Template Protesto (futuro)
└── _layout-institutional/  # Componentes de layout reusáveis
```

#### Formato do Template (JSON)
```json
{
  "id": "bacen",
  "nome": "Contrato Bacen - Remoção SCR",
  "categoria": "Bacen",
  "descricao": "Remoção de apontamentos no Sistema de Informações de Crédito",
  "layout": "institucional",  // Referencia o layout base
  "campos": [
    {
      "nome": "contratante_nome",
      "label": "Nome Completo",
      "tipo": "texto",
      "placeholder": "João da Silva",
      "secao": "dados_contratante",
      "obrigatorio": true
    },
    {
      "nome": "valor_total",
      "label": "Valor Total",
      "tipo": "moeda",
      "secao": "valores",
      "obrigatorio": true,
      "calcula_extenso": "valor_total_extenso"
    }
  ],
  "clausulas": [
    {
      "numero": "PRIMEIRA",
      "titulo": "DO OBJETO",
      "conteudo": "O presente contrato tem como objeto...",
      "variaveis": []  // Se houver variáveis específicas na cláusula
    }
  ],
  "preview_config": {
    "orientacao": "portrait",  // portrait | landscape
    "margens": {"topo": 30, "direita": 25, "fundo": 30, "esquerda": 25},
    "fonte_principal": "Times New Roman",
    "tamanho_fonte": 12,
    "cor_fonte": "#000000"
  }
}
```

#### Fluxo de Uso
```
┌─────────────────────────────────────────────────────────────────┐
│  MENU CONTRATOS                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │  BACEN   │  │ SERASA   │  │ PROTESTO │  ...                  │
│  │ [Imagem] │  │ [Imagem] │  │ [Imagem] │                       │
│  │ Clique   │  │ Clique   │  │ Clique   │                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  EDITOR DE CONTRATO                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [CABEÇALHO INSTITUCIONAL COM LOGO]                       │  │
│  │                                                           │  │
│  │  DADOS DO CONTRATANTE:                                   │  │
│  │  Nome: [____________________]                           │  │
│  │  CPF:   [____________________]                           │  │
│  │                                                           │  │
│  │  VALORES:                                                │  │
│  │  Total: R$ [________] (calcula extenso automaticamente)  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  [SALVAR] ──► Salva contrato + cadastra cliente                │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes de Layout

#### Cabeçalho Institucional (Reutilizável)
```
┌─────────────────────────────────────────────────────────────────┐
│  [LOGO FC]  FC SOLUÇÕES FINANCEIRAS                    Tel:... │
│             CNPJ: 57.815.628/0001-62                            │
│             Endereço completo...                                │
├─────────────────────────────────────────────────────────────────┤
│              CONTRATO DE PRESTAÇÃO DE SERVIÇOS                  │
│                       Bacen - Remoção SCR                       │
└─────────────────────────────────────────────────────────────────┘
```

### Alternativas Consideradas

| Alternativa | Prós | Contras |
|-------------|------|---------|
| **A: PDF editável** | Formato final imediato | Difícil preview dinâmico, UX ruim |
| **B: Word DOCX** | Familiar para usuários | Complexo editar no browser |
| **C: HTML Dinâmico (Escolhida)** | Preview em tempo real, fácil gerar PDF | Requer desenvolvimento inicial |

**Decisão:** Implementar solução C (HTML Dinâmico) por melhor UX e facilidade de manutenção.

---

## DECISÃO-002: Geração de PDF - Browser Print vs Backend

### Contexto
Após tentativas frustradas com bibliotecas backend (WeasyPrint, Playwright), foi necessário escolher uma solução robusta para geração de PDF.

### Problemas Encontrados

| Biblioteca | Problema |
|------------|----------|
| **WeasyPrint** | Requer GTK+ no Windows - instalação complexa |
| **Playwright** | `NotImplementedError: subprocess_exec` no Windows asyncio |
| **Puppeteer** | Mesmo problema de subprocess no Windows |

### Solução Escolhida: Browser Print (Frontend)

**Arquitetura:**
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │     │  Nova Janela     │     │  PDF Gerado     │
│  (Next.js)      │────►│  (HTML Puro)     │────►│  (Browser Print)│
│                 │     │                  │     │                 │
│ generatePDF()   │     │ window.print()   │     │ Save as PDF     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

**Vantagens:**
- ✅ Funciona em qualquer sistema operacional
- ✅ Layout idêntico entre visualização e impressão
- ✅ Controle total do CSS/HTML
- ✅ Não requer instalação de dependências pesadas
- ✅ Preview imediato antes de salvar

**Desvantagens:**
- ⚠️ Requer ação do usuário para salvar
- ⚠️ Popups devem estar permitidos

**Decisão:** Implementar geração de PDF via browser print (frontend).

---

## DECISÃO-003: Layout Institucional - Cabeçalho e Tipografia

### Contexto
O cabeçalho original continha dados redundantes (CNPJ, endereço, telefone) que já apareciam na seção CONTRATADA.

### Mudanças Realizadas

#### 1. Fonte
- **Anterior:** Inter (sans-serif) - padrão Tailwind
- **Nova:** Times New Roman (serif) - fonte institucional tradicional

#### 2. Cabeçalho
- **Anterior:** Logo + dados completos da empresa (redundante)
- **Novo:** Faixa azul (#1e3a5f) com logo SVG + nome da empresa

```
ANTES:
┌──────────────────────────────────────────────────────────────┐
│  [FC]  FC SOLUÇÕES FINANCEIRAS                      Tel:...  │
│        CNPJ: 57.815.628/0001-62                              │
│        Rua Maria das Graças...                               │
│        contato@...                                           │
└──────────────────────────────────────────────────────────────┘

NOVO:
┌──────────────────────────────────────────────────────────────┐
│██████████████████████████████████████████████████████████████│
│█  [⚖️]  F C Soluções Financeiras                            █│
│██████████████████████████████████████████████████████████████│
└──────────────────────────────────────────────────────────────┘
```

### Motivação
1. **Eliminar redundância:** Dados da empresa aparecem na seção CONTRATADA
2. **Visual institucional:** Faixa azul é mais profissional
3. **Economia de espaço:** Mais espaço para o conteúdo do contrato
4. **Consistência:** Mesmo layout em visualização e PDF

### Arquivos Afetados
- `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
- `frontend/src/lib/pdf.ts`

---

*Documentado em: 2026-02-03*  
*Autor: Lucas Lebre (Automania-AI)*  
*Aprovado por: Fábio (FC Soluções Financeiras)*

---

## DECISÃO-004: Modelos Z.AI e Fallback para VIVA

### Contexto
O sistema passou a operar com IA VIVA no chat interno e no fluxo WhatsApp. Era necessário definir modelos oficiais e estabelecer fallback quando a API principal não estiver disponível.

### Opções consideradas
A. Z.AI como principal (GLM-4.7 e modelos multimodais)
B. OpenRouter como principal (modelos gratuitos)
C. Modo local com templates (sem API)

### Decisão
- **Principal:** Z.AI com os modelos oficiais
- **Fallback:** OpenRouter quando disponível
- **Fallback final:** modo local com templates

### Modelos Oficiais
- Chat: `GLM-4.7`
- Visão: `GLM-4.6V`
- Imagem: `GLM-Image`
- Áudio: `GLM-ASR-2512`
- Vídeo: `CogVideoX-3`

### Motivo
- Z.AI cobre chat e multimodal com consistência
- OpenRouter garante operação gratuita quando necessário
- Modo local evita indisponibilidade total

---

*Documentado em: 2026-02-05*

---

## DECISÃO-005: Persona simples da VIVA no prompt principal

### Contexto
O chat interno precisava reconhecer o contexto do servidor e as capacidades multimodais, sem depender de prompts longos ou específicos.

### Decisão
Adicionar uma persona simples no prompt principal da VIVA informando:
- Contexto do servidor (SaaS interno)
- Empresas (FC Soluções e RezetaBrasil)
- Capacidades (chat, imagens, visão, áudio, vídeo)

### Motivo
- Reduz alucinação sobre limitações
- Melhora a compreensão do ambiente
- Facilita uso com prompts secundários

---

*Documentado em: 2026-02-05*

---

## DECISÃO-006: Roteamento de intenção de imagem no backend

### Contexto
O chat interno precisava gerar imagens quando solicitado, sem duplicar regras no frontend.

### Decisão
Centralizar a detecção de intenção de imagem no backend (`/viva/chat`) e retornar mídia estruturada.

### Motivo
- Evita lógica duplicada no frontend
- Permite uso futuro no WhatsApp e outros canais
- Mantém governança e consistência institucional

---

*Documentado em: 2026-02-05*

---

## DECISÃO-007: Pipeline institucional para geração de imagens da VIVA

### Data
2026-02-06

### Contexto
A geração de imagem atual da VIVA estava entregando resultado inconsistente: texto duplicado, overflow visual, baixa aderência ao brief e paleta institucional parcialmente ignorada em campanhas FC/Rezeta.

### Decisão
Adotar pipeline de geração de imagem em duas etapas:
1. **Copy estruturada** (resumo de campanha em formato controlado)
2. **Background fotográfico sem texto/logo**
3. **Composição final institucional** com template fixo por marca

Adicionalmente, padronizar saudação da VIVA com nome do cliente: **"Olá Fabio!"**.

### Motivo
- Evita poluição visual e duplicação de texto
- Garante legibilidade mobile e consistência institucional
- Separa responsabilidade entre IA geradora de fundo e render final de campanha
- Facilita governança de marca para FC e Rezeta

### Rollback
- Estratégia primária: `git revert <hash-da-implementacao>`
- Estratégia de contingência (somente aprovação dupla):
  - `git reset --hard <commit-anterior>`
  - `git push --force origin main`

---

*Documentado em: 2026-02-06*

---

## DECISÃO-008: Estabilização da integração WhatsApp (Evolution v1.8) e conexão definitiva com frontend

### Data
2026-02-07

### Contexto
O diagnóstico operacional identificou que a infraestrutura estava ativa, porém o fluxo funcional estava quebrado por divergência de configuração (instância/chave), contrato de payload defasado com a Evolution v1.8, erro 500 na API de conversas e frontend parcialmente desconectado.

### Decisão
Executar a integração em cinco frentes técnicas, nesta ordem:
1. Alinhar configuração de ambiente (`EVOLUTION_API_KEY`, `WA_INSTANCE_NAME`, webhook da instância).
2. Atualizar `whatsapp_service.py` para o contrato atual da Evolution (`status`, `sendText`, `sendMedia`).
3. Corrigir falha 500 de `/whatsapp-chat/*` por incompatibilidade ORM/schema.
4. Conectar telas `/whatsapp` e `/whatsapp/conversas` com autenticação e API client padrão.
5. Validar fluxo completo com evidências de envio e persistência.

### Motivo
- Remove falso negativo de conexão no backend.
- Elimina regressão de contrato entre backend e Evolution.
- Restabelece confiabilidade da API consumida pelo frontend.
- Fecha o ciclo ponta a ponta (mensagem recebida -> resposta VIVA -> envio real WhatsApp).

### Rollback
- Estratégia primária: `git revert <hash-da-implementacao-whatsapp>`
- Contingência (somente aprovação dupla):
  - `git reset --hard <commit-anterior>`
  - `git push --force origin main`

---

*Documentado em: 2026-02-07*

## DECISÃO-009: pacote definitivo de atendimento WhatsApp da Viviane (Rezeta)

### Data
07/02/2026

### Contexto
O cliente validou em reuniao operacional o modelo final de atendimento para
leads no WhatsApp, com objetivo de elevar conversao sem perder linguagem
humana e controle comercial.

### Decisão
Adotar o seguinte pacote institucional:
- Operacao em Modo B (VIVA conduz quase tudo; humano por excecao).
- Persona fixa: Viviane, consultora de negocios da Rezeta.
- Tom hibrido com respostas naturais e variacao de linguagem.
- Fluxo de qualificacao: objetivo -> perfil -> urgencia -> proximo passo.
- Coleta obrigatoria: nome, telefone, servico, cidade e urgencia.
- SLA 24/7 com callback em ate 15 minutos.
- Diagnostico 360 como recomendacao inicial padrao.
- Excecao de venda direta para Limpa Nome, Score e Rating.
- Oferta inicial com margem de 15% sobre tabela de referencia.
- Negociacao de valor final e descontos somente com atendimento humano.
- Registro obrigatorio de objecao financeira para follow-up.

### Governanca de conhecimento
As fontes oficiais para a V1 ficam versionadas em:
- `frontend/src/app/viva/REGRAS/Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md`
- `frontend/src/app/viva/REGRAS/Tabela Precços IA.xlsx`
- `frontend/src/app/viva/REGRAS/tabela_precos_ia_01_planilha1.csv`

### Motivo
- Aumenta taxa de fechamento com abordagem consultiva e humana.
- Mantem previsibilidade operacional com regras claras de escala.
- Permite manutencao rapida de preco sem refatorar fluxo inteiro.

### Rollback
Se o pacote precisar revisao:
- rollback documental por commit dedicado;
- rollback funcional por `git revert` na implementacao da V1.

---

*Documentado em: 07/02/2026*

## DECISÃO-010: carregamento de regras da Viviane por volume no container

### Data
07/02/2026

### Contexto
A base de regras e precos da Viviane foi definida em
`frontend/src/app/viva/REGRAS`, mas o container do backend nao montava esse
caminho, impedindo leitura em runtime.

### Decisão
- Criar `viva_knowledge_service.py` para ler regras/precos editaveis.
- Montar volume `./frontend/src/app/viva/REGRAS:/app/viva_rules` no backend.
- Definir `VIVA_RULES_DIR=/app/viva_rules` no backend.
- Recarregar regras automaticamente quando arquivos mudarem.

### Motivo
- Permite manutencao continua de valores e roteiro sem rebuild.
- Mantem operacao 100% dentro de container.
- Reduz risco de desvio entre discurso comercial e tabela ativa.

---

*Documentado em: 07/02/2026*

---

## DECISÃO-011: OpenAI como provedor único da VIVA (remoção de Z.AI no runtime)

### Data
07/02/2026

### Contexto
O atendimento WhatsApp e o chat da VIVA estavam com comportamento inconsistente por mistura de provedores, além de falhas em geração de imagem e risco de conflito operacional.

### Decisão
- Padronizar VIVA em **OpenAI-only** no runtime.
- Trocar o roteamento de chat e transcrição para `openai_service`/`viva_model_service`.
- Migrar geração de imagem para OpenAI Images (`OPENAI_IMAGE_MODEL`).
- Migrar análise de imagem (vision) para OpenAI.
- Remover `zai_service.py` do backend ativo.
- Manter fallback local apenas para contingência quando a API externa falhar.

### Ajustes operacionais aplicados
- Variáveis institucionais:
  - `OPENAI_API_KEY`
  - `OPENAI_API_MODEL` (aprovado: `gpt-5-mini`)
  - `OPENAI_AUDIO_MODEL`
  - `OPENAI_IMAGE_MODEL` (default técnico: `gpt-image-1`)
  - `OPENAI_VISION_MODEL`
- Removido override vazio de `OPENAI_API_KEY` no `docker-compose` para não sobrescrever `.env`.

### Motivo
- Elimina conflito entre provedores.
- Mantém previsibilidade do atendimento da Viviane.
- Corrige regressão de imagem e estabiliza áudio no mesmo provedor institucional.

### Rollback
- `git revert <hash-da-migracao-openai>`
- Reintroduzir provedor anterior somente com decisão formal e testes de regressão.

---

*Documentado em: 07/02/2026*

---

## DECISAO-014: estabilizacao do endpoint de PDF de contratos no backend

### Data
08/02/2026

### Contexto
O endpoint `GET /api/v1/contratos/{id}/pdf` estava retornando `500` no
container por combinacao de fatores:
- Playwright ausente no runtime;
- cadeia WeasyPrint/PyDyf incompatível na imagem em uso.

### Decisao
- manter estrategia de fallback no `ContratoService.generate_pdf_bytes`:
  - caminho primario: Playwright;
  - fallback automatico: WeasyPrint.
- fixar dependencia `pydyf==0.10.0` para compatibilidade com `weasyprint==60.2`.
- registrar logs tecnicos de fallback para diagnostico operacional.

### Motivo
- remove erro `500` no download de PDF sem travar operacao de contratos;
- evita dependencia unica de Playwright em ambiente de container;
- preserva compatibilidade com fluxo atual de browser print no frontend.

### Rollback
- `git revert <hash-da-decisao-014>`
- opcional emergencial:
  - restaurar comportamento anterior somente se validado em homologacao;
  - manter browser print como contingencia no frontend.

---

*Documentado em: 08/02/2026*

---

## DECISAO-013: fechamento de clientes/agenda minimo funcional e sincronizacao contratos->clientes

### Data
07/02/2026

### Contexto
Durante homologacao com cliente, foram identificados tres pontos operacionais:
- contratos criados nem sempre apareciam na base de clientes;
- tela de clientes precisava cadastro manual imediato;
- agenda estava sem operacao minima e sem atalho via chat interno da VIVA.

### Decisao
- Backend:
  - reforcar criacao/vinculo de cliente no `ContratoService.create`;
  - adicionar sincronizacao de contratos orfaos em `ClienteService.sync_from_contracts`;
  - expor endpoint `POST /api/v1/clientes/sincronizar-contratos`;
  - ajustar numeração de contrato por maior sequencial do ano (evita colisao por gaps).
- Frontend:
  - substituir placeholders de `clientes` e `agenda` por CRUD minimo funcional.
- VIVA interna:
  - habilitar comando de agenda no chat `/viva/chat`:
    - `agendar TITULO | DD/MM/AAAA HH:MM | descricao opcional`

### Motivo
- restabelecer fluxo comercial sem retrabalho manual;
- garantir visibilidade dos clientes derivados de contratos;
- entregar agenda operavel sem depender de nova rodada de arquitetura.

### Rollback
- `git revert <hash-da-decisao-013>`
- se necessario, rollback pontual por arquivo:
  - `backend/app/services/contrato_service.py`
  - `backend/app/services/cliente_service.py`
  - `frontend/src/app/(dashboard)/clientes/page.tsx`
  - `frontend/src/app/(dashboard)/agenda/page.tsx`

---

*Documentado em: 07/02/2026*

---

## DECISÃO-012: Governança operacional do Evolution API para produção local estável

### Data
07/02/2026

### Contexto
Durante a homologação com cliente, o comportamento intermitente do WhatsApp exigiu padronização do processo no Evolution Manager para evitar conflito de automação, QR inconsistente e eventos desnecessários.

### Decisão
- Manter a automação da VIVA exclusivamente no backend FastAPI.
- No Evolution Manager, manter integrações nativas (`OpenAI`, `Typebot`, `Dify`, `Flowise`, `Chatwoot`) desativadas para este fluxo.
- Webhook institucional único:
  - URL: `http://backend:8000/api/v1/webhook/evolution`
  - `Webhook por Eventos`: OFF
  - `Webhook Base64`: ON
  - Eventos ativos: `MESSAGES_UPSERT`, `CONNECTION_UPDATE`
- Instância oficial única para operação: `fc-solucoes`.

### Motivo
- Elimina concorrência entre automações.
- Reduz ruído operacional e risco de resposta duplicada.
- Preserva rastreabilidade completa no backend e no banco local.

### Rollback
- Reverter para configuração anterior apenas com validação de impacto:
  - `git revert <hash-da-decisao/processo>`
  - reaplicar configuração manual no Evolution conforme runbook.

---

*Documentado em: 07/02/2026*

---

## DECISAO-015: cliente canonico por CPF/CNPJ normalizado no fluxo de contratos

### Data
09/02/2026

### Contexto
O fluxo de `POST /api/v1/contratos` podia falhar com `500` (`MultipleResultsFound`)
quando havia clientes duplicados para o mesmo documento em formatos diferentes
(com mascara, sem mascara ou com espacos).

### Decisao
- Tratar documento de cliente por forma normalizada (somente digitos) nas buscas.
- Selecionar cliente canonico de forma deterministica quando existir legado duplicado.
- Adicionar saneamento administrativo:
  - `POST /api/v1/clientes/deduplicar-documentos`
  - relink de `contratos` e `agenda` para o cliente canonico
  - remocao dos duplicados
- No frontend:
  - `/contratos/novo` consulta cliente por documento e preenche dados automaticamente;
  - `/clientes` passa a expor editar/excluir e acao de saneamento.

### Motivo
- Remove erro 500 no fechamento/criacao de contrato.
- Formaliza regra institucional de 1 cliente por CPF/CNPJ.
- Evita regressao por inconsistencias de mascara no documento.

### Rollback
- `git checkout rollback-20260209-clientes-unicos-pre-fix`
- ou `git reset --hard rollback-20260209-clientes-unicos-pre-fix` (somente com aprovacao explicita).

---

*Documentado em: 09/02/2026*

---

## DECISAO-016: normalizacao defensiva de local_assinatura legado

### Data
09/02/2026

### Contexto
Mesmo apos a correcao geral de acentuacao (BUG-033), alguns contratos legados
continuavam exibindo local de assinatura com texto corrompido.

### Decisao
- Normalizar `local_assinatura` no preview e nos dois fluxos de PDF:
  - `frontend/src/app/(dashboard)/contratos/[id]/page.tsx`
  - `frontend/src/lib/pdf.ts`
  - `backend/app/services/pdf_service_playwright.py`
- Corrigir origem do dado em novo contrato:
  - `frontend/src/app/(dashboard)/contratos/novo/page.tsx` com default
    `Ribeirao Preto/SP`.
- Registrar BUG-034 como resolvido na trilha institucional.

### Motivo
- Eliminar exibicao residual de texto corrompido sem depender de migracao
  imediata da base legada.
- Garantir consistencia juridica e visual em preview/PDF.
- Evitar reincidencia em novos contratos.

### Rollback
- `docs/ROLLBACK/rollback-20260209-131517.patch`
- `git revert <hash-do-commit>`

---

*Documentado em: 09/02/2026*


---

## DECISAO-017: total de contratos por agregacao real + historico sob demanda no modulo clientes

### Data
09/02/2026

### Contexto
A tela de clientes precisava refletir com confiabilidade o total de contratos apos operacoes legadas e tambem oferecer visibilidade do historico por cliente sem navegar para outra tela.

### Decisao
- Backend (`ClienteService.list`): calcular `total_contratos`, `primeiro_contrato_em` e `ultimo_contrato_em` por agregacao direta em `contratos`.
- Frontend (`/clientes`): adicionar botao `Ver historico` no card, carregando contratos vinculados sob demanda.

### Motivo
- Remove dependencia exclusiva de metrica persistida sujeita a defasagem historica.
- Entrega rastreabilidade operacional no mesmo contexto da gestao de clientes.

### Rollback
- `docs/ROLLBACK/rollback-20260209-164001.patch`
- `git revert <hash-do-commit>`

---

*Documentado em: 09/02/2026*

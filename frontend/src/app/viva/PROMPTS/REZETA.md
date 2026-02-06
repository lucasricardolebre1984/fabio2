# Prompt Master (Institucional) — Identidade Visual RezetaBrasil — Versão Marketing+ (SEM alterar paleta)

## 0) Missão
Gerar imagens promocionais (banners/stories/feed) da RezetaBrasil com consistência visual absoluta, fotografia realista premium e copy em português que:
- Converta atenção em ação com clareza (mensagem em 2–3 segundos).
- Seja adaptável para públicos diversos (idade, gênero, classe, regiões).
- Aumente impacto emocional sem apelar para mentiras, promessas garantidas ou medo extremo.

## 1) NÃO NEGOCIÁVEL (Trave de Marca)
1) Paleta (não alterar):
   - Azul Marinho: #1E3A5F
   - Verde Esmeralda: #3DAA7F
   - Verde Escuro (gradiente): #2A8B68
   - Branco: #FFFFFF
2) Logo (não alterar):
   - Círculo verde esmeralda (#3DAA7F) com checkmark branco central.
   - Sempre circular, sempre centralizado no topo do overlay superior.
3) Layout com overlays edge-to-edge (não alterar):
   - Overlay superior branco semitransparente.
   - Overlay inferior gradiente verde semitransparente.
   - Pessoa com rosto bem visível no miolo (zona central).
4) Tipografia (manter estilo):
   - Sans-serif (preferência: Montserrat, Lato, Open Sans).
   - Headline MUITO grande, caixa alta, negrito.
   - Alternância de cores na headline: azul (#1E3A5F) e verde (#3DAA7F).
5) Idioma:
   - TODO texto visível na arte deve estar em português (Brasil).

## 2) Inputs (preencher campos entre [ ])
Preencha com precisão — isso é o “brief” que dirige a persuasão e a estética.

[CAMPANHA_NOME]            = (ex: Limpa Nome | Diagnóstico 360 | Linhas de Crédito PJ | Regularização | Consulta)
[OBJETIVO_DE_NEGOCIO]      = (ex: gerar leads WhatsApp | agendar diagnóstico | tráfego para landing | reconhecimento)
[PUBLICO_ALVO]             = (ex: PF endividado | PJ pequeno empresário | autônomo | CLT | MEI | aposentado)
[REGIAO_OU_BRASIL]         = (ex: Brasil | Nordeste | Sul | capitais | interior) — usar só para “vibe”, sem estereótipos
[NIVEL_DE_CONSCIENCIA]     = (1) não sabe o problema | (2) sente o problema | (3) conhece solução | (4) comparando | (5) pronto pra agir
[ANGULO_DE_MENSAGEM]       = (ex: esperança | urgência responsável | alívio | oportunidade | autoridade | prova social | simplicidade)
[FOCO_EMOCIONAL]           = (ex: alívio + dignidade | controle + confiança | recomeço | desbloqueio | tranquilidade)
[DORES_PRINCIPAIS]         = (listar 1–3: “crédito negado”, “nome travado”, “dívidas”, “medo de tentar e falhar”, “vergonha”, “insegurança”)
[DESEJO_PRINCIPAL]         = (1 frase: “voltar a comprar/empreender com paz”, “ter crédito”, “recomeçar”)
[OFERTA_OU_PROPOSTA]       = (ex: diagnóstico | consulta | ação guiada | triagem | análise)
[PROVA_OU_AUTORIDADE]      = (ex: “processo claro”, “orientação”, “passo a passo”, “análise”, “transparência”) — sem números inventados
[CALL_TO_ACTION]           = (ex: “FAÇA O DIAGNÓSTICO AGORA” | “CHAME NO WHATSAPP” | “COMEÇAR HOJE”)
[FORMATO_ASPECT_RATIO]     = (vertical 9:16 story | vertical 4:5 feed | square 1:1)
[TOP_OVERLAY_HEIGHT]       = (sugestão: 9:16 → 26% | 4:5 → 24% | 1:1 → 22%)
[BOTTOM_OVERLAY_HEIGHT]    = (sugestão: 9:16 → 28% | 4:5 → 26% | 1:1 → 24%)

## 3) Saída (o que deve ser gerado)
Uma imagem promocional fotográfica realista, moderna e profissional para a RezetaBrasil, no formato [FORMATO_ASPECT_RATIO], com:
- Atenção instantânea (headline forte e curta).
- Clareza total do próximo passo (CTA inequívoco).
- Emoção humana genuína (sem teatralidade).

## 4) Prompt Base (para o gerador de imagem) — MANTER ESTRUTURA / TURBINAR CONTEXTO
Professional promotional image for RezetaBrasil [CAMPANHA_NOME] campaign, [FORMATO_ASPECT_RATIO] format. FOCUS ON [FOCO_EMOCIONAL] with an [ANGULO_DE_MENSAGEM] tone designed for [PUBLICO_ALVO] in Brazil. Communication must be simple, direct, human, and high-trust.

BACKGROUND:
- [PERFIL_DA_PESSOA] in [DESCRICAO_DO_AMBIENTE].
- Realistic photography style, high-quality, modern Brazilian context, natural light, clean composition.
- Convey [EMOCAO_DESEJADA] as a genuine human moment (subtle facial expression, believable posture).
- Face clearly visible in the middle section.

PERSON PROFILE (choose/define based on [PUBLICO_ALVO] and [NIVEL_DE_CONSCIENCIA]):
- Diversity requirement: vary ethnicity, gender, age; represent Brazilian plurality; avoid stereotypes.
- Wardrobe: casual professional or corporate depending on PF/PJ context.
- Expression rules:
  - Problem-state campaigns: concern/frustration/overwhelm (never despair or panic).
  - Solution-state campaigns: relief/hope/confidence/happiness (never exaggerated euphoria).

ENVIRONMENT:
- [DESCRICAO_DO_AMBIENTE] should signal: safety, organization, modernity, credibility.
- Examples: bright modern home with plants; minimalist office; small business workspace; city view; clean desk; phone in hand (if CTA is chat).

TOP SECTION (covers full width edge-to-edge, [TOP_OVERLAY_HEIGHT]% height):
- Semi-transparent white overlay (70-80% opacity) extending left edge to right edge with subtle rounded bottom corners.
- At very top center: Circular logo with emerald green circle (#3DAA7F), white checkmark inside.
- Below logo: brand text “RezetaBrasil”
  - “Rezeta” in navy blue (#1E3A5F)
  - “Brasil” in emerald green (#3DAA7F)
  - Medium weight Sans-serif
- Main headline VERY LARGE, bold, uppercase Sans-serif:
  - Line 1: [HEADLINE_LINHA_1] in navy blue (#1E3A5F)
  - Line 2: [HEADLINE_LINHA_2] in emerald green (#3DAA7F)
- Subtitle (medium weight, navy blue #1E3A5F):
  - [SUBTITULO_1_LINHA] (curto, claro, sem jargão)
  - Optional second short line: [SUBTITULO_2_LINHA] (se necessário, no máximo 7–10 palavras)

BOTTOM SECTION (covers full width edge-to-edge, [BOTTOM_OVERLAY_HEIGHT]% height):
- Gradient green overlay from darker green (#2A8B68) on left to emerald green (#3DAA7F) on right, 75-85% opacity, extending edge-to-edge with subtle rounded top corners.
- White bold text LARGE centered: “[CALL_TO_ACTION]”
- Below: Small white circle with green checkmark icon (consistente com a marca)

CRITICAL REQUIREMENTS:
- Both overlays MUST extend edge-to-edge.
- Maintain color alternation (navy + emerald) in headline.
- Warm, positive, professional atmosphere.
- All visible text MUST be Portuguese (pt-BR).
- No clutter: 1 ideia por arte. Sem excesso de linhas.
- Legibilidade mobile: alto contraste, headline curta, poucas palavras.
- Avoid false guarantees, invented statistics, or aggressive fear tactics.

## 5) Motor de Copy (Marketing de Alta Conversão, sem “dark patterns”)
Objetivo: transformar [DORES_PRINCIPAIS] em ação via clareza + identidade + dignidade.

5.1 Frameworks permitidos (escolher 1 por campanha):
A) PAS (Problema–Agitação–Solução) — rápido e direto
B) AIDA (Atenção–Interesse–Desejo–Ação) — clássico
C) 4U (Útil, Urgente, Único, Ultra-específico) — headline matadora
D) StoryBrand (personagem → problema → guia → plano → ação) — narrativa de confiança

5.2 Heurísticas cognitivas (use com responsabilidade):
- Clareza > criatividade: a “criatividade” é tornar o óbvio irresistivelmente simples.
- Especificidade concreta (tempo, cenário, próximo passo) sem inventar dados.
- Alívio + dignidade: comunicar sem humilhar.
- Prova/autoridade: “processo”, “orientação”, “passo a passo”, “análise” (sem números falsos).
- Atrito zero: CTA de 2–4 palavras, verbo forte, benefício implícito.

5.3 Biblioteca de Headline (gerar variações)
Regras:
- Headline total (linha 1 + linha 2) preferencialmente 4–8 palavras.
- Linha 1 = “gancho” (tensão / contraste / diagnóstico)
- Linha 2 = “virada” (benefício / direção / desbloqueio)

Modelos (preencher conforme campanha):
- “SEU NOME” / “PODE DESTRAVAR HOJE”
- “CRÉDITO NEGADO?” / “DESCUBRA O MOTIVO”
- “BLOQUEIO INVISÍVEL” / “A GENTE TE MOSTRA”
- “RECOMEÇO REAL” / “COM PASSO A PASSO”
- “VOCÊ NÃO ESTÁ SOZINHO” / “VAMOS RESOLVER”

Subtítulos (tom humano, 1 frase):
- “Diagnóstico claro, sem enrolação.”
- “Entenda o que está travando e o próximo passo.”
- “Orientação simples pra sair do ‘não’ e ir pro ‘sim’.”
- “Comece hoje com um caminho organizado.”

CTAs (curtos, ação imediata):
- “FAZER DIAGNÓSTICO”
- “CHAMAR NO WHATSAPP”
- “COMEÇAR AGORA”
- “QUERO MEU RECOMEÇO”
- “VER MEU CASO”

## 6) Matriz de Segmentos (mensagem para “todo tipo de pessoa”)
Escolha 1 “voz” por peça, mantendo a marca:
A) Popular e direta (sem gírias pesadas): simples, acolhedora, objetiva.
B) Profissional e consultiva: credibilidade, processo, clareza.
C) Empreendedora (PJ/MEI): foco em crescimento, fluxo de caixa, oportunidade.

Adapte a cena e o personagem:
- PF: casa, celular, contas, expressão de preocupação → alívio.
- PJ/MEI: escritório simples, notebook, planilhas, postura de decisão.
- Misto: ambiente neutro, foco no rosto + gesto com celular.

## 7) Checklist de Qualidade (antes de finalizar)
- O rosto está claramente visível no meio?
- Headline é lida em 2 segundos no celular?
- Azul/verde alternados corretamente?
- Overlays edge-to-edge e opacidade correta?
- CTA em branco com alto contraste no gradiente?
- Texto 100% pt-BR, sem termos técnicos?
- Sem promessas absolutas e sem números inventados?
- A emoção parece real (não pose artificial)?

## 8) Referências (para “DNA” criativo e persuasivo — sem copiar, apenas inspirar)
- Robert Cialdini — “Influence” (princípios de persuasão e confiança)
- Chip Heath & Dan Heath — “Made to Stick” (mensagens memoráveis)
- Donald Miller — “Building a StoryBrand” (clareza narrativa)
- David Ogilvy — “Ogilvy on Advertising” (disciplina criativa e clareza)
- Eugene Schwartz — “Breakthrough Advertising” (níveis de consciência e desejo)
- Claude Hopkins — “Scientific Advertising” (copy com lógica e teste)
- Gary Bencivenga — princípios de copy orientado a benefício e especificidade
- Seth Godin — posicionamento, tensão e diferenciação
- Alex Hormozi — oferta clara, valor percebido e redução de risco (sem promessas falsas)

## 9) Campos rápidos (para facilitar preenchimento)
[PERFIL_DA_PESSOA]         = (idade, etnia, gênero, roupa, expressão, postura, acessório se necessário)
[DESCRICAO_DO_AMBIENTE]    = (casa/escritório/loja; luz natural; plantas; mesa limpa; minimalista)
[EMOCAO_DESEJADA]          = (preocupação controlada | alívio | confiança | esperança | decisão)

[HEADLINE_LINHA_1]         = (gancho curto)
[HEADLINE_LINHA_2]         = (virada/benefício)
[SUBTITULO_1_LINHA]        = (clareza + dignidade)
[SUBTITULO_2_LINHA]        = (opcional, curtíssimo)
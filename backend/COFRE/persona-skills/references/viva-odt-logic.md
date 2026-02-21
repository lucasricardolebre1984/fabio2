# VIVA ODT Logic - Operational Decision Theory

Data: 2026-02-21
Objetivo: dar a VIVA uma logica operacional previsivel para executar sem invencao.

## 1) ODT (adaptado para operacao SaaS)

ODT nesta implementacao:
- O = Outcome (resultado desejado pelo usuario)
- D = Diagnosis (diagnostico por dados reais do SaaS)
- T = Task (tarefa executavel na rota correta)

## 2) Loop pratico da VIVA

1. Outcome
- Extrair o objetivo em 1 frase.
- Exemplo: "agendar reuniao e avisar participantes no WhatsApp".

2. Diagnosis
- Verificar dados minimos necessarios.
- Consultar endpoints reais para reduzir ambiguidade.
- Nao assumir dados ausentes.

3. Task
- Executar na rota real.
- Se faltar dado obrigatorio, fazer apenas 1 pergunta objetiva.
- Retornar resultado operacional curto (feito/erro real/proximo passo).

## 3) Mapeamento ODT por dominio

- Agenda:
  - O: criar/listar/concluir compromisso
  - D: data, hora, titulo, participante(s)
  - T: `POST/GET/PATCH /api/v1/agenda*`

- Clientes:
  - O: abrir/listar cliente
  - D: id, nome, documento
  - T: `GET /api/v1/clientes*`

- Contratos:
  - O: listar/abrir contrato ou template
  - D: tipo, id, cliente
  - T: `GET /api/v1/contratos*`

- Handoff VIVA -> VIVIANE:
  - O: disparar mensagem WhatsApp no tempo certo
  - D: numero, mensagem, horario, agenda_event_id
  - T: `POST /api/v1/viva/handoff/schedule`

## 4) Literatura base (ODT/Outcome-driven)

- Tony Ulwick (Outcome-Driven Innovation):
  - `https://hbr.org/2002/01/turn-customer-input-into-innovation`
  - `https://www.strategyn.com/jobs-to-be-done/outcome-driven-innovation/`

Interpretacao aplicada:
- Outcome = objetivo do usuario
- Diagnosis = validacao por dados operacionais
- Task = execucao deterministica por endpoint

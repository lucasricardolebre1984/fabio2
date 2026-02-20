# Viviane Naturalidade - 2026-02-20

## Escopo
- Reduzir tom robotico/agressivo no WhatsApp.
- Evitar preco espontaneo quando cliente nao pediu.
- Melhorar resposta em conversa social/humor sem perder contexto comercial.

## Ajustes implementados
- Arquivo: `backend/app/services/viva_ia_service.py`
  - resposta de identidade agora reconhece feedback de ritmo/preco e ajusta tom com empatia;
  - resposta dedicada para intencao com humor (`ficar rico`) sem travar em metrico/preco;
  - filtro pos-modelo remove sentencas com preco nao solicitado;
  - regra dinamica de prompt reforca: preco so quando cliente pedir.
- Arquivo: `backend/COFRE/persona-skills/VIVIANE.md`
  - regra explicita de nao informar preco espontaneamente;
  - diretriz para responder com leveza em humor e ajustar ritmo sob feedback.
- Testes: `backend/tests/test_viviane_humanizacao.py`
  - cobertura de feedback sobre preco/ritmo;
  - cobertura de resposta com humor;
  - cobertura de limpeza de preco nao solicitado.

## Evidencia de validacao
- `python -m py_compile app/services/viva_ia_service.py tests/test_viviane_humanizacao.py`
- `PYTHONPATH=C:\\projetos\\fabio2\\backend pytest tests/test_viviane_humanizacao.py -q`
- Resultado: `17 passed`.


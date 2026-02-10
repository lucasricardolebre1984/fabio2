"""
VIVA concierge persona for internal SaaS operations.
"""
from typing import Optional


class VivaConciergeService:
    """Builds the internal VIVA concierge system prompt."""

    def __init__(self) -> None:
        self.base_prompt = (
            "Voce e VIVA, concierge do Fabio e assistente principal do SaaS da FC Solucoes Financeiras. "
            "Voce ajuda no dia a dia operacional (contratos, clientes, agenda, WhatsApp e organizacao interna). "
            "Fale de forma natural, objetiva e humana."
        )
        self.brand_memory = (
            "Contexto fixo de marcas no SaaS: "
            "FC Solucoes Financeiras usa identidade azul e branco; "
            "RezetaBrasil usa verde e azul. "
            "Quando o usuario escolher FC ou REZETA, respeite a identidade da marca automaticamente."
        )
        self.behavior_rules = [
            "Se faltarem dados, faca no maximo uma pergunta curta por vez.",
            "Evite entrevista longa e respostas engessadas.",
            "Nunca invente status, prazos, resultados ou dados de sistema.",
            "Quando houver acao operacional, confirme claramente o que foi feito.",
            "Priorize continuidade do contexto da sessao atual.",
            "Para campanhas, conduza no maximo 3 gates curtos e depois gere sem burocracia.",
            "Atue como braco direito do Fabio: pratica, proativa e orientada a resultado.",
        ]

    def build_system_prompt(self, modo: Optional[str] = None) -> str:
        rules = "\n".join(f"- {rule}" for rule in self.behavior_rules)
        prompt = (
            f"{self.base_prompt}\n\n"
            f"{self.brand_memory}\n\n"
            f"Regras de comportamento:\n{rules}"
        )
        if modo:
            prompt = f"{prompt}\n\nModo operacional atual: {modo}."
        return prompt


viva_concierge_service = VivaConciergeService()

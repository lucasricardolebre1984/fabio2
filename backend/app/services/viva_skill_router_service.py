"""
Roteador simples de skills da VIVA.

Objetivo: explicitar qual skill o orquestrador escolheu para cada mensagem.
"""

from typing import Any, Dict, Optional


class VivaSkillRouterService:
    def resolve_skill(
        self,
        *,
        mensagem: str,
        modo: Optional[str],
        agenda_query_intent: bool,
        has_agenda_create_payload: bool,
        handoff_intent: bool,
        viviane_handoff_query_intent: bool,
        campaign_flow_requested: bool,
        should_generate_image: bool,
        logo_request: bool,
    ) -> Dict[str, Any]:
        text = (mensagem or "").strip()
        text_len = len(text)

        if handoff_intent:
            return {
                "skill_id": "handoff_viviane",
                "reason": "mensagem com intencao de aviso WhatsApp para cliente",
                "confidence": 0.95,
                "mode": modo,
                "input_chars": text_len,
                "skill_source": "agents/AGENT.md",
            }

        if viviane_handoff_query_intent:
            return {
                "skill_id": "consultar_handoff_viviane",
                "reason": "consulta de tarefas pendentes/enviadas da Viviane",
                "confidence": 0.92,
                "mode": modo,
                "input_chars": text_len,
                "skill_source": "agents/AGENT.md",
            }

        if has_agenda_create_payload:
            return {
                "skill_id": "agenda_criar_compromisso",
                "reason": "comando de criacao de compromisso identificado",
                "confidence": 0.94,
                "mode": modo,
                "input_chars": text_len,
                "skill_source": "agents/AGENT.md",
            }

        if agenda_query_intent:
            return {
                "skill_id": "agenda_consultar",
                "reason": "consulta de agenda por linguagem natural",
                "confidence": 0.9,
                "mode": modo,
                "input_chars": text_len,
                "skill_source": "agents/AGENT.md",
            }

        if should_generate_image and campaign_flow_requested and modo in ("FC", "REZETA"):
            return {
                "skill_id": "generate_campanha_neutra",
                "reason": "fluxo criativo de campanha/imagem com skill neutra",
                "confidence": 0.96,
                "mode": modo,
                "input_chars": text_len,
                "skill_source": "agents/skillconteudo.txt",
            }

        if should_generate_image and logo_request:
            return {
                "skill_id": "generate_logo_background",
                "reason": "pedido de imagem em modo logo",
                "confidence": 0.9,
                "mode": "LOGO",
                "input_chars": text_len,
                "skill_source": "agents/AGENT.md",
            }

        if campaign_flow_requested and modo in ("FC", "REZETA"):
            return {
                "skill_id": "campaign_planner",
                "reason": "planejamento textual de campanha sem gerar imagem",
                "confidence": 0.88,
                "mode": modo,
                "input_chars": text_len,
                "skill_source": "agents/AGENT.md",
            }

        return {
            "skill_id": "chat_geral",
            "reason": "conversa geral com prompt principal da VIVA",
            "confidence": 0.8,
            "mode": modo,
            "input_chars": text_len,
            "skill_source": "agents/AGENT.md",
        }


viva_skill_router_service = VivaSkillRouterService()

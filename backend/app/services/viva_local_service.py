"""
VIVA Local Service - fallback sem provedor externo.

Objetivo:
- Evitar respostas longas, menus e templates quando a IA remota falha.
- Nao substituir o orquestrador/skills; apenas oferecer uma resposta minima.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.viva_agent_profile_service import viva_agent_profile_service


class VivaLocalService:
    def __init__(self) -> None:
        # Usa o mesmo contrato canonico do agente para nao reintroduzir prompts antigos.
        self._system_prompt = viva_agent_profile_service.build_system_prompt()

    def build_messages(
        self,
        user_message: str,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": self._system_prompt}]
        if context:
            for msg in context:
                tipo = str(msg.get("tipo") or "").strip().lower()
                conteudo = str(msg.get("conteudo") or "").strip()
                if not conteudo:
                    continue
                if tipo == "usuario":
                    messages.append({"role": "user", "content": conteudo})
                elif tipo == "ia":
                    messages.append({"role": "assistant", "content": conteudo})
        messages.append({"role": "user", "content": str(user_message or "").strip()})
        return messages

    async def chat(self, messages: List[Dict[str, str]], modo: Optional[str] = None) -> str:
        # Resposta curta por padrao. Nao lista modulos nem "modos" do menu lateral.
        ultima = ""
        if messages:
            ultima = str(messages[-1].get("content") or "").strip()

        if not ultima:
            return "Como posso ajudar?"

        lowered = ultima.lower()
        if any(token in lowered for token in ("bom dia", "boa tarde", "boa noite", "ola", "olá")) and len(lowered) <= 24:
            return "Ola. O que voce precisa agora?"

        # Nao tenta simular RAG/agenda sem backend; apenas pede detalhe minimo.
        return "Entendi. Me diga o objetivo e os dados essenciais (quem, quando e o que) para eu seguir."

    async def vision(self, image_base64: str, prompt: str) -> str:
        # Sem analise local real; manter curto.
        return "Recebi a imagem. Descreva exatamente o que voce quer extrair/validar dela."

    def get_status(self) -> Dict[str, Any]:
        return {
            "api_configurada": False,
            "modelo": "VIVA Local (fallback minimo)",
            "tipo": "fallback",
        }


viva_local_service = VivaLocalService()

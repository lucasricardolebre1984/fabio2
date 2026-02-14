"""DeepSeek Service - provedor alternativo ao OpenAI.

Importante: este service deve seguir o mesmo contrato canonico do agente
(`agents/AGENT.md`) para nao reintroduzir prompts legados.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.services.viva_agent_profile_service import viva_agent_profile_service


class DeepSeekService:
    def __init__(self) -> None:
        self.api_key = getattr(settings, "DEEPSEEK_API_KEY", None)
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"  # ou "deepseek-reasoner" para thinking mode
        self.system_prompt = viva_agent_profile_service.build_system_prompt()

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            return "Provedor DeepSeek nao configurado."

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 800,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return str(data["choices"][0]["message"]["content"])

                import logging

                logging.error("DeepSeek error: %s", response.status_code)
                return "Nao consegui processar agora. Tente novamente."
        except Exception as exc:
            import logging

            logging.error("DeepSeek exception: %s", repr(exc))
            return "Falha tecnica ao processar sua mensagem."

    def build_messages(
        self,
        user_message: str,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

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


deepseek_service = DeepSeekService()

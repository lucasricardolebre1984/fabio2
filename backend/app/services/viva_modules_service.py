"""
Catalogo institucional de modulos e gates da VIVA.

Objetivo: expor status tecnico para modularizacao comercial do SaaS.
"""

from typing import Any, Dict, List

from app.config import settings
from app.services.cofre_manifest_service import cofre_manifest_service


class VivaModulesService:
    def get_modules_status(self) -> Dict[str, Any]:
        has_openai_key = bool(settings.OPENAI_API_KEY)
        embedding_fallback_local = bool(settings.OPENAI_EMBEDDING_FALLBACK_LOCAL)
        rag_premium_ready = bool(has_openai_key and not embedding_fallback_local)

        gates: List[Dict[str, Any]] = [
            {
                "gate_id": "gate_1",
                "title": "Governanca e rollback",
                "status": "completed",
                "summary": "Baseline institucional e rollback de seguranca registrados.",
                "blockers": [],
                "next_actions": [
                    "Manter snapshot de rollback antes de cada rodada de mudanca estrutural.",
                ],
            },
            {
                "gate_id": "gate_2",
                "title": "Modularizacao comercial",
                "status": "in_progress",
                "summary": "Separacao por modulos e orquestracao por skills em consolidacao.",
                "blockers": [],
                "next_actions": [
                    "Concluir endpoints/contratos por modulo para onboarding rapido de novos clientes.",
                ],
            },
            {
                "gate_id": "gate_3",
                "title": "Homologacao IA conversacional",
                "status": "pending",
                "summary": "Voz/avatar institucionais e validacao semantica premium do RAG.",
                "blockers": ["BUG-092", "BUG-093", "BUG-094"],
                "next_actions": [
                    "Padronizar stack de fala ao vivo.",
                    "Aplicar avatar oficial da VIVA.",
                    "Executar bateria de qualidade semantica com embeddings OpenAI.",
                ],
            },
        ]

        modules: List[Dict[str, Any]] = cofre_manifest_service.modules()

        runtime = {
            "openai_api_key_configured": has_openai_key,
            "embedding_fallback_local": embedding_fallback_local,
            "rag_premium_ready": rag_premium_ready,
            "speech_stack": "browser_native",
        }

        return {"gates": gates, "modules": modules, "runtime": runtime}


viva_modules_service = VivaModulesService()

"""
Catalogo institucional de modulos e gates da VIVA.

Objetivo: expor status tecnico para modularizacao comercial do SaaS.
"""

from typing import Any, Dict, List

from app.config import settings


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

        modules: List[Dict[str, Any]] = [
            {
                "module_id": "core_saas",
                "nome": "Core SaaS",
                "status": "ready",
                "descricao": "Autenticacao, contratos, clientes, agenda e base operacional.",
                "dependencias": ["postgres", "redis"],
                "endpoints": ["/api/v1/auth/*", "/api/v1/contratos/*", "/api/v1/clientes/*", "/api/v1/agenda/*"],
                "notes": ["Apto para base de novos projetos com personalizacao de marca."],
            },
            {
                "module_id": "modulo_viva",
                "nome": "VIVA Interna",
                "status": "hardening",
                "descricao": "Chat interno com orquestracao, sessoes e memoria contextual.",
                "dependencias": ["openai", "postgres", "redis"],
                "endpoints": ["/api/v1/viva/chat", "/api/v1/viva/chat/sessions", "/api/v1/viva/chat/snapshot"],
                "notes": ["Prompt principal unico ativo em viva_concierge_service."],
            },
            {
                "module_id": "modulo_viviane",
                "nome": "Viviane Externa",
                "status": "ready",
                "descricao": "Atendimento comercial em WhatsApp com handoff agendado.",
                "dependencias": ["evolution_api", "postgres"],
                "endpoints": ["/api/v1/whatsapp/*", "/api/v1/whatsapp-chat/*", "/api/v1/viva/handoff/*"],
                "notes": ["Separado por dominio da VIVA interna."],
            },
            {
                "module_id": "modulo_campanhas",
                "nome": "Campanhas e Criativos",
                "status": "hardening",
                "descricao": "Planejamento criativo, geracao de imagem e historico de campanhas.",
                "dependencias": ["openai", "postgres"],
                "endpoints": ["/api/v1/viva/campanhas", "/api/v1/viva/image/generate", "/api/v1/viva/chat"],
                "notes": ["Skill generate_campanha definida para roteamento automatico."],
            },
            {
                "module_id": "modulo_memoria",
                "nome": "Memoria e RAG",
                "status": "assisted",
                "descricao": "Memoria curta/media/longa com pgvector e fallback local de embeddings.",
                "dependencias": ["openai", "postgres_pgvector", "redis"],
                "endpoints": [
                    "/api/v1/cofre/memories/status",
                    "/api/v1/cofre/memories/tables",
                    "/api/v1/cofre/memories/{table_name}/tail",
                ],
                "notes": [
                    "Operacional para continuidade.",
                    "Homologacao semantica premium pendente (BUG-094).",
                ],
            },
        ]

        runtime = {
            "openai_api_key_configured": has_openai_key,
            "embedding_fallback_local": embedding_fallback_local,
            "rag_premium_ready": rag_premium_ready,
            "speech_stack": "browser_native",
        }

        return {"gates": gates, "modules": modules, "runtime": runtime}


viva_modules_service = VivaModulesService()

"""
Capabilities catalog exposed by VIVA.
"""
from typing import Any, Dict, List


class VivaCapabilitiesService:
    def get_capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "dominio": "agenda",
                "acoes": [
                    "criar compromisso em linguagem natural",
                    "listar compromissos por periodo",
                    "concluir compromisso por id ou titulo",
                ],
                "rotas": [
                    "/api/v1/viva/chat",
                    "/api/v1/agenda",
                ],
            },
            {
                "dominio": "campanhas",
                "acoes": [
                    "planejar campanhas com briefing curto",
                    "gerar imagem com identidade FC/Rezeta",
                    "salvar e listar historico de campanhas",
                ],
                "rotas": [
                    "/api/v1/viva/chat",
                    "/api/v1/viva/campanhas",
                ],
            },
            {
                "dominio": "handoff_viviane",
                "acoes": [
                    "agendar aviso para cliente no WhatsApp",
                    "listar tarefas de handoff",
                    "processar tarefas vencidas",
                ],
                "rotas": [
                    "/api/v1/viva/handoff/schedule",
                    "/api/v1/viva/handoff",
                    "/api/v1/viva/handoff/process-due",
                ],
            },
            {
                "dominio": "midia",
                "acoes": [
                    "analise de imagem (vision)",
                    "transcricao de audio",
                    "geracao de imagem e video",
                ],
                "rotas": [
                    "/api/v1/viva/vision",
                    "/api/v1/viva/vision/upload",
                    "/api/v1/viva/audio/transcribe",
                    "/api/v1/viva/image/generate",
                    "/api/v1/viva/video/generate",
                ],
            },
            {
                "dominio": "memoria",
                "acoes": [
                    "gravar espelho canonico em COFRE por tabela/subpasta",
                    "manter memoria media da sessao em Redis",
                    "indexar memoria longa vetorial em pgvector",
                ],
                "rotas": [
                    "/api/v1/cofre/memories/status",
                    "/api/v1/cofre/memories/tables",
                    "/api/v1/cofre/memories/{table_name}/tail",
                    "/api/v1/viva/chat/sessions",
                    "/api/v1/viva/chat/snapshot",
                ],
            },
            {
                "dominio": "modulos_produto",
                "acoes": [
                    "expor status dos gates institucionais",
                    "listar readiness dos modulos comercializaveis",
                    "publicar sinal de runtime para RAG premium e stack de voz",
                ],
                "rotas": [
                    "/api/v1/viva/modules/status",
                ],
            },
        ]


viva_capabilities_service = VivaCapabilitiesService()

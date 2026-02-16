"""Domain query router for VIVA.

Centraliza consultas de dominios (contratos, clientes, campanhas e servicos)
para manter o orquestrador principal mais enxuto.
"""

import re
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.services.cliente_service import ClienteService
from app.services.contrato_service import ContratoService
from app.services.viva_campaign_repository_service import viva_campaign_repository_service
from app.services.viva_chat_domain_service import _is_direct_generation_intent, _is_image_request
from app.services.viva_shared_service import _normalize_key


def _is_contract_list_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    contract_tokens = ("contrato", "contratos")
    list_tokens = ("listar", "liste", "lista", "quais", "titulos", "todos", "registrados", "executamos", "mostre")
    has_contract = any(token in normalized for token in contract_tokens)
    has_list_signal = any(token in normalized for token in list_tokens)
    return has_contract and has_list_signal


def _is_contract_templates_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_contract = ("contrato" in normalized) or ("contratos" in normalized)
    has_template_signal = any(
        token in normalized
        for token in (
            "executamos",
            "tipos",
            "modelos",
            "modolos",
            "modolo",
            "templates",
            "template",
        )
    )
    return has_contract and has_template_signal


def _is_contracts_by_client_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_contract = "contrato" in normalized or "contratos" in normalized
    has_client = "cliente" in normalized or "para " in normalized or "pro " in normalized
    return has_contract and has_client


def _extract_client_name_for_contract_query(message: str) -> Optional[str]:
    raw = str(message or "").strip()
    if not raw:
        return None

    patterns = [
        r"(?:pro|para|do|da|de)\s+cliente\s+(.+)$",
        r"cliente\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, flags=re.IGNORECASE)
        if match:
            name = re.sub(r"[\]\[\)\(\.,;:!?]+$", "", match.group(1).strip())
            name = re.sub(r"\s+", " ", name).strip()
            if name:
                return name
    return None


def _is_client_list_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_client = ("cliente" in normalized) or ("clientes" in normalized)
    has_list_signal = any(token in normalized for token in ("listar", "liste", "lista", "quais", "todos", "registrados", "mostre"))
    return has_client and has_list_signal


def _is_services_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    return (
        ("servico" in normalized or "servicos" in normalized)
        and any(token in normalized for token in ("nossos", "empresa", "saas", "quais"))
    )


def _is_campaign_list_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_campaign = "campanha" in normalized or "campanhas" in normalized
    has_list_signal = any(
        token in normalized
        for token in ("listar", "liste", "lista", "quais", "historico", "criadas", "criados", "mostre")
    )
    has_generate_signal = bool(
        _is_image_request(message) or _is_direct_generation_intent(message)
    )
    return has_campaign and has_list_signal and not has_generate_signal


def _extract_campaign_mode_filter(message: str) -> Optional[str]:
    normalized = _normalize_key(message or "")
    if "rezeta" in normalized:
        return "REZETA"
    if " fc " in f" {normalized} " or "fc solucoes" in normalized:
        return "FC"
    return None


def _is_direct_confirmation(message: str) -> bool:
    normalized = _normalize_key(message or "")
    return normalized in {
        "sim",
        "todos",
        "todos registrados",
        "aqui no chat",
        "listar todos",
        "listar",
        "nomes",
    }


def _last_pending_list_domain(contexto: List[Dict[str, Any]]) -> Optional[str]:
    for msg in reversed(contexto[-10:]):
        if str(msg.get("tipo") or "") != "ia":
            continue
        normalized = _normalize_key(str(msg.get("conteudo") or ""))
        if not normalized:
            continue
        if ("deseja" in normalized or "quer" in normalized or "confirmo" in normalized) and (
            "listar" in normalized or "liste" in normalized or "lista" in normalized or "exiba" in normalized
        ):
            if "cliente" in normalized or "clientes" in normalized:
                return "clientes"
            if any(token in normalized for token in ("modelo", "modelos", "template", "templates", "tipos")):
                return "contratos_modelos"
            if "contrato" in normalized or "contratos" in normalized:
                return "contratos_emitidos"
    return None


class VivaDomainQueryRouterService:
    async def handle_domain_query(
        self,
        *,
        db: Any,
        user_id: UUID,
        message: str,
        contexto_efetivo: List[Dict[str, Any]],
    ) -> Optional[str]:
        pending_list_domain = _last_pending_list_domain(contexto_efetivo)
        contract_templates_intent = _is_contract_templates_intent(message)
        contracts_by_client_intent = _is_contracts_by_client_intent(message)
        contract_list_intent = (_is_contract_list_intent(message) and not contract_templates_intent) or (
            _is_direct_confirmation(message) and pending_list_domain == "contratos_emitidos"
        )
        contract_templates_intent = contract_templates_intent or (
            _is_direct_confirmation(message) and pending_list_domain == "contratos_modelos"
        )
        if contracts_by_client_intent or contract_list_intent or contract_templates_intent:
            contrato_service = ContratoService(db)
            if contracts_by_client_intent:
                client_name = _extract_client_name_for_contract_query(message)
                if not client_name:
                    return "Informe o nome do cliente para eu listar os contratos emitidos."

                contratos_data = await contrato_service.list(
                    status=None,
                    search=client_name,
                    page=1,
                    page_size=500,
                )
                contratos_items = list(contratos_data.get("items", []))
                filtered_items = [
                    item
                    for item in contratos_items
                    if client_name.lower() in str(getattr(item, "contratante_nome", "") or "").lower()
                ]
                if not filtered_items:
                    return f"Nao encontrei contratos emitidos para o cliente {client_name}."

                lines = [f"Contratos emitidos para {client_name}:"]
                for item in filtered_items:
                    numero = str(getattr(item, "numero", "") or "sem numero")
                    titulo = str(getattr(item, "template_nome", "") or getattr(item, "template_id", "") or "").strip()
                    if not titulo:
                        titulo = "Contrato sem titulo"
                    status_value = getattr(getattr(item, "status", None), "value", getattr(item, "status", ""))
                    created_at = getattr(item, "created_at", None)
                    created_label = created_at.strftime("%d/%m/%Y") if created_at else "sem data"
                    lines.append(f"- {numero} | {titulo} | {created_label} | {status_value}")
                return "\n".join(lines)
            if contract_templates_intent:
                templates = await contrato_service.list_templates()
                titles = [
                    str(item.get("nome") or "").strip()
                    for item in templates
                    if str(item.get("nome") or "").strip()
                ]
                lines = ["Titulos dos modelos de contrato ativos:"]
                if not titles:
                    contratos_data = await contrato_service.list(
                        status=None,
                        search=None,
                        page=1,
                        page_size=500,
                    )
                    contratos_items = list(contratos_data.get("items", []))
                    if not contratos_items:
                        return "Nao ha modelos ativos nem contratos registrados no sistema."

                    seen_templates: set[str] = set()
                    for item in contratos_items:
                        title = str(getattr(item, "template_nome", "") or "").strip()
                        if not title:
                            title = str(getattr(item, "template_id", "") or "").strip()
                        if title and title not in seen_templates:
                            seen_templates.add(title)
                            titles.append(title)
                    lines = [
                        "Nao encontrei modelos formais ativos. "
                        "Como referencia, estes sao os titulos de contratos ja registrados:"
                    ]
            else:
                contratos_data = await contrato_service.list(
                    status=None,
                    search=None,
                    page=1,
                    page_size=500,
                )
                contratos_items = list(contratos_data.get("items", []))
                if not contratos_items:
                    return "Nao ha contratos registrados no sistema."

                seen: set[str] = set()
                titles = []
                for item in contratos_items:
                    title = str(getattr(item, "template_nome", "") or "").strip()
                    if not title:
                        title = str(getattr(item, "template_id", "") or "").strip() or "Contrato sem titulo"
                    if title not in seen:
                        seen.add(title)
                        titles.append(title)

                lines = ["Titulos dos contratos registrados:"]
            lines.extend(f"- {title}" for title in titles)
            return "\n".join(lines)

        client_list_intent = _is_client_list_intent(message) or (
            _is_direct_confirmation(message) and pending_list_domain == "clientes"
        )
        if client_list_intent:
            cliente_service = ClienteService(db)
            payload = await cliente_service.list(search=None, page=1, page_size=200)
            clients = list(payload.get("items", []))
            if not clients:
                return "Nao ha clientes registrados no sistema."
            lines = ["Clientes registrados:"]
            for item in clients:
                if isinstance(item, dict):
                    nome = str(item.get("nome") or "").strip()
                else:
                    nome = str(getattr(item, "nome", "") or "").strip()
                lines.append(f"- {nome or 'Cliente sem nome'}")
            return "\n".join(lines)

        if _is_services_intent(message):
            lines = [
                "Servicos do SaaS:",
                "- gestao de contratos",
                "- gestao de clientes",
                "- agenda operacional com sync Google Calendar",
                "- campanhas e criativos IA",
                "- handoff para WhatsApp",
                "- memoria operacional da VIVA no COFRE",
            ]
            return "\n".join(lines)

        if _is_campaign_list_intent(message):
            mode_filter = _extract_campaign_mode_filter(message)
            rows, total = await viva_campaign_repository_service.list_campaign_rows(
                db=db,
                user_id=user_id,
                modo=mode_filter,
                limit=30,
                offset=0,
            )
            if total <= 0:
                return "Nao ha campanhas registradas no sistema."
            lines = ["Campanhas registradas:"]
            for row in rows:
                created_label = (
                    row.created_at.strftime("%d/%m/%Y %H:%M")
                    if getattr(row, "created_at", None)
                    else "sem data"
                )
                lines.append(f"- {row.titulo} ({row.modo}) - {created_label}")
            return "\n".join(lines)

        return None


viva_domain_query_router_service = VivaDomainQueryRouterService()

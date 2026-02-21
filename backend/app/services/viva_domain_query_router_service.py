"""Domain query router for VIVA.

Centraliza consultas de dominios (contratos, clientes, campanhas e servicos)
para manter o orquestrador principal mais enxuto.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
import re

from app.services.assistant.intents.campanhas import (
    extract_campaign_mode_filter,
    is_campaign_count_intent,
    is_campaign_list_intent,
)
from app.services.assistant.intents.clientes import (
    extract_client_name_for_detail_query,
    is_client_detail_intent,
    is_client_list_intent,
    is_client_profile_contracts_intent,
    is_visual_proof_request,
)
from app.services.assistant.intents.contratos import (
    extract_client_name_for_contract_query,
    is_contract_list_intent,
    is_contract_templates_intent,
    is_contracts_by_client_intent,
)
from app.services.cliente_service import ClienteService
from app.services.contrato_service import ContratoService
from app.services.viva_campaign_repository_service import viva_campaign_repository_service
from app.services.viva_shared_service import _normalize_key, _normalize_mojibake_text


def _is_direct_confirmation(message: str) -> bool:
    normalized = _normalize_key(message or "")
    return normalized in {
        "sim",
        "ok",
        "quero",
        "quero mostrar",
        "quero mostre",
        "quero sim",
        "pode listar",
        "com numero",
        "numero",
        "com numero do contrato",
        "todos",
        "todos registrados",
        "aqui no chat",
        "listar todos",
        "listar",
        "nomes",
    }


def _last_pending_list_domain(contexto: List[Dict[str, Any]]) -> Optional[str]:
    # Considera apenas o ultimo prompt da IA para evitar capturar confirmacoes antigas.
    for msg in reversed(contexto[-4:]):
        if str(msg.get("tipo") or "") == "ia":
            normalized = _normalize_key(str(msg.get("conteudo") or ""))
            if not normalized:
                return None
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
    return None


def _format_optional(value: Any) -> str:
    text = _normalize_mojibake_text(value).strip()
    return text if text else "nao informado"


def _find_best_client_match(items: List[Dict[str, Any]], requested_name: str) -> Optional[Dict[str, Any]]:
    if not items:
        return None
    normalized_requested = _normalize_key(requested_name)
    if not normalized_requested:
        return items[0]

    def score(item: Dict[str, Any]) -> int:
        name = _normalize_key(str(item.get("nome") or ""))
        if not name:
            return 0
        if name == normalized_requested:
            return 100
        if normalized_requested in name:
            return 80
        if name in normalized_requested:
            return 60
        request_tokens = set(normalized_requested.split())
        name_tokens = set(name.split())
        return len(request_tokens.intersection(name_tokens)) * 10

    ranked = sorted(items, key=score, reverse=True)
    return ranked[0] if ranked and score(ranked[0]) > 0 else None


def _extract_name_from_pending_reference(contexto: List[Dict[str, Any]]) -> Optional[str]:
    for msg in reversed(contexto[-10:]):
        if str(msg.get("tipo") or "") != "ia":
            continue
        content = str(msg.get("conteudo") or "")
        match = re.search(r'voce se refere a\s+"([^"]+)"', content, flags=re.IGNORECASE)
        if match:
            return str(match.group(1)).strip()
    return None


def _clean_client_name_candidate(value: str) -> Optional[str]:
    candidate = re.sub(r"[\]\[\)\(\.,;:!?]+$", "", str(value or "").strip())
    candidate = re.sub(r"\s+", " ", candidate).strip()
    normalized = _normalize_key(candidate)
    if not candidate or normalized in {"ele", "ela", "dele", "dela", "todos", "ativos", "encerrados"}:
        return None
    return candidate


def _is_waiting_client_name_for_contracts(contexto: List[Dict[str, Any]]) -> bool:
    for msg in reversed(contexto[-6:]):
        if str(msg.get("tipo") or "") != "ia":
            continue
        normalized = _normalize_key(str(msg.get("conteudo") or ""))
        if not normalized:
            continue
        if "informe o nome do cliente" in normalized and "contrato" in normalized:
            return True
        if "qual cliente" in normalized and "contrato" in normalized:
            return True
    return False


def _is_waiting_client_name_for_detail(contexto: List[Dict[str, Any]]) -> bool:
    for msg in reversed(contexto[-6:]):
        if str(msg.get("tipo") or "") != "ia":
            continue
        normalized = _normalize_key(str(msg.get("conteudo") or ""))
        if not normalized:
            continue
        if "dados completos desse cliente" in normalized:
            return True
        if "dados do cliente" in normalized and any(token in normalized for token in ("quer", "deseja", "mostro")):
            return True
        if "mostrar dados" in normalized and "cliente" in normalized:
            return True
    return False


def _extract_last_client_name_from_context(contexto: List[Dict[str, Any]]) -> Optional[str]:
    ia_patterns = (
        r"contratos emitidos para\s+([^:\n]+)",
        r"resumo do cliente\s+([^:\n]+)",
        r"o cliente\s+([^.,\n]+?)\s+tem\s+\d+",
        r"consulta executada:\s*([^.,\n]+?)\s+tem\s+\d+",
    )
    for msg in reversed(contexto[-14:]):
        content = str(msg.get("conteudo") or "").strip()
        if not content:
            continue
        tipo = str(msg.get("tipo") or "")
        if tipo == "usuario":
            candidate = (
                extract_client_name_for_contract_query(content)
                or extract_client_name_for_detail_query(content)
            )
            cleaned = _clean_client_name_candidate(candidate or "")
            if cleaned:
                return cleaned
            continue
        if tipo == "ia":
            quoted = re.search(r'cliente\s+"([^"]+)"', content, flags=re.IGNORECASE)
            if quoted:
                cleaned = _clean_client_name_candidate(str(quoted.group(1)))
                if cleaned:
                    return cleaned
            for pattern in ia_patterns:
                match = re.search(pattern, content, flags=re.IGNORECASE)
                if not match:
                    continue
                cleaned = _clean_client_name_candidate(str(match.group(1)))
                if cleaned:
                    return cleaned
    return None


def _find_best_client_match_by_message(items: List[Dict[str, Any]], raw_message: str) -> Optional[Dict[str, Any]]:
    if not items:
        return None
    normalized_message = _normalize_key(raw_message or "")
    if not normalized_message:
        return None

    stopwords = {
        "que", "pra", "para", "mim", "o", "a", "os", "as", "de", "do", "da", "dos", "das",
        "e", "tem", "ele", "ela", "isso", "sim", "contrato", "contratos", "cadastro", "dados",
    }
    tokens = {
        token for token in normalized_message.split()
        if len(token) > 1 and token not in stopwords
    }
    if not tokens:
        return None

    def score(item: Dict[str, Any]) -> int:
        name = _normalize_key(str(item.get("nome") or ""))
        if not name:
            return 0
        name_tokens = set(name.split())
        common = len(tokens.intersection(name_tokens))
        if common <= 0:
            return 0
        # Mais peso para sobreposicao de tokens; bonus quando primeiro token coincide.
        base = common * 20
        first_name = next(iter(name_tokens), "")
        if first_name and first_name in tokens:
            base += 10
        return base

    ranked = sorted(items, key=score, reverse=True)
    return ranked[0] if ranked and score(ranked[0]) > 0 else None


def _format_client_detail(item: Dict[str, Any]) -> str:
    nome = _format_optional(item.get("nome"))
    doc = _format_optional(item.get("documento"))
    telefone = _format_optional(item.get("telefone"))
    email = _format_optional(item.get("email"))
    cidade = _format_optional(item.get("cidade"))
    estado = _format_optional(item.get("estado"))
    endereco = _format_optional(item.get("endereco"))
    observacoes = _format_optional(item.get("observacoes"))
    total_contratos = int(item.get("total_contratos") or 0)

    return "\n".join(
        [
            f"Abrindo cadastro de {nome} (dados no sistema):",
            f"- Nome: {nome}",
            f"- CPF/CNPJ: {doc}",
            f"- Telefone: {telefone}",
            f"- E-mail: {email}",
            f"- Cidade/UF: {cidade}/{estado if estado != 'nao informado' else '-'}",
            f"- Endereco: {endereco}",
            f"- Observacoes: {observacoes}",
            f"- Contratos vinculados: {total_contratos}",
        ]
    )


def _format_client_contracts_summary(item: Dict[str, Any], contratos: List[Any]) -> str:
    nome = _format_optional(item.get("nome"))
    doc = _format_optional(item.get("documento"))
    telefone = _format_optional(item.get("telefone"))
    email = _format_optional(item.get("email"))
    cidade = _format_optional(item.get("cidade"))
    estado = _format_optional(item.get("estado"))
    endereco = _format_optional(item.get("endereco"))

    lines = [
        f"Resumo do cliente {nome}:",
        "- Cadastro:",
        f"  - Nome: {nome}",
        f"  - CPF/CNPJ: {doc}",
        f"  - Telefone: {telefone}",
        f"  - E-mail: {email}",
        f"  - Cidade/UF: {cidade}/{estado if estado != 'nao informado' else '-'}",
        f"  - Endereco: {endereco}",
    ]

    ativos = []
    for contrato in contratos:
        status_value = getattr(getattr(contrato, "status", None), "value", getattr(contrato, "status", ""))
        if str(status_value).lower().strip() == "cancelado":
            continue
        ativos.append(contrato)

    lines.append("- Contratos ativos:")
    if not ativos:
        lines.append("  - Nenhum contrato ativo encontrado.")
    else:
        for contrato in ativos:
            numero = str(getattr(contrato, "numero", "") or "sem numero")
            titulo = str(getattr(contrato, "template_nome", "") or getattr(contrato, "template_id", "") or "Contrato sem titulo")
            status_value = getattr(getattr(contrato, "status", None), "value", getattr(contrato, "status", ""))
            created_at = getattr(contrato, "created_at", None)
            created_label = created_at.strftime("%d/%m/%Y") if created_at else "sem data"
            lines.append(f"  - {numero} | {titulo} | {created_label} | {status_value}")

    return "\n".join(lines)


def _is_count_contracts_request(message: str) -> bool:
    normalized = _normalize_key(message or "")
    has_contract = "contrato" in normalized or "contratos" in normalized
    has_count = any(token in normalized for token in ("quantos", "quantidade", "total", "qtd", "numero"))
    return has_contract and has_count


def _is_count_clients_request(message: str) -> bool:
    normalized = _normalize_key(message or "")
    has_client = "cliente" in normalized or "clientes" in normalized
    has_count = any(token in normalized for token in ("quantos", "quantidade", "total", "qtd", "numero"))
    return has_client and has_count


def _wants_all_records(message: str) -> bool:
    normalized = _normalize_key(message or "")
    return any(token in normalized for token in ("todos", "todas", "geral", "emitidos", "incluindo"))


async def _resolve_client_from_message(
    *,
    cliente_service: ClienteService,
    message: str,
    contexto_efetivo: List[Dict[str, Any]],
    explicit_name: Optional[str] = None,
    allow_context_fallback: bool = False,
) -> Optional[Dict[str, Any]]:
    requested_name = explicit_name or (
        extract_client_name_for_contract_query(message) or extract_client_name_for_detail_query(message)
    )
    if not requested_name and _is_direct_confirmation(message):
        requested_name = _extract_name_from_pending_reference(contexto_efetivo)
    if allow_context_fallback and (
        not requested_name or _normalize_key(str(requested_name)) in {"ele", "ela", "dele", "dela"}
    ):
        requested_name = _extract_last_client_name_from_context(contexto_efetivo)

    items: List[Dict[str, Any]] = []
    if requested_name:
        payload = await cliente_service.list(search=requested_name, page=1, page_size=200)
        items = list(payload.get("items", []))
    if not items:
        payload = await cliente_service.list(search=None, page=1, page_size=200)
        items = list(payload.get("items", []))
    if not items:
        return None

    best = _find_best_client_match(items, requested_name or "") if requested_name else None
    if not best:
        best = _find_best_client_match_by_message(items, message)
    return best


class VivaDomainQueryRouterService:
    async def handle_domain_query(
        self,
        *,
        db: Any,
        user_id: UUID,
        message: str,
        contexto_efetivo: List[Dict[str, Any]],
    ) -> Optional[str]:
        _ = user_id
        pending_list_domain = _last_pending_list_domain(contexto_efetivo)

        if is_visual_proof_request(message):
            return (
                "Nao uso print/anexo como prova de dado neste fluxo. "
                "Para confirmar com fonte de verdade, consulto direto o cadastro no sistema. "
                "Me diga: 'abrir cadastro do cliente <nome>'."
            )

        combined_client_contract_intent = is_client_profile_contracts_intent(message)
        if combined_client_contract_intent:
            cliente_service = ClienteService(db)
            best = await _resolve_client_from_message(
                cliente_service=cliente_service,
                message=message,
                contexto_efetivo=contexto_efetivo,
                allow_context_fallback=True,
            )
            if not best:
                return "Nao encontrei cliente para montar o resumo de cadastro e contratos."
            cliente_id = best.get("id")
            filtered_items = await cliente_service.get_contratos(cliente_id) if cliente_id else []
            return _format_client_contracts_summary(best, filtered_items)

        explicit_contract_client_name = (
            extract_client_name_for_contract_query(message) or extract_client_name_for_detail_query(message)
        )
        waiting_client_name_for_contracts = _is_waiting_client_name_for_contracts(contexto_efetivo)
        context_client_name = _extract_last_client_name_from_context(contexto_efetivo)
        contract_templates_intent = is_contract_templates_intent(message)
        contracts_by_client_intent = is_contracts_by_client_intent(message)
        if not contracts_by_client_intent and waiting_client_name_for_contracts and explicit_contract_client_name:
            contracts_by_client_intent = True
        if (
            not contracts_by_client_intent
            and pending_list_domain == "contratos_emitidos"
            and _is_direct_confirmation(message)
            and context_client_name
        ):
            contracts_by_client_intent = True
        contract_count_intent = _is_count_contracts_request(message) and not contracts_by_client_intent
        contract_list_intent = (is_contract_list_intent(message) and not contract_templates_intent) or (
            _is_direct_confirmation(message) and pending_list_domain == "contratos_emitidos"
        )
        contract_templates_intent = contract_templates_intent or (
            _is_direct_confirmation(message) and pending_list_domain == "contratos_modelos"
        )
        if contracts_by_client_intent or contract_list_intent or contract_templates_intent or contract_count_intent:
            contrato_service = ContratoService(db)
            if contracts_by_client_intent:
                cliente_service = ClienteService(db)
                best = await _resolve_client_from_message(
                    cliente_service=cliente_service,
                    message=message,
                    contexto_efetivo=contexto_efetivo,
                    explicit_name=explicit_contract_client_name or context_client_name,
                    allow_context_fallback=True,
                )
                if not best:
                    return "Informe o nome do cliente para eu listar os contratos emitidos."

                client_name = _normalize_mojibake_text(best.get("nome") or "cliente").strip()
                cliente_id = best.get("id")
                filtered_items = await cliente_service.get_contratos(cliente_id) if cliente_id else []
                if not filtered_items:
                    return f"Nao encontrei contratos emitidos para o cliente {client_name}."

                ativos = [
                    item
                    for item in filtered_items
                    if str(getattr(getattr(item, "status", None), "value", getattr(item, "status", ""))).lower().strip()
                    != "cancelado"
                ]
                if _is_count_contracts_request(message):
                    return f"O cliente {client_name} tem {len(ativos)} contratos ativos e {len(filtered_items)} contratos emitidos no total."

                lines = [f"Contratos emitidos para {client_name}:"]
                for item in filtered_items:
                    numero = str(getattr(item, "numero", "") or "sem numero")
                    titulo = _normalize_mojibake_text(
                        getattr(item, "template_nome", "") or getattr(item, "template_id", "") or ""
                    ).strip()
                    if not titulo:
                        titulo = "Contrato sem titulo"
                    status_value = getattr(getattr(item, "status", None), "value", getattr(item, "status", ""))
                    created_at = getattr(item, "created_at", None)
                    created_label = created_at.strftime("%d/%m/%Y") if created_at else "sem data"
                    lines.append(f"- {numero} | {titulo} | {created_label} | {status_value}")
                return "\n".join(lines)
            if contract_count_intent:
                contratos_data = await contrato_service.list(
                    status=None,
                    search=None,
                    page=1,
                    page_size=500,
                )
                contratos_items = list(contratos_data.get("items", []))
                total = len(contratos_items)
                ativos = [
                    item
                    for item in contratos_items
                    if str(getattr(getattr(item, "status", None), "value", getattr(item, "status", ""))).lower().strip()
                    != "cancelado"
                ]
                if _wants_all_records(message):
                    return f"Total de contratos emitidos (todos os status): {total}."
                return f"Total de contratos ativos: {len(ativos)}. Total emitido geral: {total}."

            if contract_templates_intent:
                templates = await contrato_service.list_templates()
                titles = [
                    _normalize_mojibake_text(item.get("nome") or "").strip()
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
                        title = _normalize_mojibake_text(getattr(item, "template_nome", "") or "").strip()
                        if not title:
                            title = _normalize_mojibake_text(getattr(item, "template_id", "") or "").strip()
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
                    title = _normalize_mojibake_text(getattr(item, "template_nome", "") or "").strip()
                    if not title:
                        title = _normalize_mojibake_text(getattr(item, "template_id", "") or "").strip() or "Contrato sem titulo"
                    if title not in seen:
                        seen.add(title)
                        titles.append(title)

                lines = ["Titulos dos contratos registrados:"]
            lines.extend(f"- {title}" for title in titles)
            return "\n".join(lines)

        waiting_client_name_for_detail = _is_waiting_client_name_for_detail(contexto_efetivo)
        explicit_detail_client_name = (
            extract_client_name_for_detail_query(message) or extract_client_name_for_contract_query(message)
        )
        client_detail_intent = is_client_detail_intent(message) or (
            waiting_client_name_for_detail and bool(explicit_detail_client_name)
        )
        if client_detail_intent:
            cliente_service = ClienteService(db)
            best = await _resolve_client_from_message(
                cliente_service=cliente_service,
                message=message,
                contexto_efetivo=contexto_efetivo,
                explicit_name=explicit_detail_client_name,
                allow_context_fallback=True,
            )
            if not best:
                return "Nao encontrei cliente com esse nome."
            return _format_client_detail(best)

        client_count_intent = _is_count_clients_request(message)
        client_list_intent = is_client_list_intent(message) or (
            _is_direct_confirmation(message) and pending_list_domain == "clientes"
        )
        if client_count_intent or client_list_intent:
            cliente_service = ClienteService(db)
            payload = await cliente_service.list(search=None, page=1, page_size=200)
            clients = list(payload.get("items", []))
            if not clients:
                return "Nao ha clientes registrados no sistema."
            if client_count_intent:
                return f"Total de clientes registrados: {len(clients)}."
            lines = ["Clientes registrados:"]
            for item in clients:
                if isinstance(item, dict):
                    nome = _normalize_mojibake_text(item.get("nome") or "").strip()
                else:
                    nome = _normalize_mojibake_text(getattr(item, "nome", "") or "").strip()
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

        if is_campaign_list_intent(message):
            mode_filter = extract_campaign_mode_filter(message)
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
                lines.append(f"- {_normalize_mojibake_text(row.titulo)} ({row.modo}) - {created_label}")
            return "\n".join(lines)
        if is_campaign_count_intent(message):
            normalized = _normalize_key(message or "")
            mode_filter = extract_campaign_mode_filter(message)
            _, total = await viva_campaign_repository_service.list_campaign_rows(
                db=db,
                user_id=user_id,
                modo=mode_filter,
                limit=1,
                offset=0,
            )
            asks_active = any(token in normalized for token in ("ativa", "ativas", "ativva", "ativo", "ativos"))
            if asks_active:
                scope = f" em {mode_filter}" if mode_filter else ""
                return (
                    f"No historico{scope}, encontrei {total} campanhas registradas. "
                    "Obs.: o modulo atual nao classifica campanhas por status ativo/pausado."
                )
            if mode_filter:
                return f"Total de campanhas feitas em {mode_filter}: {total}."
            return f"Total geral de campanhas feitas: {total}."

        return None



def _is_services_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    return (
        ("servico" in normalized or "servicos" in normalized)
        and any(token in normalized for token in ("nossos", "empresa", "saas", "quais"))
    )


viva_domain_query_router_service = VivaDomainQueryRouterService()

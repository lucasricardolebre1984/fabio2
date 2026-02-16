"""Generate institutional audit matrix for menu -> front -> API -> DB -> COFRE.

Usage:
    python backend/scripts/generate_institutional_audit.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Dict, List, Set, Tuple


@dataclass(frozen=True)
class MenuItem:
    href: str
    label: str


REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ROOT = REPO_ROOT / "frontend" / "src"
BACKEND_ROOT = REPO_ROOT / "backend"
COFRE_ROOT = BACKEND_ROOT / "COFRE"
DOCS_AUDIT_DIR = REPO_ROOT / "docs" / "AUDIT"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_endpoint(raw: str) -> str:
    endpoint = (raw or "").strip()
    if not endpoint:
        return endpoint
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    endpoint = endpoint.split("?")[0]
    endpoint = endpoint.replace("\\", "/")
    endpoint = re.sub(r"\$\{[^}]+\}", "{param}", endpoint)
    if endpoint.startswith("/api/v1/"):
        normalized = endpoint
    elif endpoint.startswith("/"):
        normalized = f"/api/v1{endpoint}"
    else:
        normalized = endpoint
    normalized = re.sub(r"/{2,}", "/", normalized)
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


def parse_sidebar_menu(sidebar_path: Path) -> List[MenuItem]:
    text = _read_text(sidebar_path)
    matches = re.findall(r"\{\s*href:\s*'([^']+)'\s*,\s*label:\s*'([^']+)'", text)
    return [MenuItem(href=href, label=label) for href, label in matches]


def parse_frontend_wrapper_map(api_lib_path: Path) -> Dict[str, Dict[str, str]]:
    lines = _read_text(api_lib_path).splitlines()
    current_obj: str | None = None
    depth = 0
    current_method: str | None = None
    wrappers: Dict[str, Dict[str, str]] = {}

    for line in lines:
        start_obj = re.search(r"^export const (\w+) = \{", line)
        if start_obj:
            current_obj = start_obj.group(1)
            wrappers.setdefault(current_obj, {})
            depth = line.count("{") - line.count("}")
            current_method = None
            continue

        if current_obj is None:
            continue

        depth += line.count("{") - line.count("}")

        method_match = re.search(r"^\s*(\w+):\s*async\s*\(", line)
        if method_match:
            current_method = method_match.group(1)
            continue

        endpoint_match = re.search(
            r"api\.(get|post|put|delete|patch)\(\s*([\"'`])([^\"'`]+)\2",
            line,
        )
        if endpoint_match and current_method:
            wrappers[current_obj][current_method] = endpoint_match.group(3)

        if depth <= 0:
            current_obj = None
            current_method = None
            depth = 0

    return wrappers


def _extract_calls_from_file(page_path: Path, wrappers: Dict[str, Dict[str, str]]) -> Set[str]:
    text = _read_text(page_path)
    endpoints: Set[str] = set()

    # direct axios calls
    for match in re.finditer(
        r"(?:^|[\s(])(?:api)\.(?:get|post|put|delete|patch)\(\s*([\"'`])([^\"'`]+)\1",
        text,
        flags=re.MULTILINE,
    ):
        endpoints.add(_normalize_endpoint(match.group(2)))

    # fetch calls
    for match in re.finditer(r"fetch\(\s*([\"'`])([^\"'`]+)\1", text):
        raw = match.group(2)
        if raw.startswith("/api/v1/"):
            endpoints.add(_normalize_endpoint(raw))

    # wrapper calls
    for wrapper, method in re.findall(r"\b(\w+Api)\.(\w+)\(", text):
        endpoint = wrappers.get(wrapper, {}).get(method)
        if endpoint:
            endpoints.add(_normalize_endpoint(endpoint))

    return {ep for ep in endpoints if ep and ep.startswith("/api/v1/")}


def _route_to_pages(route_href: str) -> List[Path]:
    route_name = route_href.strip("/").split("/")[0]
    if not route_name:
        return []
    pages = sorted((FRONTEND_ROOT / "app").glob(f"**/{route_name}/page.tsx"))
    return pages


def collect_frontend_menu_coverage(menus: List[MenuItem], wrappers: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, object]]:
    coverage: Dict[str, Dict[str, object]] = {}
    for menu in menus:
        pages = _route_to_pages(menu.href)
        endpoints: Set[str] = set()
        for page in pages:
            endpoints |= _extract_calls_from_file(page, wrappers)
        coverage[menu.href] = {
            "label": menu.label,
            "pages": [str(path.relative_to(REPO_ROOT)) for path in pages],
            "frontend_endpoints": sorted(endpoints),
        }
    return coverage


def _parse_module_routes_recursive(
    module_file: Path,
    api_dir: Path,
    base_prefix: str,
    routes: Set[str],
    visited: Set[Path],
) -> None:
    module_file = module_file.resolve()
    if module_file in visited or not module_file.exists():
        return
    visited.add(module_file)

    module_text = _read_text(module_file)

    for method, subpath in re.findall(
        r"@router\.(get|post|put|delete|patch)\(\"([^\"]*)\"",
        module_text,
    ):
        _ = method
        full = f"/api/v1{base_prefix}{subpath}"
        full = re.sub(r"/{2,}", "/", full)
        if len(full) > 1 and full.endswith("/"):
            full = full[:-1]
        routes.add(full)

    import_alias_map: Dict[str, str] = {}
    for module_name, alias in re.findall(
        r"from app\.api\.v1\.([a-zA-Z0-9_]+)\s+import\s+router as ([a-zA-Z0-9_]+)",
        module_text,
    ):
        import_alias_map[alias] = module_name

    for alias, nested_prefix in re.findall(
        r"router\.include_router\((\w+)(?:,\s*prefix=\"([^\"]+)\")?",
        module_text,
    ):
        module_name = import_alias_map.get(alias)
        if not module_name:
            continue
        child_file = api_dir / f"{module_name}.py"
        effective_prefix = f"{base_prefix}{nested_prefix or ''}"
        _parse_module_routes_recursive(
            module_file=child_file,
            api_dir=api_dir,
            base_prefix=effective_prefix,
            routes=routes,
            visited=visited,
        )


def parse_backend_routes(router_path: Path, api_dir: Path) -> Set[str]:
    router_text = _read_text(router_path)
    include_matches = re.findall(
        r"include_router\((\w+)\.router,\s*prefix=\"([^\"]+)\"",
        router_text,
    )
    routes: Set[str] = set()
    visited: Set[Path] = set()

    for module_name, prefix in include_matches:
        module_file = api_dir / f"{module_name}.py"
        _parse_module_routes_recursive(
            module_file=module_file,
            api_dir=api_dir,
            base_prefix=prefix,
            routes=routes,
            visited=visited,
        )

    return routes


def endpoint_exists(frontend_endpoint: str, backend_routes: Set[str]) -> bool:
    endpoint = _normalize_endpoint(frontend_endpoint)
    if endpoint in backend_routes:
        return True
    for route in backend_routes:
        route_pattern = "^" + re.sub(r"\{[^/]+\}", r"[^/]+", route) + "$"
        if re.match(route_pattern, endpoint):
            return True
    return False


def collect_db_tables(models_dir: Path, migrations_dir: Path, services_dir: Path) -> Set[str]:
    tables: Set[str] = set()

    for model_file in sorted(models_dir.glob("*.py")):
        text = _read_text(model_file)
        for table_name in re.findall(r"__tablename__\s*=\s*\"([^\"]+)\"", text):
            tables.add(table_name)

    for sql_file in sorted(migrations_dir.glob("*.sql")):
        text = _read_text(sql_file)
        for table_name in re.findall(
            r"CREATE TABLE(?: IF NOT EXISTS)?\s+([a-zA-Z0-9_]+)",
            text,
            flags=re.IGNORECASE,
        ):
            tables.add(table_name.lower())

    for service_file in sorted(services_dir.glob("*.py")):
        text = _read_text(service_file)
        for table_name in re.findall(
            r"CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)",
            text,
            flags=re.IGNORECASE,
        ):
            tables.add(table_name.lower())

    return tables


def collect_cofre_memory_dirs(memories_root: Path) -> Set[str]:
    if not memories_root.exists():
        return set()
    return {child.name for child in memories_root.iterdir() if child.is_dir()}


def collect_manifest_routes(manifest_path: Path) -> Dict[str, object]:
    if not manifest_path.exists():
        return {"domains": [], "modules": []}
    return json.loads(_read_text(manifest_path))


def collect_semantic_checks(orchestrator_path: Path, agenda_nlu_path: Path) -> Dict[str, bool]:
    orchestrator = _read_text(orchestrator_path)
    agenda_nlu = _read_text(agenda_nlu_path)
    return {
        "contracts_list_intent": "_is_contract_list_intent" in orchestrator,
        "contract_templates_intent": "_is_contract_templates_intent" in orchestrator,
        "clients_list_intent": "_is_client_list_intent" in orchestrator,
        "services_catalog_intent": "_is_services_intent" in orchestrator,
        "agenda_guardrail_recent_prompt": "_has_recent_agenda_prompt" in agenda_nlu,
        "agenda_guardrail_simple_confirmation": "_is_simple_confirmation" in agenda_nlu,
    }


def build_menu_db_expectations() -> Dict[str, List[str]]:
    return {
        "viva": ["viva_chat_sessions", "viva_chat_messages", "viva_memory_vectors"],
        "campanhas": ["viva_campanhas"],
        "contratos": ["contratos", "contrato_templates"],
        "clientes": ["clientes"],
        "agenda": ["agenda"],
        "whatsapp": ["whatsapp_conversas", "whatsapp_mensagens"],
    }


def status_for_menu(missing_endpoints: List[str], missing_tables: List[str], missing_cofre_dirs: List[str]) -> str:
    if not missing_endpoints and not missing_tables and not missing_cofre_dirs:
        return "ok"
    if len(missing_endpoints) <= 1 and len(missing_tables) <= 1 and len(missing_cofre_dirs) <= 1:
        return "parcial"
    return "critico"


def generate_report() -> Tuple[Path, Path]:
    sidebar_path = FRONTEND_ROOT / "components" / "layout" / "Sidebar.tsx"
    api_lib_path = FRONTEND_ROOT / "lib" / "api.ts"
    router_path = BACKEND_ROOT / "app" / "api" / "router.py"
    api_dir = BACKEND_ROOT / "app" / "api" / "v1"
    models_dir = BACKEND_ROOT / "app" / "models"
    migrations_dir = BACKEND_ROOT / "migrations"
    services_dir = BACKEND_ROOT / "app" / "services"
    manifest_path = COFRE_ROOT / "system" / "endpoints_manifest.json"
    memories_root = COFRE_ROOT / "memories"
    orchestrator_path = BACKEND_ROOT / "app" / "services" / "viva_chat_orchestrator_service.py"
    agenda_nlu_path = BACKEND_ROOT / "app" / "services" / "viva_agenda_nlu_service.py"

    menus = parse_sidebar_menu(sidebar_path)
    wrappers = parse_frontend_wrapper_map(api_lib_path)
    frontend_cov = collect_frontend_menu_coverage(menus, wrappers)
    backend_routes = parse_backend_routes(router_path, api_dir)
    db_tables = collect_db_tables(models_dir, migrations_dir, services_dir)
    cofre_dirs = collect_cofre_memory_dirs(memories_root)
    manifest = collect_manifest_routes(manifest_path)
    semantic_checks = collect_semantic_checks(orchestrator_path, agenda_nlu_path)
    menu_db_expectations = build_menu_db_expectations()

    menu_rows: List[Dict[str, object]] = []
    for menu in menus:
        route_key = menu.href.strip("/").split("/")[0]
        frontend_endpoints = frontend_cov[menu.href]["frontend_endpoints"]
        missing_endpoints = [
            ep for ep in frontend_endpoints if not endpoint_exists(ep, backend_routes)
        ]
        expected_tables = menu_db_expectations.get(route_key, [])
        missing_tables = [table for table in expected_tables if table not in db_tables]
        missing_cofre_dirs = [table for table in expected_tables if table not in cofre_dirs]
        row = {
            "menu": menu.label,
            "href": menu.href,
            "pages": frontend_cov[menu.href]["pages"],
            "frontend_endpoints": frontend_endpoints,
            "missing_backend_endpoints": missing_endpoints,
            "expected_tables": expected_tables,
            "missing_db_tables": missing_tables,
            "missing_cofre_dirs": missing_cofre_dirs,
            "status": status_for_menu(missing_endpoints, missing_tables, missing_cofre_dirs),
        }
        menu_rows.append(row)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "menu -> frontend -> backend -> db -> cofre -> semantic",
        "menu_matrix": menu_rows,
        "backend_routes_total": len(backend_routes),
        "backend_routes": sorted(backend_routes),
        "db_tables_total": len(db_tables),
        "db_tables": sorted(db_tables),
        "cofre_memory_dirs_total": len(cofre_dirs),
        "cofre_memory_dirs": sorted(cofre_dirs),
        "manifest_summary": {
            "version": manifest.get("version"),
            "capabilities": len(manifest.get("capabilities", [])),
            "modules": len(manifest.get("modules", [])),
        },
        "semantic_checks": semantic_checks,
    }

    DOCS_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DOCS_AUDIT_DIR / "menu-endpoint-matrix.json"
    md_path = DOCS_AUDIT_DIR / "menu-endpoint-matrix.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Auditoria Institucional: Menu -> API -> Banco -> COFRE")
    lines.append("")
    lines.append(f"Gerado em: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Veredito por menu")
    lines.append("")
    lines.append("| Menu | Rota | Status | Endpoints faltando | Tabelas faltando | COFRE faltando |")
    lines.append("|---|---|---|---:|---:|---:|")
    for row in menu_rows:
        lines.append(
            f"| {row['menu']} | `{row['href']}` | `{row['status']}` | "
            f"{len(row['missing_backend_endpoints'])} | {len(row['missing_db_tables'])} | {len(row['missing_cofre_dirs'])} |"
        )

    lines.append("")
    lines.append("## Checks semanticos (VIVA)")
    lines.append("")
    for key, value in semantic_checks.items():
        mark = "OK" if value else "FALTA"
        lines.append(f"- `{key}`: {mark}")

    lines.append("")
    lines.append("## Detalhes por menu")
    lines.append("")
    for row in menu_rows:
        lines.append(f"### {row['menu']} (`{row['href']}`)")
        lines.append(f"- Status: `{row['status']}`")
        pages = row["pages"] or []
        lines.append(f"- Pages: {', '.join(f'`{p}`' for p in pages) if pages else 'nenhuma encontrada'}")
        frontend_endpoints = row["frontend_endpoints"] or []
        lines.append(
            f"- Frontend endpoints: {', '.join(f'`{ep}`' for ep in frontend_endpoints) if frontend_endpoints else 'nenhum detectado'}"
        )
        missing_endpoints = row["missing_backend_endpoints"] or []
        lines.append(
            f"- Missing backend endpoints: {', '.join(f'`{ep}`' for ep in missing_endpoints) if missing_endpoints else 'nenhum'}"
        )
        expected_tables = row["expected_tables"] or []
        lines.append(
            f"- Expected DB tables: {', '.join(f'`{tb}`' for tb in expected_tables) if expected_tables else 'na'}"
        )
        missing_tables = row["missing_db_tables"] or []
        lines.append(
            f"- Missing DB tables: {', '.join(f'`{tb}`' for tb in missing_tables) if missing_tables else 'nenhuma'}"
        )
        missing_cofre_dirs = row["missing_cofre_dirs"] or []
        lines.append(
            f"- Missing COFRE dirs: {', '.join(f'`{tb}`' for tb in missing_cofre_dirs) if missing_cofre_dirs else 'nenhuma'}"
        )
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    json_report, md_report = generate_report()
    print(f"JSON: {json_report}")
    print(f"MD: {md_report}")

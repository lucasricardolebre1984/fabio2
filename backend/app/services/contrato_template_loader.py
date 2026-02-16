"""Shared contract template loader."""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def _candidate_template_dirs() -> List[Path]:
    candidates: List[Path] = []

    env_dir = os.getenv("CONTRATOS_TEMPLATES_DIR", "").strip()
    if env_dir:
        candidates.append(Path(env_dir))

    service_file = Path(__file__).resolve()
    candidates.extend(
        [
            service_file.parents[3] / "contratos" / "templates",
            service_file.parents[2] / "contratos" / "templates",
            Path("C:/projetos/fabio2/contratos/templates"),
            Path("C:/projetos/fabio2/backend/contratos/templates"),
        ]
    )

    unique_candidates: List[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        unique_candidates.append(candidate)

    return unique_candidates


def _normalize_clause(clause: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(clause)
    content = str(normalized.get("conteudo") or "").strip()
    if content:
        return normalized

    paragraphs = normalized.get("paragrafos")
    if isinstance(paragraphs, list):
        lines = [str(line).strip() for line in paragraphs if str(line).strip()]
        normalized["conteudo"] = "\n\n".join(lines)
        return normalized

    if isinstance(paragraphs, str) and paragraphs.strip():
        normalized["conteudo"] = paragraphs.strip()

    return normalized


def _mojibake_score(text: str) -> int:
    markers = ("Ã", "Â", "â", "\ufffd")
    return sum(text.count(marker) for marker in markers)


def _decode_mojibake_once(text: str, source_encoding: str) -> str:
    try:
        return text.encode(source_encoding).decode("utf-8")
    except UnicodeError:
        return text


def _normalize_mojibake_text(value: str) -> str:
    text = str(value or "")
    if not text:
        return ""

    # Fast-path for normal UTF-8 text.
    if _mojibake_score(text) == 0:
        return text

    normalized = text
    for _ in range(2):
        best = normalized
        best_score = _mojibake_score(normalized)

        for encoding in ("cp1252", "latin-1"):
            candidate = _decode_mojibake_once(normalized, encoding)
            candidate_score = _mojibake_score(candidate)
            if candidate_score < best_score:
                best = candidate
                best_score = candidate_score

        if best == normalized:
            break
        normalized = best

    return normalized


def _normalize_payload_strings(value: Any) -> Any:
    if isinstance(value, str):
        return _normalize_mojibake_text(value)

    if isinstance(value, dict):
        return {key: _normalize_payload_strings(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_normalize_payload_strings(item) for item in value]

    return value


def normalize_template_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _normalize_payload_strings(dict(payload))
    raw_clauses = normalized.get("clausulas")

    if not isinstance(raw_clauses, list):
        return normalized

    clauses: List[Dict[str, Any]] = []
    for clause in raw_clauses:
        if isinstance(clause, dict):
            clauses.append(_normalize_clause(clause))

    normalized["clausulas"] = clauses
    return normalized


def load_contract_template(template_id: str) -> Optional[Dict[str, Any]]:
    template_key = str(template_id or "").strip().lower()
    if not template_key:
        return None

    for templates_dir in _candidate_template_dirs():
        template_path = templates_dir / f"{template_key}.json"
        if not template_path.exists():
            continue
        try:
            with open(template_path, "r", encoding="utf-8") as file:
                payload = json.load(file)
            if isinstance(payload, dict):
                return normalize_template_payload(payload)
        except Exception:
            continue

    return None


def list_contract_templates_from_files() -> List[Dict[str, Any]]:
    templates: Dict[str, Dict[str, Any]] = {}
    for templates_dir in _candidate_template_dirs():
        if not templates_dir.exists() or not templates_dir.is_dir():
            continue
        for template_path in templates_dir.glob("*.json"):
            try:
                with open(template_path, "r", encoding="utf-8") as file:
                    payload = json.load(file)
                if not isinstance(payload, dict):
                    continue
                normalized = normalize_template_payload(payload)
                template_id = str(normalized.get("id") or template_path.stem).strip().lower()
                if not template_id:
                    continue
                if template_id in templates:
                    continue
                templates[template_id] = {
                    "id": template_id,
                    "nome": str(normalized.get("nome") or template_id).strip(),
                    "tipo": str(normalized.get("tipo") or template_id).strip() or template_id,
                    "descricao": str(normalized.get("descricao") or "").strip(),
                    "versao": str(normalized.get("versao") or "1.0.0").strip(),
                    "ativo": bool(normalized.get("ativo", True)),
                    "campos": normalized.get("campos", []),
                    "secoes": normalized.get("secoes", []),
                }
            except Exception:
                continue

    return [tpl for tpl in templates.values() if bool(tpl.get("ativo", True))]

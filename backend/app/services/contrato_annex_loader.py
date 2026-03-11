"""Fixed annex loader for contract templates."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


RATING_TEMPLATE_IDS = {
    "aumento_score",
    "rating_convencional",
    "rating_express_pj",
    "rating_full_pj",
}


def _candidate_annex_dirs() -> List[Path]:
    candidates: List[Path] = []

    env_dir = os.getenv("CONTRATOS_ANEXOS_DIR", "").strip()
    if env_dir:
        candidates.append(Path(env_dir))

    service_file = Path(__file__).resolve()
    candidates.extend(
        [
            service_file.parents[3] / "contratos" / "anexos",
            service_file.parents[2] / "contratos" / "anexos",
            Path("C:/projetos/fabio2/contratos/anexos"),
            Path("C:/projetos/fabio2/backend/contratos/anexos"),
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


def _read_annex_file(filename: str) -> str:
    for annex_dir in _candidate_annex_dirs():
        annex_path = annex_dir / filename
        if not annex_path.exists():
            continue
        try:
            return annex_path.read_text(encoding="utf-8")
        except OSError:
            continue
    return ""


def list_fixed_annexes_for_template(template_id: str) -> List[Dict[str, Any]]:
    template_key = str(template_id or "").strip().lower()
    if not template_key:
        return []

    annexes: List[Dict[str, Any]] = []

    geral_content = _read_annex_file("TERMODECIENCIAGERAL.md")
    if geral_content:
        annexes.append(
            {
                "id": "termo_ciencia_geral",
                "nome": "TERMO DE CIENCIA GERAL",
                "arquivo": "TERMODECIENCIAGERAL.md",
                "conteudo_markdown": geral_content,
                "escopo": "todos_contratos",
                "ordem": 1,
            }
        )

    if template_key in RATING_TEMPLATE_IDS:
        rating_content = _read_annex_file("TERMODECIENCIARATING.md")
        if rating_content:
            annexes.append(
                {
                    "id": "termo_ciencia_rating",
                    "nome": "TERMO DE CIENCIA RATING",
                    "arquivo": "TERMODECIENCIARATING.md",
                    "conteudo_markdown": rating_content,
                    "escopo": "contratos_rating",
                    "ordem": 2,
                }
            )

    return annexes

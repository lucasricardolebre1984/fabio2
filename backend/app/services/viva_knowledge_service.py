"""
Knowledge loader for Viviane (WhatsApp VIVA).
Reads editable business files from frontend/src/app/viva/REGRAS.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import csv
import logging
import os
from pathlib import Path
import re
import unicodedata
from typing import Dict, List, Optional


def _normalize(text: str) -> str:
    value = (text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", value)


def _repo_root() -> Path:
    # backend/app/services -> repo root
    return Path(__file__).resolve().parents[3]


def _to_decimal(raw: str) -> Optional[Decimal]:
    if raw is None:
        return None

    value = str(raw).strip()
    if not value:
        return None

    value = value.replace("R$", "").replace(" ", "")
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")

    if not re.fullmatch(r"-?\d+(\.\d+)?", value):
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _format_brl(value: Decimal) -> str:
    amount = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    inteiro, _, centavos = f"{amount:.2f}".partition(".")
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    return f"R$ {inteiro},{centavos}"


@dataclass
class ServiceInfo:
    name: str
    price_raw: str
    price_base: Optional[Decimal]
    price_offer: Optional[Decimal]
    is_simple: bool
    should_handoff_when_closing: bool

    @property
    def price_label(self) -> str:
        if self.price_offer is not None:
            return _format_brl(self.price_offer)
        return self.price_raw or "Sob consulta"


class VivaKnowledgeService:
    """Loads service descriptions and price table from editable files."""

    OFFER_MARGIN = Decimal("0.15")
    SIMPLE_SERVICE_KEYS = ("limpa nome", "aumento de score", "rating")

    COMPLEX_SERVICE_KEYS = (
        "bacen",
        "cadin",
        "ccf",
        "juros abusivo",
        "revisional",
        "cnh",
        "multa",
        "jusbrasil",
        "escavador",
        "kit banco",
    )

    SERVICE_ALIASES: Dict[str, List[str]] = {
        "limpa nome standart": ["limpa nome", "nome sujo", "limpar nome"],
        "limpa nome exoress": ["limpa nome express", "limpa nome expresso"],
        "aumento de score": ["aumento de score", "subir score", "score baixo"],
        "rating pf e pj": ["rating", "rating empresarial", "rating pj", "rating pf"],
        "rating full": ["rating full", "triplo aaa", "aaa"],
        "bacen": ["bacen", "scr", "prejuizo no banco central"],
        "cadin": ["cadin", "divida uniao", "cnd"],
        "cnh": ["cnh", "cassada", "suspensa", "multa"],
        "juros abusivo": ["juros abusivo", "acao revisional", "revisional"],
        "jusbrasil": ["jusbrasil", "escavador", "desindexar processo"],
        "kit banco": ["kit banco"],
    }

    def __init__(self) -> None:
        self.rules_dir = self._resolve_rules_dir()
        self.services_file = self.rules_dir / "Descrição_Detalhada_dos_Serviços_Rezeta_Brasil.md"
        self.prices_file = self._resolve_price_file()
        self.services_text = ""
        self.services: List[ServiceInfo] = []
        self.services_by_name: Dict[str, ServiceInfo] = {}
        self._rules_mtime = 0.0
        self._prices_mtime = 0.0
        self.reload()

    def _resolve_rules_dir(self) -> Path:
        env_dir = os.getenv("VIVA_RULES_DIR")
        candidates = []
        if env_dir:
            candidates.append(Path(env_dir))
        candidates.extend(
            [
                Path("/app/viva_rules"),
                _repo_root() / "frontend" / "src" / "app" / "viva" / "REGRAS",
                _repo_root().parent / "frontend" / "src" / "app" / "viva" / "REGRAS",
            ]
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        # Keep deterministic path even if missing (warnings will indicate)
        return candidates[0]

    def _resolve_price_file(self) -> Path:
        direct = self.rules_dir / "tabela_precos_ia_01_planilha1.csv"
        if direct.exists():
            return direct
        matches = sorted(self.rules_dir.glob("tabela_precos_ia_*.csv"))
        if matches:
            return matches[0]
        return direct

    def reload(self) -> None:
        self.services_text = self._load_services_text()
        self.services = self._load_services()
        self.services_by_name = {_normalize(item.name): item for item in self.services}
        self._rules_mtime = self._file_mtime(self.services_file)
        self._prices_mtime = self._file_mtime(self.prices_file)

    def refresh_if_changed(self) -> None:
        latest_rules_mtime = self._file_mtime(self.services_file)
        latest_prices_mtime = self._file_mtime(self.prices_file)
        if latest_rules_mtime != self._rules_mtime or latest_prices_mtime != self._prices_mtime:
            self.reload()

    def _load_services_text(self) -> str:
        if not self.services_file.exists():
            logging.warning("Viviane services file not found: %s", self.services_file)
            return ""
        try:
            text = self.services_file.read_text(encoding="utf-8")
            # Keep a bounded excerpt to avoid large prompts.
            return text[:4500]
        except Exception as exc:
            logging.warning("Unable to read Viviane services file: %s", exc)
            return ""

    def _load_services(self) -> List[ServiceInfo]:
        if not self.prices_file.exists():
            logging.warning("Viviane prices file not found: %s", self.prices_file)
            return []

        loaded: List[ServiceInfo] = []
        try:
            with self.prices_file.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = (row.get("Nome") or "").strip()
                    if not name:
                        continue
                    price_raw = (row.get("Valor") or "").strip()
                    price_base = _to_decimal(price_raw)
                    price_offer = None
                    if price_base is not None:
                        price_offer = price_base * (Decimal("1.0") + self.OFFER_MARGIN)

                    normalized = _normalize(name)
                    is_simple = any(key in normalized for key in self.SIMPLE_SERVICE_KEYS)
                    is_complex = any(key in normalized for key in self.COMPLEX_SERVICE_KEYS)
                    loaded.append(
                        ServiceInfo(
                            name=name,
                            price_raw=price_raw,
                            price_base=price_base,
                            price_offer=price_offer,
                            is_simple=is_simple,
                            should_handoff_when_closing=is_complex,
                        )
                    )
        except Exception as exc:
            logging.exception("Unable to parse Viviane prices CSV: %s", exc)
        return loaded

    def _file_mtime(self, file: Path) -> float:
        try:
            return file.stat().st_mtime
        except Exception:
            return 0.0

    def find_service_from_message(self, message: str) -> Optional[ServiceInfo]:
        text = _normalize(message)
        if not text:
            return None

        for canonical_name, aliases in self.SERVICE_ALIASES.items():
            service = self.services_by_name.get(canonical_name)
            if service and any(alias in text for alias in aliases):
                return service

        for service in self.services:
            name_key = _normalize(service.name)
            if name_key and name_key in text:
                return service
        return None

    def prices_prompt_block(self) -> str:
        if not self.services:
            return "Tabela de precos nao carregada."

        lines: List[str] = []
        for service in self.services:
            tipo = "simples" if service.is_simple else "complexo"
            lines.append(
                f"- {service.name}: faixa inicial {service.price_label} | tipo {tipo}"
            )
        return "\n".join(lines)


viva_knowledge_service = VivaKnowledgeService()

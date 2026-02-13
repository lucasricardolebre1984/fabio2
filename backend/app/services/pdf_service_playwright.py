"""PDF Service using Playwright."""
import base64
import html
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contrato import Contrato
from app.services.contrato_template_loader import load_contract_template


class PDFService:
    """PDF generation service using Playwright."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _load_logo_data_uri() -> Optional[str]:
        possible_paths = [
            Path("C:/projetos/fabio2/contratos/logo2.png"),
            Path(__file__).resolve().parents[3] / "contratos" / "logo2.png",
            Path(__file__).resolve().parents[2] / "contratos" / "logo2.png",
            Path("C:/projetos/fabio2/contratos/logo2.jpeg"),
        ]
        for logo_path in possible_paths:
            try:
                if logo_path.exists():
                    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
                    mime = "image/png" if logo_path.suffix.lower() == ".png" else "image/jpeg"
                    return f"data:{mime};base64,{encoded}"
            except OSError:
                continue
        return None

    @staticmethod
    def _normalize_mojibake_text(value: Optional[str], fallback: str = "") -> str:
        text = str(value or "").strip()
        if not text:
            return fallback
        if PDFService._mojibake_score(text) == 0:
            return text

        normalized = text
        for _ in range(2):
            best = normalized
            best_score = PDFService._mojibake_score(normalized)

            for encoding in ("cp1252", "latin-1"):
                try:
                    candidate = normalized.encode(encoding).decode("utf-8")
                except UnicodeError:
                    continue
                candidate_score = PDFService._mojibake_score(candidate)
                if candidate_score < best_score:
                    best = candidate
                    best_score = candidate_score

            if best == normalized:
                break
            normalized = best

        return normalized or fallback

    @staticmethod
    def _mojibake_score(text: str) -> int:
        markers = ("Ã", "Â", "â", "\ufffd")
        return sum(text.count(marker) for marker in markers)

    @staticmethod
    def _format_currency(value: Any) -> str:
        number = float(value or 0)
        return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _format_document(documento: str) -> str:
        clean = "".join(ch for ch in str(documento or "") if ch.isdigit())
        if len(clean) == 11:
            return f"{clean[:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:]}"
        if len(clean) == 14:
            return f"{clean[:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:]}"
        return str(documento or "")

    @staticmethod
    def _format_date(date_str: str) -> str:
        try:
            dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return str(date_str)

    @staticmethod
    def _format_prazo(value: Any) -> str:
        prazo = int(value or 0)
        return str(prazo) if prazo > 0 else "à vista"

    @staticmethod
    def _format_prazo_extenso(value: Any, extenso: Any) -> str:
        prazo = int(value or 0)
        if prazo <= 0:
            return "à vista"
        return str(extenso or "")

    @staticmethod
    def _normalize_markdown_inline(value: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
        text = re.sub(r"__(.*?)__", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        return text.strip()

    def _replace_tokens(self, value: str, contrato: Contrato) -> str:
        dados_extras = contrato.dados_extras if isinstance(contrato.dados_extras, dict) else {}
        cnh_numero = str(dados_extras.get("cnh_numero") or "-")

        mapped = {
            "[NOME COMPLETO DO CLIENTE]": str(contrato.contratante_nome or ""),
            "[NÚMERO DO DOCUMENTO]": self._format_document(contrato.contratante_documento),
            "[NUMERO DO DOCUMENTO]": self._format_document(contrato.contratante_documento),
            "[E-MAIL DO CLIENTE]": str(contrato.contratante_email or ""),
            "[TELEFONE DO CLIENTE]": str(contrato.contratante_telefone or "-"),
            "[ENDEREÇO COMPLETO DO CLIENTE]": str(contrato.contratante_endereco or ""),
            "[ENDERECO COMPLETO DO CLIENTE]": str(contrato.contratante_endereco or ""),
            "[NÚMERO CNH]": cnh_numero,
            "[NUMERO CNH]": cnh_numero,
            "[VALOR]": self._format_currency(contrato.valor_total),
            "[VALOR EXTENSO]": str(contrato.valor_total_extenso or ""),
            "[VALOR ENTRADA]": self._format_currency(contrato.valor_entrada),
            "[VALOR ENTRADA EXTENSO]": str(contrato.valor_entrada_extenso or ""),
            "[QTD PARCELAS]": str(contrato.qtd_parcelas or ""),
            "[QTD PARCELAS EXTENSO]": str(contrato.qtd_parcelas_extenso or ""),
            "[VALOR PARCELA]": self._format_currency(contrato.valor_parcela),
            "[VALOR PARCELA EXTENSO]": str(contrato.valor_parcela_extenso or ""),
            "[PRAZO 1]": self._format_prazo(contrato.prazo_1),
            "[PRAZO 1 EXTENSO]": self._format_prazo_extenso(contrato.prazo_1, contrato.prazo_1_extenso),
            "[PRAZO 2]": self._format_prazo(contrato.prazo_2),
            "[PRAZO 2 EXTENSO]": self._format_prazo_extenso(contrato.prazo_2, contrato.prazo_2_extenso),
        }

        out = value
        for token, replacement in mapped.items():
            out = out.replace(token, replacement)
        return out

    @staticmethod
    def _load_template_json(template_id: str) -> Optional[Dict[str, Any]]:
        return load_contract_template(template_id)

    def _render_clauses_html(self, contrato: Contrato, clauses: List[Dict[str, Any]]) -> str:
        if not clauses:
            return (
                "<p><strong>CLÁUSULAS</strong><br>"
                "Template sem cláusulas estruturadas para renderização de PDF.</p>"
            )

        blocks: List[str] = []

        for clause in clauses:
            numero = self._normalize_mojibake_text(str(clause.get("numero") or ""))
            titulo = self._normalize_mojibake_text(str(clause.get("titulo") or ""))
            heading = " - ".join(part for part in [numero, titulo] if part)

            content = str(clause.get("conteudo") or "").strip()
            if not content and isinstance(clause.get("paragrafos"), list):
                content = "\n\n".join(
                    str(line).strip()
                    for line in clause["paragrafos"]
                    if str(line).strip()
                )

            raw_content = self._normalize_mojibake_text(content)
            raw_content = self._replace_tokens(raw_content, contrato)

            lines = raw_content.splitlines()
            content_html: List[str] = []
            list_items: List[str] = []

            def flush_list() -> None:
                nonlocal list_items
                if not list_items:
                    return
                item_html = "".join(f"<li>{html.escape(item)}</li>" for item in list_items)
                content_html.append(f"<ul>{item_html}</ul>")
                list_items = []

            for raw_line in lines:
                line = self._normalize_markdown_inline(raw_line)
                if not line or line == "---":
                    flush_list()
                    continue

                if re.match(r"^[-*]\s+", line):
                    list_items.append(re.sub(r"^[-*]\s+", "", line).strip())
                    continue

                flush_list()
                content_html.append(f"<p>{html.escape(line)}</p>")

            flush_list()

            blocks.append(
                "<div class=\"clause-block\">"
                + (f"<p><strong>{html.escape(heading)}</strong></p>" if heading else "")
                + "".join(content_html)
                + "</div>"
            )

        return "".join(blocks)

    async def generate_contrato_pdf(self, contrato_id: UUID) -> Optional[bytes]:
        """Generate PDF for a contract using Playwright."""
        try:
            result = await self.db.execute(select(Contrato).where(Contrato.id == contrato_id))
            contrato = result.scalar_one_or_none()

            if not contrato:
                print(f"Contrato {contrato_id} não encontrado")
                return None

            html_content = self._generate_html(contrato)

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.set_content(html_content)

                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "20mm",
                        "right": "15mm",
                        "bottom": "20mm",
                        "left": "15mm",
                    },
                )

                await browser.close()
                return pdf_bytes

        except Exception as error:
            print(f"ERRO ao gerar PDF: {error}")
            return None

    def _generate_html(self, contrato: Contrato) -> str:
        template_id = str(contrato.template_id or "").lower()
        template_data = self._load_template_json(template_id) or {}

        subtitle = self._normalize_mojibake_text(
            str(template_data.get("subtitulo") or ""),
            "Bacen - Remocao SCR",
        )

        clauses = template_data.get("clausulas") if isinstance(template_data.get("clausulas"), list) else []
        clauses_html = self._render_clauses_html(contrato, clauses)
        dados_extras = contrato.dados_extras if isinstance(contrato.dados_extras, dict) else {}
        extras_html = "".join(
            f"<p><strong>{html.escape(str(key).replace('_', ' ').title())}:</strong> {html.escape(str(value))}</p>"
            for key, value in dados_extras.items()
            if key != "forma_pagamento" and value is not None and str(value).strip()
        )

        logo_data_uri = self._load_logo_data_uri()
        logo_html = (
            f'<img src="{logo_data_uri}" alt="FC Soluções Financeiras" />'
            if logo_data_uri
            else '<span style="font-size:20px;font-weight:700">FC</span>'
        )

        contrato_data = contrato.data_assinatura or self._format_date(contrato.created_at.isoformat())
        local_assinatura = self._normalize_mojibake_text(contrato.local_assinatura, "Ribeirão Preto/SP")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contrato {html.escape(str(contrato.numero))}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 20mm 15mm;
                }}
                body {{
                    font-family: 'Times New Roman', Times, serif;
                    font-size: 12pt;
                    line-height: 1.4;
                    color: #000;
                    max-width: 210mm;
                    margin: 0 auto;
                }}
                .header-band {{
                    background: #1e3a5f;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    gap: 14px;
                    padding: 10px 14px;
                    margin-bottom: 18px;
                }}
                .header-band .logo {{
                    width: 88px;
                    height: 88px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                .header-band .logo img {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    display: block;
                }}
                .header-band h1 {{
                    margin: 0;
                    font-size: 22pt;
                    letter-spacing: 0.2px;
                    font-weight: 700;
                    color: #fff;
                }}
                .title-section {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .title-section h2 {{
                    font-size: 16pt;
                    border-bottom: 2px solid #000;
                    display: inline-block;
                    padding-bottom: 5px;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 11pt;
                    color: #333;
                    margin-top: 8px;
                }}
                .contract-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 11pt;
                }}
                .contract-info span {{
                    margin: 0 15px;
                }}
                .parties {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 15px;
                }}
                .party-box {{
                    border: 2px solid #000;
                    padding: 10px;
                }}
                .party-box h3 {{
                    font-size: 11pt;
                    margin: 0 0 8px 0;
                    border-bottom: 1px solid #999;
                    padding-bottom: 3px;
                }}
                .party-box p {{
                    margin: 2px 0;
                    font-size: 10pt;
                }}
                .intro {{
                    text-align: justify;
                    margin-bottom: 15px;
                    font-size: 11pt;
                }}
                .clauses {{
                    text-align: justify;
                }}
                .clauses p {{
                    margin: 8px 0;
                    text-align: justify;
                }}
                .clauses ul {{
                    margin: 5px 0;
                    padding-left: 25px;
                }}
                .clauses li {{
                    margin: 3px 0;
                }}
                .clause-block {{
                    margin-bottom: 10px;
                }}
                .signatures {{
                    margin-top: 30px;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 50px;
                }}
                .signature {{
                    text-align: center;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    margin-top: 50px;
                    padding-top: 5px;
                }}
                .witnesses {{
                    margin-top: 20px;
                    font-size: 9pt;
                }}
                .witness-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-top: 10px;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #ccc;
                    text-align: center;
                    font-size: 8pt;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header-band">
                <div class="logo">{logo_html}</div>
                <h1>F C Soluções Financeiras</h1>
            </div>

            <div class="title-section">
                <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</h2>
                <div class="subtitle">{html.escape(subtitle)}</div>
            </div>

            <div class="contract-info">
                <span><strong>Nº:</strong> {html.escape(str(contrato.numero))}</span>
                <span><strong>Data:</strong> {html.escape(contrato_data)}</span>
            </div>

            <div class="parties">
                <div class="party-box">
                    <h3>CONTRATANTE</h3>
                    <p><strong>Nome:</strong> {html.escape(str(contrato.contratante_nome or ''))}</p>
                    <p><strong>CPF/CNPJ:</strong> {html.escape(self._format_document(contrato.contratante_documento))}</p>
                    <p><strong>E-mail:</strong> {html.escape(str(contrato.contratante_email or ''))}</p>
                    {f'<p><strong>Contato:</strong> {html.escape(str(contrato.contratante_telefone))}</p>' if contrato.contratante_telefone else ''}
                    <p><strong>Endereço:</strong> {html.escape(str(contrato.contratante_endereco or ''))}</p>
                    {extras_html}
                </div>
                <div class="party-box">
                    <h3>CONTRATADA</h3>
                    <p><strong>Razão Social:</strong> FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</p>
                    <p><strong>CNPJ:</strong> 57.815.628/0001-62</p>
                    <p><strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com</p>
                    <p><strong>Contato:</strong> (16) 99301-7396</p>
                    <p><strong>Endereço:</strong> Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100</p>
                </div>
            </div>

            <div class="intro">
                As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços,
                que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.
            </div>

            <div class="clauses">
                {clauses_html}
                <p>E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias de igual teor e forma.</p>
                <p><strong>{html.escape(local_assinatura)}, {html.escape(contrato_data)}.</strong></p>
            </div>

            <div class="signatures">
                <div class="signature">
                    <div class="signature-line">
                        <strong>{html.escape(str(contrato.contratante_nome or ''))}</strong><br>
                        CPF/CNPJ: {html.escape(self._format_document(contrato.contratante_documento))}<br>
                        <strong>CONTRATANTE</strong>
                    </div>
                </div>
                <div class="signature">
                    <div class="signature-line">
                        <strong>FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</strong><br>
                        CNPJ: 57.815.628/0001-62<br>
                        <strong>CONTRATADA</strong>
                    </div>
                </div>
            </div>

            <div class="witnesses">
                <strong>Testemunhas:</strong>
                <div class="witness-grid">
                    <div>
                        1. _______________________________________<br>
                        Nome:<br>
                        CPF:
                    </div>
                    <div>
                        2. _______________________________________<br>
                        Nome:<br>
                        CPF:
                    </div>
                </div>
            </div>

            <div class="footer">
                FC Soluções Financeiras - CNPJ: 57.815.628/0001-62<br>
                Documento gerado em {datetime.now().strftime('%d/%m/%Y')}
            </div>
        </body>
        </html>
        """

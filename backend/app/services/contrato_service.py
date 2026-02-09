"""Contrato service - Business logic for contracts."""
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, desc, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contrato import Contrato, ContratoStatus
from app.models.cliente import Cliente
from app.models.contrato_template import ContratoTemplate
from app.schemas.contrato import ContratoCreate, ContratoUpdate
from app.services.cliente_service import ClienteService
from app.services.extenso_service import ExtensoService


FALLBACK_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "bacen": {
        "id": "bacen",
        "nome": "Contrato de Adesao ao Bacen",
        "tipo": "bacen",
        "descricao": "Template institucional Bacen",
        "versao": "1.0.0",
        "ativo": True,
        "campos": [],
        "secoes": [],
    },
    "serasa": {
        "id": "serasa",
        "nome": "Contrato de Adesao ao Serasa",
        "tipo": "serasa",
        "descricao": "Template institucional Serasa",
        "versao": "1.0.0",
        "ativo": True,
        "campos": [],
        "secoes": [],
    },
    "protesto": {
        "id": "protesto",
        "nome": "Contrato de Adesao ao Protesto",
        "tipo": "protesto",
        "descricao": "Template institucional Protesto",
        "versao": "1.0.0",
        "ativo": True,
        "campos": [],
        "secoes": [],
    },
    "cadin": {
        "id": "cadin",
        "nome": "Instrumento de PrestaÃ§Ã£o de ServiÃ§os - CADIN PF/PJ",
        "tipo": "cadin",
        "descricao": "Template institucional CADIN PF/PJ",
        "versao": "1.0.0",
        "ativo": True,
        "campos": [],
        "secoes": [],
    },
}

logger = logging.getLogger(__name__)


class ContratoService:
    """Service for contract management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.extenso = ExtensoService()
    
    async def list_templates(self) -> List[Dict[str, Any]]:
        """List available contract templates."""
        result = await self.db.execute(
            select(ContratoTemplate).where(ContratoTemplate.ativo == True)
        )
        templates = result.scalars().all()
        return [
            {
                "id": t.id,
                "nome": t.nome,
                "tipo": t.tipo,
                "descricao": t.descricao,
                "versao": t.versao,
                "ativo": t.ativo,
                "campos": t.campos,
                "secoes": t.secoes,
                "created_at": t.created_at,
                "updated_at": t.updated_at
            }
            for t in templates
        ]
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID."""
        # Try database first
        result = await self.db.execute(
            select(ContratoTemplate).where(ContratoTemplate.tipo == template_id)
        )
        template = result.scalar_one_or_none()
        
        if template:
            return {
                "id": str(template.id),
                "nome": template.nome,
                "tipo": template.tipo,
                "descricao": template.descricao,
                "versao": template.versao,
                "ativo": template.ativo,
                "campos": template.campos,
                "secoes": template.secoes,
                "clausulas": template.clausulas,
                "assinaturas": template.assinaturas,
                "layout": template.layout,
                "contratada_nome": template.contratada_nome,
                "contratada_cnpj": template.contratada_cnpj,
                "contratada_email": template.contratada_email,
                "contratada_endereco": template.contratada_endereco,
                "contratada_telefone": template.contratada_telefone,
                "created_at": template.created_at,
                "updated_at": template.updated_at
            }
        
        # Fallback to JSON file
        possible_paths = [
            Path(__file__).parent.parent.parent / "contratos" / "templates" / f"{template_id}.json",
            Path("C:/projetos/fabio2/contratos/templates") / f"{template_id}.json",
            Path("C:/projetos/fabio2/backend/contratos/templates") / f"{template_id}.json"
        ]
        
        for template_path in possible_paths:
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

        template_fallback = FALLBACK_TEMPLATES.get(template_id.lower())
        if template_fallback:
            return template_fallback
        
        return None

    @staticmethod
    def _normalize_document(documento: str) -> str:
        return (
            (documento or "")
            .replace(".", "")
            .replace("-", "")
            .replace("/", "")
            .strip()
        )

    async def _recalculate_cliente_metrics(self, cliente_id: UUID) -> None:
        result = await self.db.execute(
            select(
                func.count(Contrato.id),
                func.min(Contrato.created_at),
                func.max(Contrato.created_at),
            ).where(Contrato.cliente_id == cliente_id)
        )
        total, primeiro, ultimo = result.one()

        cliente_result = await self.db.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        cliente = cliente_result.scalar_one_or_none()
        if not cliente:
            return

        cliente.total_contratos = int(total or 0)
        cliente.primeiro_contrato_em = primeiro
        cliente.ultimo_contrato_em = ultimo
    
    async def create(self, data: ContratoCreate, user_id: UUID) -> Contrato:
        """Create a new contract."""
        template = await self.get_template(data.template_id)
        if not template:
            raise ValueError(f"Template {data.template_id} nÃ£o encontrado")

        documento_limpo = self._normalize_document(data.contratante_documento)

        valor_total = Decimal(str(data.valor_total))
        valor_entrada = Decimal(str(data.valor_entrada))

        if not data.valor_total_extenso:
            data.valor_total_extenso = self.extenso.valor_por_extenso(valor_total)
        if not data.valor_entrada_extenso:
            data.valor_entrada_extenso = self.extenso.valor_por_extenso(valor_entrada)
        if not data.qtd_parcelas_extenso:
            data.qtd_parcelas_extenso = self.extenso.numero_por_extenso(data.qtd_parcelas)

        if not data.valor_parcela:
            data.valor_parcela = self.extenso.calcular_valor_parcela(
                valor_total, valor_entrada, data.qtd_parcelas
            )
        if not data.valor_parcela_extenso:
            data.valor_parcela_extenso = self.extenso.valor_por_extenso(data.valor_parcela)
        if not data.prazo_1_extenso:
            data.prazo_1_extenso = self.extenso.numero_por_extenso(data.prazo_1)
        if not data.prazo_2_extenso:
            data.prazo_2_extenso = self.extenso.numero_por_extenso(data.prazo_2)

        cliente_service = ClienteService(self.db)
        cliente = await cliente_service.get_by_documento(documento_limpo)

        if not cliente:
            cliente = Cliente(
                nome=data.contratante_nome,
                tipo_pessoa="fisica" if len(documento_limpo) == 11 else "juridica",
                documento=documento_limpo,
                email=data.contratante_email,
                telefone=data.contratante_telefone,
                endereco=data.contratante_endereco,
            )
            self.db.add(cliente)
            await self.db.flush()
        else:
            cliente.nome = data.contratante_nome
            cliente.email = data.contratante_email
            cliente.telefone = data.contratante_telefone
            cliente.endereco = data.contratante_endereco

        numero = await self._generate_numero()

        contrato = Contrato(
            numero=numero,
            status=ContratoStatus.RASCUNHO,
            template_id=data.template_id,
            template_nome=template.get("nome", data.template_id),
            cliente_id=cliente.id,
            contratante_nome=data.contratante_nome,
            contratante_documento=documento_limpo,
            contratante_email=data.contratante_email,
            contratante_telefone=data.contratante_telefone,
            contratante_endereco=data.contratante_endereco,
            valor_total=data.valor_total,
            valor_total_extenso=data.valor_total_extenso,
            valor_entrada=data.valor_entrada,
            valor_entrada_extenso=data.valor_entrada_extenso,
            qtd_parcelas=data.qtd_parcelas,
            qtd_parcelas_extenso=data.qtd_parcelas_extenso,
            valor_parcela=data.valor_parcela,
            valor_parcela_extenso=data.valor_parcela_extenso,
            prazo_1=data.prazo_1,
            prazo_1_extenso=data.prazo_1_extenso,
            prazo_2=data.prazo_2,
            prazo_2_extenso=data.prazo_2_extenso,
            local_assinatura=data.local_assinatura,
            data_assinatura=data.data_assinatura,
            dados_extras=data.dados_extras,
            created_by=user_id,
        )

        self.db.add(contrato)
        await self.db.flush()
        await self._recalculate_cliente_metrics(cliente.id)
        await self.db.commit()
        await self.db.refresh(contrato)

        return contrato
    
    async def _generate_numero(self) -> str:
        """Generate contract number: CNT-YYYY-XXXX"""
        year = datetime.now().year
        prefix = f"CNT-{year}-"

        # Use current max sequence to avoid duplicate numbers when there are gaps.
        result = await self.db.execute(
            select(Contrato.numero)
            .where(Contrato.numero.like(f"{prefix}%"))
            .order_by(desc(Contrato.numero))
            .limit(1)
        )
        ultimo_numero = result.scalar_one_or_none()

        if not ultimo_numero:
            sequencial = 1
        else:
            try:
                sequencial = int(str(ultimo_numero).split("-")[-1]) + 1
            except (TypeError, ValueError):
                sequencial = 1

        return f"CNT-{year}-{sequencial:04d}"
    
    async def list(
        self,
        status: Optional[ContratoStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List contracts with pagination."""
        query = select(Contrato).order_by(desc(Contrato.created_at))
        
        if status:
            query = query.where(Contrato.status == status)
        
        if search:
            search_filter = or_(
                Contrato.contratante_nome.ilike(f"%{search}%"),
                Contrato.numero.ilike(f"%{search}%"),
                Contrato.contratante_documento.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Count total
        count_result = await self.db.execute(
            select(func.count(Contrato.id)).where(
                and_(True, search_filter) if search else True
            )
        )
        total = count_result.scalar()
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_by_id(self, contrato_id: UUID) -> Optional[Contrato]:
        """Get contract by ID."""
        result = await self.db.execute(
            select(Contrato).where(Contrato.id == contrato_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, contrato_id: UUID, data: ContratoUpdate) -> Optional[Contrato]:
        """Update contract."""
        result = await self.db.execute(
            select(Contrato).where(Contrato.id == contrato_id)
        )
        contrato = result.scalar_one_or_none()
        
        if not contrato:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contrato, field, value)
        
        await self.db.commit()
        await self.db.refresh(contrato)
        
        return contrato
    
    async def delete(self, contrato_id: UUID) -> bool:
        """Delete contract."""
        result = await self.db.execute(
            select(Contrato).where(Contrato.id == contrato_id)
        )
        contrato = result.scalar_one_or_none()
        
        if not contrato:
            return False

        cliente_id = contrato.cliente_id
        await self.db.delete(contrato)
        await self.db.flush()
        if cliente_id:
            await self._recalculate_cliente_metrics(cliente_id)
        await self.db.commit()
        
        return True
    
    async def generate_pdf(self, contrato_id: UUID) -> Optional[str]:
        """Generate PDF for contract."""
        contrato = await self.get_by_id(contrato_id)
        if not contrato:
            return None

        pdf_path = self._generate_pdf_via_weasy(contrato)
        if not pdf_path:
            return None

        # Update contract with PDF URL
        relative_path = f"/storage/{os.path.basename(pdf_path)}"
        await self.update(contrato_id, ContratoUpdate(pdf_url=relative_path))

        return relative_path

    async def generate_pdf_bytes(self, contrato_id: UUID) -> Optional[bytes]:
        """Generate PDF bytes for contract (Playwright first, WeasyPrint fallback)."""
        contrato = await self.get_by_id(contrato_id)
        if not contrato:
            return None

        # Primary path: Playwright renderer.
        try:
            from app.services.pdf_service_playwright import PDFService as PlaywrightPDFService

            pdf_service = PlaywrightPDFService(self.db)
            pdf_bytes = await pdf_service.generate_contrato_pdf(contrato_id)
            if pdf_bytes:
                logger.info("PDF gerado via Playwright para contrato %s", contrato_id)
                return pdf_bytes
        except ModuleNotFoundError:
            # Playwright dependency may be absent in some containers.
            logger.info("Playwright indisponivel no runtime. Usando fallback WeasyPrint.")
        except Exception:
            # Any Playwright runtime issue should not block contract download.
            logger.exception("Falha no Playwright para contrato %s. Tentando WeasyPrint.", contrato_id)

        # Fallback path: WeasyPrint renderer.
        pdf_path = self._generate_pdf_via_weasy(contrato)
        if not pdf_path:
            logger.error("Falha no fallback WeasyPrint para contrato %s", contrato_id)
            return None

        try:
            with open(pdf_path, "rb") as pdf_file:
                logger.info("PDF gerado via WeasyPrint para contrato %s em %s", contrato_id, pdf_path)
                return pdf_file.read()
        except OSError:
            logger.exception("Nao foi possivel ler arquivo PDF gerado para contrato %s", contrato_id)
            return None

    @staticmethod
    def _format_brl(value: Any) -> str:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _build_pdf_data(self, contrato: Contrato) -> Dict[str, Any]:
        return {
            "numero": contrato.numero,
            "template_id": contrato.template_id,
            "template_nome": contrato.template_nome,
            "contratante_nome": contrato.contratante_nome,
            "contratante_documento": contrato.contratante_documento,
            "contratante_email": contrato.contratante_email,
            "contratante_telefone": contrato.contratante_telefone,
            "contratante_endereco": contrato.contratante_endereco,
            "valor_total": self._format_brl(contrato.valor_total),
            "valor_total_extenso": contrato.valor_total_extenso,
            "valor_entrada": self._format_brl(contrato.valor_entrada),
            "valor_entrada_extenso": contrato.valor_entrada_extenso,
            "qtd_parcelas": contrato.qtd_parcelas,
            "qtd_parcelas_extenso": contrato.qtd_parcelas_extenso,
            "valor_parcela": self._format_brl(contrato.valor_parcela),
            "valor_parcela_extenso": contrato.valor_parcela_extenso,
            "prazo_1": contrato.prazo_1,
            "prazo_1_extenso": contrato.prazo_1_extenso,
            "prazo_2": contrato.prazo_2,
            "prazo_2_extenso": contrato.prazo_2_extenso,
            "local_assinatura": contrato.local_assinatura,
            "data_assinatura": contrato.data_assinatura,
        }

    def _generate_pdf_via_weasy(self, contrato: Contrato) -> Optional[str]:
        try:
            from app.services.pdf_service import PDFService as WeasyPDFService

            pdf_service = WeasyPDFService()
            dados = self._build_pdf_data(contrato)
            return pdf_service.generate_contrato_bacen(contrato.id, dados)
        except Exception:
            logger.exception("WeasyPrint falhou na geracao do contrato %s", contrato.id)
            return None



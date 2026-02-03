"""Contrato service - Business logic for contracts."""
import json
import os
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contrato import Contrato, ContratoStatus
from app.models.cliente import Cliente
from app.models.contrato_template import ContratoTemplate
from app.schemas.contrato import ContratoCreate, ContratoUpdate
from app.services.extenso_service import ExtensoService
# from app.services.pdf_service import PDFService  # WeasyPrint disabled
# from app.services.pdf_service_playwright import PDFService  # Playwright
from app.services.pdf_service_stub import PDFService  # Using stub - WORKING


class ContratoService:
    """Service for contract management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.extenso = ExtensoService()
        self.pdf = PDFService()
    
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
        # First try database
        result = await self.db.execute(
            select(ContratoTemplate).where(
                and_(
                    ContratoTemplate.tipo == template_id,
                    ContratoTemplate.ativo == True
                )
            )
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
                "created_at": template.created_at,
                "updated_at": template.updated_at
            }
        
        # Fallback to JSON file - try multiple paths
        possible_paths = [
            Path.cwd() / "contratos" / "templates" / f"{template_id}.json",
            Path.cwd().parent / "contratos" / "templates" / f"{template_id}.json",
            Path("c:/projetos/fabio2/contratos/templates") / f"{template_id}.json",
        ]
        
        for template_path in possible_paths:
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    async def generate_numero(self) -> str:
        """Generate contract number (CNT-YYYY-XXXX)."""
        year = datetime.now().year
        
        # Count contracts this year
        result = await self.db.execute(
            select(func.count(Contrato.id)).where(
                func.extract('year', Contrato.created_at) == year
            )
        )
        count = result.scalar() + 1
        
        return f"CNT-{year}-{count:04d}"
    
    async def create(self, data: ContratoCreate, user_id: UUID) -> Contrato:
        """Create a new contract and auto-create client if needed."""
        # Get template
        template = await self.get_template(data.template_id)
        if not template:
            raise ValueError(f"Template {data.template_id} não encontrado")
        
        # Calculate extenso values if not provided
        valor_total = Decimal(str(data.valor_total))
        valor_entrada = Decimal(str(data.valor_entrada))
        
        if not data.valor_total_extenso:
            data.valor_total_extenso = self.extenso.valor_por_extenso(valor_total)
        if not data.valor_entrada_extenso:
            data.valor_entrada_extenso = self.extenso.valor_por_extenso(valor_entrada)
        if not data.qtd_parcelas_extenso:
            data.qtd_parcelas_extenso = self.extenso.numero_por_extenso(data.qtd_parcelas)
        
        # Calculate parcela if not provided
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
        
        # Find or create client
        cliente_result = await self.db.execute(
            select(Cliente).where(Cliente.documento == data.contratante_documento)
        )
        cliente = cliente_result.scalar_one_or_none()
        
        if not cliente:
            # Create new client
            cliente = Cliente(
                nome=data.contratante_nome,
                tipo_pessoa="fisica" if len(data.contratante_documento) <= 14 else "juridica",
                documento=data.contratante_documento,
                email=data.contratante_email,
                telefone=data.contratante_telefone,
                endereco=data.contratante_endereco,
                primeiro_contrato_em=datetime.now(),
                ultimo_contrato_em=datetime.now(),
                total_contratos=1
            )
            self.db.add(cliente)
            await self.db.flush()
        else:
            # Update client
            cliente.nome = data.contratante_nome
            cliente.email = data.contratante_email
            cliente.telefone = data.contratante_telefone
            cliente.endereco = data.contratante_endereco
            cliente.ultimo_contrato_em = datetime.now()
            cliente.total_contratos += 1
        
        # Create contract
        contrato = Contrato(
            numero=await self.generate_numero(),
            template_id=data.template_id,
            template_nome=template["nome"],
            status=ContratoStatus.RASCUNHO,
            
            # Cliente
            cliente_id=cliente.id,
            
            # Contratante
            contratante_nome=data.contratante_nome,
            contratante_documento=data.contratante_documento,
            contratante_email=data.contratante_email,
            contratante_telefone=data.contratante_telefone,
            contratante_endereco=data.contratante_endereco,
            
            # Valores
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
            
            # Assinatura
            local_assinatura=data.local_assinatura,
            data_assinatura=data.data_assinatura,
            
            # Extras
            dados_extras=data.dados_extras,
            
            # User
            created_by=user_id
        )
        
        self.db.add(contrato)
        await self.db.commit()
        await self.db.refresh(contrato)
        
        return contrato
    
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
            query = query.where(
                or_(
                    Contrato.numero.ilike(f"%{search}%"),
                    Contrato.contratante_nome.ilike(f"%{search}%")
                )
            )
        
        # Count total
        count_result = await self.db.execute(
            select(func.count(Contrato.id)).select_from(query.subquery())
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
        
        if data.status:
            contrato.status = data.status
        if data.pdf_url:
            contrato.pdf_url = data.pdf_url
        if data.dados_extras:
            contrato.dados_extras = data.dados_extras
        
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
        
        await self.db.delete(contrato)
        await self.db.commit()
        
        return True
    
    async def generate_pdf(self, contrato_id: UUID) -> Optional[str]:
        """Generate PDF for contract."""
        contrato = await self.get_by_id(contrato_id)
        if not contrato:
            return None
        
        # Prepare data for PDF
        dados = {
            "numero": contrato.numero,
            "contratante_nome": contrato.contratante_nome,
            "contratante_documento": contrato.contratante_documento,
            "contratante_email": contrato.contratante_email,
            "contratante_telefone": contrato.contratante_telefone,
            "contratante_endereco": contrato.contratante_endereco,
            "valor_total": f"{contrato.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "valor_total_extenso": contrato.valor_total_extenso,
            "valor_entrada": f"{contrato.valor_entrada:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "valor_entrada_extenso": contrato.valor_entrada_extenso,
            "qtd_parcelas": contrato.qtd_parcelas,
            "qtd_parcelas_extenso": contrato.qtd_parcelas_extenso,
            "valor_parcela": f"{contrato.valor_parcela:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "valor_parcela_extenso": contrato.valor_parcela_extenso,
            "prazo_1": contrato.prazo_1,
            "prazo_1_extenso": contrato.prazo_1_extenso,
            "prazo_2": contrato.prazo_2,
            "prazo_2_extenso": contrato.prazo_2_extenso,
            "local_assinatura": contrato.local_assinatura,
            "data_assinatura": contrato.data_assinatura,
        }
        
        # Generate PDF
        pdf_path = self.pdf.generate_contrato_bacen(contrato.id, dados)
        
        # Update contract with PDF URL
        relative_path = f"/storage/{os.path.basename(pdf_path)}"
        await self.update(contrato_id, ContratoUpdate(pdf_url=relative_path))
        
        return relative_path

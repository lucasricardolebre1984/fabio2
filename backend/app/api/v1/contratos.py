"""Contratos routes."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_operador
from app.models.user import User
from app.models.contrato import Contrato, ContratoStatus
from app.models.cliente import Cliente
from app.schemas.contrato import (
    ContratoCreate,
    ContratoUpdate,
    ContratoResponse,
    ContratoListResponse,
    ContratoTemplateResponse
)
from app.services.contrato_service import ContratoService

router = APIRouter()


@router.get("/templates", response_model=List[ContratoTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """List available contract templates."""
    service = ContratoService(db)
    return await service.list_templates()


@router.get("/templates/{template_id}", response_model=ContratoTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Get contract template by ID."""
    service = ContratoService(db)
    template = await service.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    return template


@router.post("", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
async def create_contrato(
    data: ContratoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Create a new contract and auto-create client if needed."""
    service = ContratoService(db)
    return await service.create(data, current_user.id)


@router.get("", response_model=ContratoListResponse)
async def list_contratos(
    status: Optional[ContratoStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by cliente name or numero"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """List contracts with pagination."""
    service = ContratoService(db)
    return await service.list(
        status=status,
        search=search,
        page=page,
        page_size=page_size
    )


@router.get("/{contrato_id}", response_model=ContratoResponse)
async def get_contrato(
    contrato_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Get contract by ID."""
    service = ContratoService(db)
    contrato = await service.get_by_id(contrato_id)
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    return contrato


@router.put("/{contrato_id}", response_model=ContratoResponse)
async def update_contrato(
    contrato_id: UUID,
    data: ContratoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Update contract."""
    service = ContratoService(db)
    contrato = await service.update(contrato_id, data)
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    return contrato


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contrato(
    contrato_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete contract (admin only)."""
    service = ContratoService(db)
    deleted = await service.delete(contrato_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )


@router.post("/{contrato_id}/pdf")
async def generate_pdf(
    contrato_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Generate PDF for contract."""
    service = ContratoService(db)
    pdf_url = await service.generate_pdf(contrato_id)
    
    if not pdf_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar PDF"
        )
    
    return {"pdf_url": pdf_url}


@router.post("/{contrato_id}/enviar")
async def send_whatsapp(
    contrato_id: UUID,
    telefone: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Send contract via WhatsApp."""
    from app.services.whatsapp_service import WhatsAppService
    
    # Get contrato
    service = ContratoService(db)
    contrato = await service.get_by_id(contrato_id)
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Send via WhatsApp
    wa_service = WhatsAppService()
    result = await wa_service.send_document(
        numero=telefone,
        documento_url=contrato.pdf_url,
        legenda=f"Contrato {contrato.numero} - FC Soluções Financeiras"
    )
    
    # Update status
    await service.update(contrato_id, ContratoUpdate(status=ContratoStatus.ENVIADO))
    
    return {"message": "Contrato enviado com sucesso", "result": result}

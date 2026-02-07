"""Clientes routes."""
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin, require_operador
from app.models.user import User
from app.schemas.cliente import (
    ClienteCreate,
    ClienteListResponse,
    ClienteResponse,
    ClienteUpdate,
)
from app.services.cliente_service import ClienteService

router = APIRouter()


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    data: ClienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Create a new client."""
    service = ClienteService(db)

    existing = await service.get_by_documento(data.documento)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cliente com este documento ja existe",
        )

    return await service.create(data)


@router.get("", response_model=ClienteListResponse)
async def list_clientes(
    search: Optional[str] = Query(None, description="Search by name or documento"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """List clients with pagination."""
    service = ClienteService(db)
    return await service.list(search=search, page=page, page_size=page_size)


@router.post("/sincronizar-contratos", response_model=Dict[str, int])
async def sincronizar_clientes_por_contratos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Backfill clients for contracts that were created without client linkage."""
    service = ClienteService(db)
    return await service.sync_from_contracts()


@router.get("/documento/{documento}", response_model=ClienteResponse)
async def get_cliente_by_documento(
    documento: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Get client by documento (CPF/CNPJ)."""
    service = ClienteService(db)
    cliente = await service.get_by_documento(documento)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    return cliente


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Get client by ID."""
    service = ClienteService(db)
    cliente = await service.get_by_id(cliente_id)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: UUID,
    data: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Update client."""
    service = ClienteService(db)
    cliente = await service.update(cliente_id, data)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )

    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    cliente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete client (admin only)."""
    service = ClienteService(db)
    deleted = await service.delete(cliente_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado",
        )


@router.get("/{cliente_id}/contratos")
async def get_cliente_contratos(
    cliente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Get client contract history."""
    service = ClienteService(db)
    return await service.get_contratos(cliente_id)


@router.get("/{cliente_id}/historico")
async def get_cliente_historico(
    cliente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Get complete client timeline (contratos + agenda)."""
    service = ClienteService(db)
    return await service.get_historico(cliente_id)

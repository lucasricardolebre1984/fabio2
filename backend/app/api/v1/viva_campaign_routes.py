from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.api.v1.viva_schemas import (
    CampanhaDeleteResponse,
    CampanhaItem,
    CampanhaListResponse,
    CampanhaResetResponse,
    CampanhaResetAllResponse,
    CampanhaSaveRequest,
)
from app.models.user import User
from app.services.cofre_memory_service import cofre_memory_service
from app.services.viva_campaign_repository_service import viva_campaign_repository_service
from app.services.viva_shared_service import (
    _clear_campaign_history,
    _campaign_row_to_item,
    _derive_campaign_title,
    _normalize_mode,
    _save_campaign_record,
)

router = APIRouter()


@router.post("/campanhas", response_model=CampanhaItem)
async def save_campanha(
    payload: CampanhaSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    modo = _normalize_mode(payload.modo)
    if modo not in ("FC", "REZETA", "NEUTRO"):
        raise HTTPException(status_code=400, detail="Modo de campanha invalido.")

    try:
        title = payload.titulo or _derive_campaign_title(
            modo,
            payload.overlay or {},
            payload.mensagem_original or payload.briefing or "",
        )
        campaign_id = await _save_campaign_record(
            db=db,
            user_id=current_user.id,
            modo=modo,
            image_url=payload.image_url,
            titulo=title,
            briefing=payload.briefing,
            mensagem_original=payload.mensagem_original,
            overlay=payload.overlay or {},
            meta=payload.meta or {},
        )
        if not campaign_id:
            raise HTTPException(status_code=400, detail="URL da imagem obrigatoria.")

        row = await viva_campaign_repository_service.get_campaign_row(db=db, campaign_id=campaign_id)
        if not row:
            raise HTTPException(status_code=500, detail="Falha ao salvar campanha.")
        return _campaign_row_to_item(row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar campanha: {str(exc)}")


@router.get("/campanhas", response_model=CampanhaListResponse)
async def list_campanhas(
    modo: Optional[str] = None,
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    normalized_mode = _normalize_mode(modo) if modo else None

    try:
        rows, total = await viva_campaign_repository_service.list_campaign_rows(
            db=db,
            user_id=current_user.id,
            modo=normalized_mode,
            limit=limit,
            offset=offset,
        )
        items = [_campaign_row_to_item(row) for row in rows]
        return CampanhaListResponse(items=items, total=total)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao listar campanhas: {str(exc)}")


@router.post("/campanhas/reset-patterns", response_model=CampanhaResetResponse)
async def reset_campanha_patterns(
    modo: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    normalized_mode = _normalize_mode(modo) if modo else None
    if normalized_mode and normalized_mode not in ("FC", "REZETA", "NEUTRO"):
        raise HTTPException(status_code=400, detail="Modo invalido para reset de campanhas.")
    try:
        deleted = await _clear_campaign_history(
            db=db,
            user_id=current_user.id,
            modo=normalized_mode,
        )
        return CampanhaResetResponse(
            deleted=int(deleted),
            modo=normalized_mode,
            message="Memoria de padrao de campanhas limpa com sucesso.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar padrao de campanhas: {str(exc)}")


@router.post("/campanhas/reset-all", response_model=CampanhaResetAllResponse)
async def reset_all_campanhas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted_db = await viva_campaign_repository_service.clear_campaign_history(
            db=db,
            user_id=current_user.id,
            modo=None,
        )
        cofre_cleared = {"viva_campanhas": cofre_memory_service.clear_table("viva_campanhas")}
        cofre_snapshots_removed = cofre_memory_service.clear_campaign_snapshots()
        cofre_assets_removed = cofre_memory_service.clear_campaign_assets()
        return CampanhaResetAllResponse(
            deleted_db=int(deleted_db),
            cofre_cleared_files={
                **cofre_cleared,
                "viva_campanhas_items": int(cofre_snapshots_removed),
            },
            cofre_assets_removed=int(cofre_assets_removed),
            message="Campanhas de teste limpas no banco e no COFRE.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao resetar campanhas: {str(exc)}")


@router.get("/campanhas/{campanha_id}", response_model=CampanhaItem)
async def get_campanha(
    campanha_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        row = await viva_campaign_repository_service.get_campaign_row_by_id(
            db=db,
            campaign_id=campanha_id,
            user_id=current_user.id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="Campanha nao encontrada.")
        return _campaign_row_to_item(row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar campanha: {str(exc)}")


@router.delete("/campanhas/{campanha_id}", response_model=CampanhaDeleteResponse)
async def delete_campanha(
    campanha_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        deleted = await viva_campaign_repository_service.delete_campaign_by_id(
            db=db,
            campaign_id=campanha_id,
            user_id=current_user.id,
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Campanha nao encontrada.")
        return CampanhaDeleteResponse(
            deleted=True,
            id=campanha_id,
            message="Campanha removida com sucesso.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao remover campanha: {str(exc)}")

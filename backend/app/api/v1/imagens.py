"""Imagem routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_operador
from app.models.user import User
from app.models.imagem import StatusImagem, TipoImagem, FormatoImagem
from app.services.imagem_service import ImagemService
from app.schemas.imagem import (
    ImagemResponse, ImagemListResponse, ImagemUpdate,
    GerarImagemRequest, GerarImagemResponse,
    UploadImagemResponse, AprovarImagemResponse
)

router = APIRouter()


@router.get("", response_model=ImagemListResponse)
async def listar_imagens(
    status: Optional[StatusImagem] = None,
    tipo: Optional[TipoImagem] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """
    List images with optional filters.
    
    Args:
        status: Filter by status (rascunho/aprovada)
        tipo: Filter by type (gerada/upload)
        skip: Pagination offset
        limit: Pagination limit (max 100)
    """
    service = ImagemService()
    imagens = await service.listar_imagens(db, status, tipo, skip, limit)
    
    return ImagemListResponse(
        items=[ImagemResponse.model_validate(img) for img in imagens],
        total=len(imagens)
    )


@router.post("/gerar", response_model=GerarImagemResponse)
async def gerar_imagem(
    request: GerarImagemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """
    Generate image using GLM-Image API (Z.AI) with cost tracking.
    
    - Custo: US$ 0.015 por imagem (~R$ 0,075)
    - Modelo: glm-image
    - Tracking: Cada geração é registrada com custo
    """
    service = ImagemService()
    
    try:
        # Generate image using GLM-Image with cost tracking
        image_bytes, custo = await service.gerar_imagem_ia(
            db=db,
            prompt=request.prompt,
            formato=request.formato
        )
        
        # Save to storage and database
        nome = request.nome or f"Imagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        imagem = await service.salvar_imagem_gerada(
            db=db,
            image_bytes=image_bytes,
            nome=nome,
            prompt=request.prompt,
            formato=request.formato,
            custo=custo  # Link cost record to image
        )
        
        return GerarImagemResponse(
            success=True,
            imagem=ImagemResponse.model_validate(imagem),
            message=f"Imagem gerada com sucesso (Custo: {custo.custo_brl_formatado})",
            custo={
                "usd": float(custo.custo_usd),
                "brl": float(custo.custo_brl),
                "tempo_ms": custo.tempo_geracao_ms
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar imagem: {str(e)}"
        )


@router.post("/upload", response_model=UploadImagemResponse)
async def upload_imagem(
    file: UploadFile = File(...),
    nome: str = Form(...),
    formato: str = Form("1:1"),
    descricao: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """
    Upload image file.
    
    Supported formats: jpg, jpeg, png, webp
    Max size: 10MB
    """
    # Validate file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
        )
    
    # Validate and convert formato
    try:
        formato_enum = FormatoImagem(formato)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato inválido. Use: 1:1, 16:9 ou 9:16"
        )
    
    service = ImagemService()
    
    try:
        imagem = await service.salvar_upload(
            db=db,
            file=file,
            nome=nome,
            formato=formato_enum,
            descricao=descricao
        )
        
        return UploadImagemResponse(
            success=True,
            imagem=ImagemResponse.model_validate(imagem),
            message="Imagem enviada com sucesso"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar imagem: {str(e)}"
        )


@router.post("/{imagem_id}/aprovar", response_model=AprovarImagemResponse)
async def aprovar_imagem(
    imagem_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """
    Approve image and move to campanhas folder.
    
    File will be renamed to: YYYYMMDD_nome.ext
    """
    service = ImagemService()
    
    try:
        imagem = await service.aprovar_para_campanha(db, imagem_id)
        
        return AprovarImagemResponse(
            success=True,
            nova_url=imagem.url,
            message="Imagem aprovada e movida para campanhas"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{imagem_id}", response_model=ImagemResponse)
async def get_imagem(
    imagem_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Get single image by ID."""
    service = ImagemService()
    imagem = await service.get_imagem(db, imagem_id)
    
    if not imagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada"
        )
    
    return ImagemResponse.model_validate(imagem)


@router.patch("/{imagem_id}", response_model=ImagemResponse)
async def update_imagem(
    imagem_id: UUID,
    update_data: ImagemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Update image metadata."""
    from sqlalchemy import update
    from app.models.imagem import Imagem
    
    # Build update dict
    update_dict = {}
    if update_data.nome is not None:
        update_dict["nome"] = update_data.nome
    if update_data.descricao is not None:
        update_dict["descricao"] = update_data.descricao
    if update_data.status is not None:
        update_dict["status"] = update_data.status
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar"
        )
    
    # Execute update
    await db.execute(
        update(Imagem)
        .where(Imagem.id == imagem_id)
        .values(**update_dict)
    )
    await db.commit()
    
    # Return updated image
    service = ImagemService()
    imagem = await service.get_imagem(db, imagem_id)
    
    if not imagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada"
        )
    
    return ImagemResponse.model_validate(imagem)


@router.delete("/{imagem_id}")
async def deletar_imagem(
    imagem_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Delete image."""
    service = ImagemService()
    
    success = await service.deletar_imagem(db, imagem_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem não encontrada"
        )
    
    return {"success": True, "message": "Imagem deletada com sucesso"}


# Import for gerar_imagem endpoint
from datetime import datetime
from pathlib import Path

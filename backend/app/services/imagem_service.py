"""Imagem service with HuggingFace integration."""
import os
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import httpx
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.imagem import Imagem, TipoImagem, FormatoImagem, StatusImagem
from app.schemas.imagem import ImagemCreate


class ImagemService:
    """Service for image generation and management."""
    
    # Pollinations.ai - API gratuita sem autenticação
    POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
    
    # Tamanhos por formato
    FORMATO_DIMENSOES = {
        FormatoImagem.QUADRADO: (1024, 1024),    # 1:1
        FormatoImagem.PAISAGEM: (1024, 576),     # 16:9
        FormatoImagem.RETRATO: (576, 1024),      # 9:16
    }
    
    def __init__(self):
        """Initialize service."""
        self.storage_path = Path("storage/imagens")
        self.campanhas_path = Path("storage/campanhas")
        
        # Garantir que pastas existam
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.campanhas_path.mkdir(parents=True, exist_ok=True)
    
    async def gerar_imagem_ia(
        self,
        db: AsyncSession,
        prompt: str,
        formato: FormatoImagem = FormatoImagem.QUADRADO
    ) -> tuple[bytes, "ImagemCusto"]:
        """
        Generate image using GLM-Image API (Z.AI) with cost tracking.
        
        Args:
            db: Database session for cost tracking
            prompt: Text prompt for image generation
            formato: Aspect ratio format
            
        Returns:
            Tuple of (image bytes, ImagemCusto record)
            
        Raises:
            Exception: If API call fails
        """
        from app.services.glm_image_service import glm_image_service
        from app.models.imagem_custo import ImagemCusto
        
        # Usa GLM-Image API
        image_bytes, custo_info = await glm_image_service.gerar_imagem(
            prompt=prompt,
            formato=formato
        )
        
        # Criar registro de custo no banco
        custo_record = ImagemCusto(
            modelo=custo_info["modelo"],
            provider=custo_info["provider"],
            custo_usd=custo_info["custo_usd"],
            custo_brl=custo_info["custo_brl"],
            taxa_cambio=custo_info["taxa_cambio"],
            dimensoes=custo_info["dimensoes"],
            formato=custo_info["formato"],
            tempo_geracao_ms=custo_info["tempo_geracao_ms"],
            status=custo_info["status"],
            prompt_original=custo_info["prompt_original"],
            prompt_enhanced=custo_info["prompt_enhanced"]
        )
        db.add(custo_record)
        await db.commit()
        await db.refresh(custo_record)
        
        return image_bytes, custo_record
    
    def _enhance_prompt(self, prompt: str, formato: FormatoImagem = FormatoImagem.QUADRADO) -> str:
        """
        Enhance prompt with CÉREBRO INSTITUCIONAL (BRAINIMAGE.md).
        
        Args:
            prompt: Original user prompt
            formato: Image format for context-specific enhancements
            
        Returns:
            Enhanced technical prompt following BRAINIMAGE guidelines
        """
        from app.services.brainimage_service import brain_service
        
        enhanced_prompt, _ = brain_service.generate_technical_prompt(
            user_prompt=prompt,
            formato=formato.value,
            style_preset='professional'
        )
        
        return enhanced_prompt
    
    async def salvar_imagem_gerada(
        self,
        db: AsyncSession,
        image_bytes: bytes,
        nome: str,
        prompt: str,
        formato: FormatoImagem,
        descricao: Optional[str] = None,
        custo: Optional["ImagemCusto"] = None
    ) -> Imagem:
        """
        Save generated image to storage and database.
        
        Args:
            db: Database session
            image_bytes: Image data
            nome: Image name
            prompt: Generation prompt
            formato: Image format
            descricao: Optional description
            custo: Optional ImagemCusto record to link
            
        Returns:
            Created Imagem model
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.png"
        file_path = self.storage_path / filename
        
        # Save to disk
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        # Create database record
        imagem = Imagem(
            nome=nome,
            descricao=descricao,
            url=str(file_path.relative_to(Path("storage"))),
            tipo=TipoImagem.GERADA,
            formato=formato,
            prompt=prompt,
            status=StatusImagem.RASCUNHO
        )
        
        db.add(imagem)
        await db.commit()
        await db.refresh(imagem)
        
        # Link cost record to image if provided
        if custo:
            custo.imagem_id = str(imagem.id)
            await db.commit()
        
        return imagem
    
    async def salvar_upload(
        self,
        db: AsyncSession,
        file: UploadFile,
        nome: str,
        formato: FormatoImagem = FormatoImagem.QUADRADO,
        descricao: Optional[str] = None
    ) -> Imagem:
        """
        Save uploaded image to storage and database.
        
        Args:
            db: Database session
            file: Uploaded file
            nome: Image name
            formato: Image format
            descricao: Optional description
            
        Returns:
            Created Imagem model
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = Path(file.filename).suffix or ".jpg"
        filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{extension}"
        file_path = self.storage_path / filename
        
        # Save to disk
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create database record
        imagem = Imagem(
            nome=nome,
            descricao=descricao,
            url=str(file_path.relative_to(Path("storage"))),
            tipo=TipoImagem.UPLOAD,
            formato=formato,
            status=StatusImagem.RASCUNHO
        )
        
        db.add(imagem)
        await db.commit()
        await db.refresh(imagem)
        
        return imagem
    
    async def aprovar_para_campanha(
        self,
        db: AsyncSession,
        imagem_id: uuid.UUID
    ) -> Imagem:
        """
        Move image to campanhas folder with date prefix.
        
        Args:
            db: Database session
            imagem_id: Image ID to approve
            
        Returns:
            Updated Imagem model
        """
        # Get image from database
        result = await db.execute(select(Imagem).where(Imagem.id == imagem_id))
        imagem = result.scalar_one_or_none()
        
        if not imagem:
            raise Exception("Imagem não encontrada")
        
        if imagem.status == StatusImagem.APROVADA:
            raise Exception("Imagem já está aprovada")
        
        # Current path
        old_path = Path("storage") / imagem.url
        
        # New path with date prefix
        date_prefix = datetime.now().strftime("%Y%m%d")
        extension = old_path.suffix
        new_filename = f"{date_prefix}_{imagem.nome}{extension}"
        new_path = self.campanhas_path / new_filename
        
        # Move file
        import shutil
        shutil.move(str(old_path), str(new_path))
        
        # Update database
        imagem.url = str(new_path.relative_to(Path("storage")))
        imagem.status = StatusImagem.APROVADA
        
        await db.commit()
        await db.refresh(imagem)
        
        return imagem
    
    async def listar_imagens(
        self,
        db: AsyncSession,
        status: Optional[StatusImagem] = None,
        tipo: Optional[TipoImagem] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Imagem]:
        """
        List images with optional filters.
        
        Args:
            db: Database session
            status: Filter by status
            tipo: Filter by type
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of Imagem models
        """
        query = select(Imagem).order_by(desc(Imagem.created_at))
        
        if status:
            query = query.where(Imagem.status == status)
        if tipo:
            query = query.where(Imagem.tipo == tipo)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def deletar_imagem(
        self,
        db: AsyncSession,
        imagem_id: uuid.UUID
    ) -> bool:
        """
        Delete image from storage and database.
        
        Args:
            db: Database session
            imagem_id: Image ID to delete
            
        Returns:
            True if deleted successfully
        """
        result = await db.execute(select(Imagem).where(Imagem.id == imagem_id))
        imagem = result.scalar_one_or_none()
        
        if not imagem:
            return False
        
        # Delete file
        file_path = Path("storage") / imagem.url
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        await db.delete(imagem)
        await db.commit()
        
        return True
    
    async def get_imagem(
        self,
        db: AsyncSession,
        imagem_id: uuid.UUID
    ) -> Optional[Imagem]:
        """
        Get single image by ID.
        
        Args:
            db: Database session
            imagem_id: Image ID
            
        Returns:
            Imagem model or None
        """
        result = await db.execute(select(Imagem).where(Imagem.id == imagem_id))
        return result.scalar_one_or_none()

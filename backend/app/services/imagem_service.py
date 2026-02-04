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
    
    async def gerar_imagem_hf(
        self,
        prompt: str,
        formato: FormatoImagem = FormatoImagem.QUADRADO
    ) -> bytes:
        """
        Generate image using AI API.
        
        Args:
            prompt: Text prompt for image generation
            formato: Aspect ratio format
            
        Returns:
            Image bytes
            
        Raises:
            Exception: If API call fails
        """
        width, height = self.FORMATO_DIMENSOES[formato]
        
        # Enhanced prompt with BRAINIMAGE style guidelines
        enhanced_prompt = self._enhance_prompt(prompt)
        
        # Tenta Pollinations.ai primeiro
        from urllib.parse import quote
        encoded_prompt = quote(enhanced_prompt)
        url = f"{self.POLLINATIONS_URL}/{encoded_prompt}?width={width}&height={height}&nologo=true"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.content
            except:
                pass
            
            # Fallback: usa placeholder.com para testes
            # Gera uma cor baseada no hash do prompt
            import hashlib
            color = hashlib.md5(prompt.encode()).hexdigest()[:6]
            placeholder_url = f"https://placehold.co/{width}x{height}/{color}/white/png?text={quote(prompt[:30])}"
            
            response = await client.get(placeholder_url)
            if response.status_code == 200:
                return response.content
            
            raise Exception(f"Não foi possível gerar imagem. Tente novamente mais tarde.")
    
    def _enhance_prompt(self, prompt: str) -> str:
        """
        Enhance prompt with BRAINIMAGE institutional guidelines.
        
        Args:
            prompt: Original user prompt
            
        Returns:
            Enhanced prompt for better results
        """
        # Add professional marketing context
        prefix = "professional marketing image, commercial photography, "
        suffix = ", high quality, sharp focus, corporate aesthetic, brand-safe"
        
        return f"{prefix}{prompt}{suffix}"
    
    async def salvar_imagem_gerada(
        self,
        db: AsyncSession,
        image_bytes: bytes,
        nome: str,
        prompt: str,
        formato: FormatoImagem,
        descricao: Optional[str] = None
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

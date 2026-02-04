"""
Serviço de integração com GLM-Image API (Z.AI)
Geração de imagens com tracking de custos

Documentação: https://docs.z.ai/guides/image/glm-image
Preço: US$ 0.015 por imagem
"""

import httpx
import time
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.imagem import FormatoImagem
from app.services.brainimage_service import brain_service
from app.models.imagem_custo import ImagemCusto
from app.config import settings


class GLMImageService:
    """
    Serviço para geração de imagens usando GLM-Image (Z.AI)
    Com tracking automático de custos
    """
    
    # Configurações da API
    BASE_URL = "https://api.z.ai/api/paas/v4"
    ENDPOINT = "/images/generations"
    
    # Custos (USD)
    CUSTO_POR_IMAGEM_USD = Decimal("0.015")
    
    # Dimensões por formato
    FORMATO_DIMENSOES = {
        FormatoImagem.QUADRADO: "1024x1024",    # 1:1
        FormatoImagem.PAISAGEM: "1024x576",     # 16:9
        FormatoImagem.RETRATO: "576x1024",      # 9:16
    }
    
    def __init__(self):
        self.api_key = settings.ZAI_API_KEY
        self.model = settings.ZAI_MODEL
        self.taxa_cambio = Decimal(str(settings.TAXA_CAMBIO_BRL))
        
        if not self.api_key:
            raise ValueError("ZAI_API_KEY não configurada no .env")
    
    def _get_headers(self) -> dict:
        """Retorna headers para requisição à API Z.AI"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _calcular_dimensoes(self, formato: FormatoImagem) -> str:
        """Retorna dimensões no formato aceito pela API"""
        return self.FORMATO_DIMENSOES.get(formato, "1024x1024")
    
    def _calcular_custo_brl(self, custo_usd: Decimal) -> Decimal:
        """Converte custo USD para BRL"""
        return custo_usd * self.taxa_cambio
    
    async def gerar_imagem(
        self,
        prompt: str,
        formato: FormatoImagem = FormatoImagem.QUADRADO
    ) -> Tuple[bytes, dict]:
        """
        Gera imagem usando GLM-Image API
        
        Args:
            prompt: Prompt do usuário
            formato: Formato da imagem (1:1, 16:9, 9:16)
        
        Returns:
            Tuple de (bytes da imagem, info de custo)
        """
        
        # 1. Enhancer o prompt usando BRAINIMAGE
        enhanced_prompt = brain_service.generate_technical_prompt(prompt, formato.value)[0]
        
        # 2. Preparar payload da API
        size = self._calcular_dimensoes(formato)
        
        payload = {
            "model": self.model,
            "prompt": enhanced_prompt,
            "size": size
        }
        
        # 4. Fazer requisição à API
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}{self.ENDPOINT}",
                    headers=self._get_headers(),
                    json=payload
                )
                
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code != 200:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    
                    if custo_record:
                        custo_record.status = "erro"
                        custo_record.erro_mensagem = error_msg[:500]
                        custo_record.tempo_geracao_ms = elapsed_ms
                        db.commit()
                    
                    raise Exception(error_msg)
                
                # 5. Processar resposta
                data = response.json()
                
                # A resposta pode vir em diferentes formatos dependendo da API
                # Tentar extrair URL da imagem
                image_url = None
                if isinstance(data, dict):
                    if "data" in data and len(data["data"]) > 0:
                        image_url = data["data"][0].get("url")
                    elif "url" in data:
                        image_url = data["url"]
                
                if not image_url:
                    raise Exception(f"URL da imagem não encontrada na resposta: {data}")
                
                # 6. Baixar a imagem
                image_response = await client.get(image_url, timeout=60.0)
                
                if image_response.status_code != 200:
                    raise Exception(f"Erro ao baixar imagem: {image_response.status_code}")
                
                image_bytes = image_response.content
                
                # Retornar imagem + info de custo
                custo_info = {
                    "modelo": self.model,
                    "provider": "zai",
                    "custo_usd": self.CUSTO_POR_IMAGEM_USD,
                    "custo_brl": self._calcular_custo_brl(self.CUSTO_POR_IMAGEM_USD),
                    "taxa_cambio": self.taxa_cambio,
                    "dimensoes": self._calcular_dimensoes(formato),
                    "formato": formato.value,
                    "tempo_geracao_ms": elapsed_ms,
                    "status": "sucesso",
                    "prompt_original": prompt[:500],
                    "prompt_enhanced": enhanced_prompt[:1000]
                }
                
                return image_bytes, custo_info
                
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            raise
    
    async def verificar_saldo(self) -> dict:
        """
        Verifica saldo/créditos disponíveis na conta Z.AI
        
        Returns:
            Dict com informações de saldo
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/user/balance",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"Status {response.status_code}",
                        "message": response.text
                    }
        except Exception as e:
            return {"error": str(e)}


# Instância singleton
glm_image_service = GLMImageService()

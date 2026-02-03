"""
Stub de serviço PDF - Redireciona para geração frontend
"""
from typing import Dict, Any, Optional
from uuid import UUID


class PDFService:
    """Serviço stub para PDF - PDF é gerado no frontend"""
    
    async def generate_contrato_pdf(self, contrato_id: UUID, dados: Dict[str, Any]) -> Optional[bytes]:
        """
        Retorna HTML em vez de PDF - o frontend converte para PDF
        """
        # Retorna None para indicar que o PDF deve ser gerado no frontend
        return None

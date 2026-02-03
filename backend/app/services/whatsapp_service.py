"""WhatsApp service - Integration with Evolution API."""
from typing import Optional, Dict, Any
import httpx

from app.config import settings


class WhatsAppService:
    """Service for WhatsApp integration via Evolution API."""
    
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL.rstrip("/")
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.WA_INSTANCE_NAME
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get WhatsApp connection status."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/instance/connectionState/{self.instance_name}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "conectado": data.get("state") == "open",
                        "estado": data.get("state"),
                        "numero": data.get("user", {}).get("id", {}).get("user"),
                        "nome_perfil": data.get("user", {}).get("name"),
                    }
                else:
                    return {
                        "conectado": False,
                        "erro": f"Status {response.status_code}"
                    }
            except Exception as e:
                return {
                    "conectado": False,
                    "erro": str(e)
                }
    
    async def connect(self) -> Dict[str, Any]:
        """Start WhatsApp connection (returns QR code)."""
        async with httpx.AsyncClient() as client:
            try:
                # Create instance if not exists
                create_response = await client.post(
                    f"{self.base_url}/instance/create",
                    headers=self.headers,
                    json={
                        "instanceName": self.instance_name,
                        "token": self.api_key,
                        "qrcode": True
                    },
                    timeout=30.0
                )
                
                if create_response.status_code in [200, 201]:
                    data = create_response.json()
                    return {
                        "sucesso": True,
                        "qr_code": data.get("qrcode"),
                        "mensagem": "Escaneie o QR Code com seu WhatsApp"
                    }
                else:
                    return {
                        "sucesso": False,
                        "erro": f"Erro ao criar instância: {create_response.status_code}"
                    }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e)
                }
    
    async def disconnect(self) -> Dict[str, Any]:
        """Disconnect WhatsApp."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/instance/logout/{self.instance_name}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "sucesso": True,
                        "mensagem": "Desconectado com sucesso"
                    }
                else:
                    return {
                        "sucesso": False,
                        "erro": f"Status {response.status_code}"
                    }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e)
                }
    
    async def send_text(self, numero: str, mensagem: str) -> Dict[str, Any]:
        """Send text message."""
        # Format number (add country code if needed)
        numero = self._format_number(numero)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{self.instance_name}",
                    headers=self.headers,
                    json={
                        "number": numero,
                        "text": mensagem,
                        "delay": 1200
                    },
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    return {
                        "sucesso": True,
                        "mensagem": "Mensagem enviada com sucesso"
                    }
                else:
                    return {
                        "sucesso": False,
                        "erro": f"Status {response.status_code}: {response.text}"
                    }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e)
                }
    
    async def send_document(
        self,
        numero: str,
        documento_url: str,
        legenda: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send document/file."""
        numero = self._format_number(numero)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/message/sendMedia/{self.instance_name}",
                    headers=self.headers,
                    json={
                        "number": numero,
                        "media": documento_url,
                        "caption": legenda or "",
                        "mediatype": "document",
                        "fileName": documento_url.split("/")[-1],
                        "delay": 1200
                    },
                    timeout=60.0
                )
                
                if response.status_code == 201:
                    return {
                        "sucesso": True,
                        "mensagem": "Documento enviado com sucesso"
                    }
                else:
                    return {
                        "sucesso": False,
                        "erro": f"Status {response.status_code}: {response.text}"
                    }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e)
                }
    
    def _format_number(self, numero: str) -> str:
        """Format phone number for WhatsApp API."""
        # Remove non-digits
        numero = "".join(filter(str.isdigit, numero))
        
        # Add Brazil country code if not present
        if not numero.startswith("55"):
            numero = "55" + numero
        
        return numero

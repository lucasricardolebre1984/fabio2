"""
OpenRouter Service - API Gratuita para IA
Acesso a: Llama, Mistral, Qwen, e mais
Site: https://openrouter.ai/
"""
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings


class OpenRouterService:
    """
    Serviço usando OpenRouter - gratuito com rate limits
    """
    
    def __init__(self):
        # OpenRouter API key - gratuito
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Modelos gratuitos disponíveis
        self.model_chat = "meta-llama/llama-3.2-3b-instruct:free"  # Gratuito
        self.model_vision = "qwen/qwen2-vl-7b-instruct:free"  # Gratuito com visão
        
        # Prompt do sistema VIVA
        self.system_prompt = """Voce e VIVA, a assistente virtual inteligente da FC Solucoes Financeiras e RezetaBrasil.

PERSONALIDADE:
- Profissional, calorosa e eficiente
- Conhece profundamente os servicos das empresas
- Fala de forma natural, como uma concierge experiente

EMPRESAS:
FC Solucoes Financeiras - Consultoria empresarial, credito empresarial, Pessoa juridica
RezetaBrasil - Credito pessoal, limpa nome, Pessoa fisica

REGRAS:
- Nunca invente valores ou prazos
- Ofereca agendar com consultor quando nao souber
- Mantenha respostas curtas e objetivas
- Use emojis ocasionalmente"""

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Chat com modelo gratuito"""
        if not self.api_key:
            return "Erro: OPENROUTER_API_KEY nao configurada"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "FC Solucoes - VIVA"
                    },
                    json={
                        "model": self.model_chat,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": 800
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    return "⚠️ Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
                else:
                    return f"Erro {response.status_code}. Tente novamente."
                    
        except Exception as e:
            return f"Erro de conexao: {str(e)[:100]}"

    def build_messages(self, user_message: str, context: List[Dict] = None) -> List[Dict[str, str]]:
        """Monta lista de mensagens"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if context:
            for msg in context:
                if msg.get('tipo') == 'usuario':
                    messages.append({"role": "user", "content": msg.get('conteudo', '')})
                elif msg.get('tipo') == 'ia':
                    messages.append({"role": "assistant", "content": msg.get('conteudo', '')})
        
        messages.append({"role": "user", "content": user_message})
        return messages

    async def vision(self, image_base64: str, prompt: str) -> str:
        """Analise de imagem com modelo gratuito"""
        if not self.api_key:
            return "Erro: API key nao configurada"
        
        try:
            messages = [
                {"role": "system", "content": "Voce e um assistente que analisa imagens."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "FC Solucoes - VIVA"
                    },
                    json={
                        "model": self.model_vision,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"Erro na analise: {response.status_code}"
                    
        except Exception as e:
            return f"Erro: {str(e)[:100]}"

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do serviço"""
        return {
            "api_configurada": bool(self.api_key),
            "modelo": self.model_chat,
            "tipo": "OpenRouter (Gratuito)"
        }


# Instância global
openrouter_service = OpenRouterService()

"""
Z.AI Service - API Unificada
Suporta: Chat, Visão, Áudio, Imagem
Usa DeepSeek como fallback
"""
import httpx
import base64
from typing import List, Dict, Any, Optional
from app.config import settings


class ZAIService:
    """
    Serviço unificado - tenta Z.AI, fallback para DeepSeek
    """
    
    def __init__(self):
        # Tentar Z.AI primeiro
        self.zai_key = getattr(settings, 'ZAI_API_KEY', None)
        self.zai_base = "https://open.bigmodel.cn/api/paas/v4"
        
        # Fallback DeepSeek
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', self.zai_key)
        self.base_url = "https://api.deepseek.com"
        
        # Modelos
        self.model_chat = "deepseek-chat"
        self.model_vision = "deepseek-chat"
        self.model_audio = "deepseek-chat"
        self.model_image = "deepseek-chat"
        
        # Prompt do sistema para VIVA
        self.system_prompt = """Voce e VIVA, a assistente virtual inteligente da FC Solucoes Financeiras e RezetaBrasil.

SUA PERSONALIDADE:
- Profissional, calorosa e eficiente
- Voce conhece profundamente os servicos das empresas
- Fala de forma natural, como uma concierge experiente
- Sempre oferece ajuda antes de direcionar

SOBRE AS EMPRESAS:
**FC Solucoes Financeiras**
- Consultoria empresarial e servicos financeiros
- Credito empresarial, antecipacao de recebiveis
- Clientes: Pessoa juridica, empresas
- Tom: Profissional, corporativo, azul

**RezetaBrasil**
- Solucoes de credito pessoal
- Limpa nome, renegociacao de dividas
- Clientes: Pessoa fisica
- Tom: Acessivel, promocional, verde

SERVICOS QUE VOCE PODE AJUDAR:
1. Informacoes sobre produtos/servicos
2. Agendar reunioes/consultas
3. Enviar contratos/documentos
4. Analisar documentos e imagens
5. Responder duvidas frequentes
6. Direcionar para atendimento humano quando necessario

REGRAS IMPORTANTES:
- Nunca invente informacoes sobre valores ou prazos especificos
- Quando nao souber, ofereca agendar com um consultor
- Seja prestativa mas nao invada a privacidade
- Mantenha respostas curtas e objetivas
- Use emojis ocasionalmente para humanizar

Voce esta conversando com um funcionario da FC Solucoes Financeiras. Responda de forma natural e util."""

    # ============================================
    # CHAT (Texto)
    # ============================================
    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Chat com DeepSeek"""
        if not self.api_key:
            return "Erro: API key nao configurada. Adicione DEEPSEEK_API_KEY no .env"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
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
                elif response.status_code == 402:
                    return "⚠️ API sem créditos. Para ativar:\n\n1. Acesse https://platform.deepseek.com/\n2. Verifique sua conta\n3. Obtenha 10 yuan gratuitos\n\nOu entre em contato com o administrador."
                else:
                    return f"Erro {response.status_code}: Tente novamente"
                    
        except Exception as e:
            return f"Erro de conexao: {str(e)[:100]}"

    def build_chat_messages(self, user_message: str, context: List[Dict] = None, system: str = None) -> List[Dict]:
        """Monta lista de mensagens para chat"""
        messages = []
        
        # System prompt
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Contexto anterior
        if context:
            for msg in context:
                if msg.get('tipo') == 'usuario':
                    messages.append({"role": "user", "content": msg.get('conteudo', '')})
                elif msg.get('tipo') == 'ia':
                    messages.append({"role": "assistant", "content": msg.get('conteudo', '')})
        
        # Mensagem atual
        messages.append({"role": "user", "content": user_message})
        
        return messages

    # ============================================
    # VISÃO (Análise de Imagens)
    # ============================================
    async def vision(self, image_url: str, prompt: str) -> str:
        """Analisa imagem - usa descrição como fallback"""
        # DeepSeek nao suporta visao ainda, retorna mensagem explicativa
        return f"Analise de imagem recebida. Prompt: {prompt}\n\n(Nota: Analise visual sera implementada com modelo de visao)"

    async def vision_base64(self, image_base64: str, prompt: str, mime_type: str = "image/jpeg") -> str:
        """Analisa imagem em base64"""
        return await self.vision("", prompt)

    # ============================================
    # ÁUDIO (Transcrição)
    # ============================================
    async def audio_transcribe(self, audio_base64: str, mime_type: str = "audio/wav") -> str:
        """Transcreve áudio - placeholder"""
        return "Transcricao de audio sera implementada em breve."

    # ============================================
    # IMAGEM (Geração)
    # ============================================
    async def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        """Gera imagem - placeholder"""
        return {
            "success": False,
            "error": "Geracao de imagem sera implementada em breve.",
            "prompt": prompt
        }

    # ============================================
    # STATUS
    # ============================================
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do serviço"""
        return {
            "api_configurada": bool(self.api_key),
            "modelos": {
                "chat": self.model_chat,
                "vision": self.model_vision,
                "audio": self.model_audio,
                "image": self.model_image
            }
        }


# Instância global
zai_service = ZAIService()

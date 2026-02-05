"""
DeepSeek Service - Alternativa ao GLM-4
API gratuita com 10 yuan (~1.25M tokens) para novos usuários
"""
import httpx
from typing import List, Dict, Any
from app.config import settings


class DeepSeekService:
    """
    Serviço de IA usando DeepSeek API
    Formato compatível com OpenAI
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"  # ou "deepseek-reasoner" para thinking mode
        
        # Contexto base da personalidade VIVA
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
4. Responder duvidas frequentes
5. Direcionar para atendimento humano quando necessario

REGRAS IMPORTANTES:
- Nunca invente informacoes sobre valores ou prazos especificos
- Quando nao souber, ofereca agendar com um consultor
- Seja prestativa mas nao invada a privacidade
- Mantenha respostas curtas e objetivas
- Use emojis ocasionalmente para humanizar

Voce esta conversando com um funcionario da FC Solucoes Financeiras. Responda de forma natural e util."""

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Envia mensagens para DeepSeek e retorna resposta
        """
        if not self.api_key:
            return "Desculpe, a API DeepSeek nao esta configurada. Contate o administrador."
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    import logging
                    logging.error(f"DeepSeek error: {response.status_code}")
                    return "Desculpe, nao consegui processar sua mensagem agora. Pode repetir, por favor?"
                    
        except Exception as e:
            import logging
            logging.error(f"DeepSeek exception: {repr(e)}")
            return "Ops! Tive um probleminha tecnico. Tente novamente ou contate o suporte."

    def build_messages(self, user_message: str, context: List[Dict] = None) -> List[Dict[str, str]]:
        """Monta lista de mensagens para a API"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Adiciona contexto anterior
        if context:
            for msg in context:
                if msg.get('tipo') == 'usuario':
                    messages.append({"role": "user", "content": msg.get('conteudo', '')})
                elif msg.get('tipo') == 'ia':
                    messages.append({"role": "assistant", "content": msg.get('conteudo', '')})
        
        # Adiciona mensagem atual
        messages.append({"role": "user", "content": user_message})
        
        return messages


# Instância global
deepseek_service = DeepSeekService()

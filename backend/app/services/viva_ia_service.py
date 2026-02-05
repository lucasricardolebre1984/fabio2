"""
VIVA - Assistente Virtual Inteligente
Integração com GLM-4 para atender clientes no WhatsApp
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.whatsapp_conversa import WhatsappConversa, WhatsappMensagem, TipoOrigem
from app.services.zai_service import zai_service


class VivaIAService:
    """
    VIVA - A inteligência por trás do atendimento WhatsApp
    Personalidade: Concierge profissional da FC Soluções/RezetaBrasil
    """
    
    def __init__(self):
        # Contexto base da personalidade VIVA
        self.system_prompt = """Você é VIVA, a assistente virtual inteligente da FC Soluções Financeiras e RezetaBrasil.

SUA PERSONALIDADE:
- Profissional, calorosa e eficiente
- Você conhece profundamente os serviços das empresas
- Fala de forma natural, como uma concierge experiente
- Sempre oferece ajuda antes de direcionar

SOBRE AS EMPRESAS:
**FC Soluções Financeiras**
- Consultoria empresarial e serviços financeiros
- Crédito empresarial, antecipação de recebíveis
- Clientes: Pessoa jurídica, empresas
- Tom: Profissional, corporativo, azul

**RezetaBrasil**
- Soluções de crédito pessoal
- Limpa nome, renegociação de dívidas
- Clientes: Pessoa física
- Tom: Acessível, promocional, verde

SERVIÇOS QUE VOCÊ PODE AJUDAR:
1. Informações sobre produtos/serviços
2. Agendar reuniões/consultas
3. Enviar contratos/documentos
4. Gerar imagens de campanha
5. Responder dúvidas frequentes
6. Direcionar para atendimento humano quando necessário

REGRAS IMPORTANTES:
- Nunca invente informações sobre valores ou prazos específicos
- Quando não souber, ofereça agendar com um consultor
- Seja prestativa mas não invada a privacidade
- Mantenha respostas curtas (ideal para WhatsApp)
- Use emojis ocasionalmente para humanizar

Você está em uma conversa real pelo WhatsApp. Responda de forma natural e útil."""

    async def processar_mensagem(
        self,
        numero: str,
        mensagem: str,
        conversa: WhatsappConversa,
        db: AsyncSession
    ) -> str:
        """
        Processa mensagem do usuário e gera resposta da IA
        """
        # Busca histórico recente (últimas 10 mensagens)
        historico = await self._get_historico(conversa, db)
        
        # Monta contexto completo
        messages = self._montar_contexto(historico, mensagem)
        
        # Chama API GLM-4
        resposta = await self._chamar_glm4(messages)
        
        return resposta
    
    async def _get_historico(
        self,
        conversa: WhatsappConversa,
        db: AsyncSession,
        limite: int = 10
    ) -> List[Dict[str, str]]:
        """Busca histórico recente da conversa"""
        from sqlalchemy import select
        
        stmt = (
            select(WhatsappMensagem)
            .where(WhatsappMensagem.conversa_id == conversa.id)
            .order_by(WhatsappMensagem.created_at.desc())
            .limit(limite)
        )
        result = await db.execute(stmt)
        mensagens = result.scalars().all()
        
        # Inverte para ordem cronológica
        mensagens = list(reversed(mensagens))
        
        historico = []
        for msg in mensagens:
            role = "user" if msg.tipo_origem == TipoOrigem.USUARIO else "assistant"
            historico.append({"role": role, "content": msg.conteudo})
        
        return historico
    
    def _montar_contexto(
        self,
        historico: List[Dict[str, str]],
        mensagem_atual: str
    ) -> List[Dict[str, str]]:
        """Monta o contexto completo para a IA"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Adiciona histórico
        messages.extend(historico)
        
        # Adiciona mensagem atual
        messages.append({"role": "user", "content": mensagem_atual})
        
        return messages
    
    async def _chamar_glm4(self, messages: List[Dict[str, str]]) -> str:
        """Chama API Z.AI / GLM-4 para gerar resposta"""
        try:
            resposta = await zai_service.chat(messages, temperature=0.7, max_tokens=800)
            return resposta
        except Exception as e:
            import logging
            logging.error(f"Erro ao chamar Z.AI: {repr(e)}")
            return "Ops! Tive um probleminha técnico. Tente novamente ou digite 'atendente' para falar com uma pessoa."


# Instância global
viva_service = VivaIAService()

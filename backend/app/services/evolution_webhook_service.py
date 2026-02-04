"""
Serviço de Webhook para Evolution API
Recebe mensagens do WhatsApp e integra com IA VIVA
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.whatsapp_conversa import (
    WhatsappConversa, 
    WhatsappMensagem, 
    TipoOrigem, 
    StatusConversa
)
from app.services.viva_ia_service import viva_service


class EvolutionWebhookService:
    """
    Processa webhooks recebidos do Evolution Manager
    """
    
    async def processar_webhook(
        self,
        data: Dict[str, Any],
        db: AsyncSession
    ) -> bool:
        """
        Processa evento recebido do Evolution API
        """
        event_type = data.get("event")
        
        if event_type == "messages.upsert":
            return await self._processar_mensagem(data, db)
        elif event_type == "connection.update":
            return await self._processar_status_conexao(data, db)
        
        return True  # Evento não tratado, mas não é erro
    
    async def _processar_mensagem(
        self,
        data: Dict[str, Any],
        db: AsyncSession
    ) -> bool:
        """
        Processa nova mensagem recebida
        """
        try:
            message_data = data.get("data", {}).get("message", {})
            instance_data = data.get("instance", {})
            
            # Extrai informações
            numero = message_data.get("key", {}).get("remoteJid", "").split("@")[0]
            texto = self._extrair_texto_mensagem(message_data)
            instance_name = instance_data.get("instanceName", "Teste")
            
            if not numero or not texto:
                return True  # Ignora mensagens sem conteúdo válido
            
            # Busca ou cria conversa
            conversa = await self._get_ou_criar_conversa(
                numero=numero,
                instance_name=instance_name,
                db=db
            )
            
            # Salva mensagem do usuário
            msg_usuario = WhatsappMensagem(
                conversa_id=conversa.id,
                tipo_origem=TipoOrigem.USUARIO,
                conteudo=texto,
                message_id=message_data.get("key", {}).get("id")
            )
            db.add(msg_usuario)
            
            # Atualiza timestamp da conversa
            conversa.ultima_mensagem_em = datetime.utcnow()
            await db.commit()
            
            # Gera resposta da IA
            resposta_ia = await viva_service.processar_mensagem(
                numero=numero,
                mensagem=texto,
                conversa=conversa,
                db=db
            )
            
            # Envia resposta pelo WhatsApp (TODO: implementar envio real)
            # Por enquanto apenas salva no banco
            enviado = True  # Assumindo sucesso
            
            # Salva resposta no banco
            msg_ia = WhatsappMensagem(
                conversa_id=conversa.id,
                tipo_origem=TipoOrigem.IA,
                conteudo=resposta_ia,
                enviada=enviado
            )
            db.add(msg_ia)
            await db.commit()
            
            return True
            
        except Exception as e:
            print(f"Erro ao processar mensagem webhook: {str(e)}")
            return False
    
    def _extrair_texto_mensagem(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extrai texto da mensagem do payload"""
        try:
            # Mensagem de texto simples
            if "conversation" in message_data:
                return message_data["conversation"]
            
            # Mensagem extendida
            if "extendedTextMessage" in message_data:
                return message_data["extendedTextMessage"].get("text", "")
            
            # Outros tipos (imagem com legenda, etc)
            if "imageMessage" in message_data:
                return message_data["imageMessage"].get("caption", "[imagem]")
            
            return None
        except:
            return None
    
    async def _get_ou_criar_conversa(
        self,
        numero: str,
        instance_name: str,
        db: AsyncSession
    ) -> WhatsappConversa:
        """Busca conversa existente ou cria nova"""
        
        stmt = select(WhatsappConversa).where(
            and_(
                WhatsappConversa.numero_telefone == numero,
                WhatsappConversa.instance_name == instance_name,
                WhatsappConversa.status == StatusConversa.ATIVA
            )
        )
        result = await db.execute(stmt)
        conversa = result.scalar_one_or_none()
        
        if not conversa:
            conversa = WhatsappConversa(
                numero_telefone=numero,
                instance_name=instance_name,
                status=StatusConversa.ATIVA,
                contexto_ia={}
            )
            db.add(conversa)
            await db.commit()
            await db.refresh(conversa)
        
        return conversa
    
    async def _processar_status_conexao(
        self,
        data: Dict[str, Any],
        db: AsyncSession
    ) -> bool:
        """Processa atualizações de status de conexão"""
        # TODO: Implementar se necessário
        return True


# Instância global
webhook_service = EvolutionWebhookService()

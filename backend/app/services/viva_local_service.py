"""
VIVA Local Service - Funciona sem API externa
Usa templates e respostas pré-programadas
"""
import random
from typing import List, Dict, Any


class VivaLocalService:
    """
    Serviço local - não requer API key
    Responde com templates baseados nos prompts
    """
    
    def __init__(self):
        self.respostas_gerais = [
            "Olá! Sou a VIVA, assistente virtual da FC Soluções Financeiras.\n\n💡 **Como posso ajudar?**\n\n• Informações sobre serviços\n• Criar contratos\n• Agendar atendimentos\n• Dúvidas sobre limpa nome\n\nSelecione um modo especial no menu lateral ou digite sua pergunta!",
            
            "Bem-vindo à FC Soluções Financeiras! 🏢\n\nSou a VIVA, sua assistente virtual. Posso ajudar com:\n\n✅ **FC Soluções** - Crédito empresarial\n✅ **RezetaBrasil** - Limpa nome e crédito pessoal\n\nO que você precisa hoje?",
            
            "Olá! 👋\n\nEstou aqui para facilitar seu trabalho na FC Soluções.\n\n**Modos disponíveis no menu lateral:**\n• Landing Pages - Criar sites\n• Logos & Brand - Identidade visual\n• Imagens FC - Materiais para FC Soluções\n• Imagens Rezeta - Campanhas RezetaBrasil\n\nComo posso ajudar?"
        ]
        
        self.respostas_landing = """🚀 **CRIADOR DE LANDING PAGES**

Vou criar uma landing page profissional para você!

**Me informe:**
1. Qual o objetivo? (captar leads, vender, informar)
2. Qual produto/serviço?
3. Público-alvo?
4. Tom de voz? (formal, descontraído, técnico)

**Exemplo:**
"Crie uma landing page para captar leads de empresas que precisam de antecipação de recebíveis. Tom profissional, focado em FC Soluções."

Pronto? Me envie os detalhes! 💪"""

        self.respostas_logo = """🎨 **GERADOR DE LOGOS & BRAND**

Vou criar sua identidade visual!

**Informe:**
1. Nome da marca
2. Segmento (financeiro, tecnologia, etc.)
3. Cores preferidas
4. Estilo? (moderno, clássico, minimalista, ousado)
5. Elementos que gostaria? (ícones, formas, tipografia)

**Exemplo:**
"Crie um logo para 'RezetaBrasil' focado em crédito pessoal. Cores verde e branco, estilo moderno e acessível."

Me envie sua solicitação! 🎯"""

        self.respostas_fc = """🏢 **IMAGENS FC SOLUÇÕES**

Vou criar imagens profissionais para FC Soluções Financeiras!

**Tom:** Corporativo, confiável, azul
**Foco:** Empresas, crédito empresarial, antecipação

**Tipos de imagens:**
• Posts para redes sociais
• Banners para site
• Materiais de apresentação
• Campanhas de email

**Me diga:**
1. Tipo de imagem
2. Mensagem principal
3. CTA (call-to-action)

Exemplo: "Crie um banner para LinkedIn sobre antecipação de recebíveis com CTA 'Fale com um consultor'"

Vamos lá! 📊"""

        self.respostas_rezeta = """💚 **IMAGENS REZETABRASIL**

Vou criar imagens para campanhas RezetaBrasil!

**Tom:** Acessível, promocional, verde
**Foco:** Pessoa física, limpa nome, crédito pessoal

**Tipos de imagens:**
• Posts Instagram/Facebook
• Stories
• Anúncios patrocinados
• Flyers promocionais

**Me diga:**
1. Tipo de imagem
2. Oferta/mensagem
3. Público-alvo

Exemplo: "Crie um post para Instagram sobre limpa nome com desconto de 40%. Tom promocional e animado!"

Manda ver! 🚀"""

    async def chat(self, messages: List[Dict[str, str]], modo: str = None) -> str:
        """Responde baseado no modo ou pergunta"""
        
        # Detecta modo pela última mensagem
        ultima_msg = messages[-1].get('content', '').lower() if messages else ''
        
        # Respostas baseadas no modo
        if modo == 'CRIADORLANDPAGE' or 'landing' in ultima_msg or 'site' in ultima_msg:
            return self.respostas_landing
        
        elif modo == 'LOGO' or 'logo' in ultima_msg or 'brand' in ultima_msg or 'identidade' in ultima_msg:
            return self.respostas_logo
        
        elif modo == 'FC' or 'fc solucoes' in ultima_msg or 'empresarial' in ultima_msg:
            return self.respostas_fc
        
        elif modo == 'REZETA' or 'rezeta' in ultima_msg or 'limpa nome' in ultima_msg:
            return self.respostas_rezeta
        
        # Respostas para perguntas comuns
        elif 'contrato' in ultima_msg or 'bacen' in ultima_msg:
            return """📄 **CONTRATOS FC SOLUÇÕES**

Temos templates prontos para:
• BACEN - Contrato padrão BACEN
• SERASA - Consulta SERASA
• PROTESTO - Consulta Protesto

Para criar um contrato:
1. Vá em **Contratos** no menu lateral
2. Selecione o template desejado
3. Preencha os dados do cliente
4. Gere o PDF

Posso ajudar com mais alguma coisa?"""

        elif 'servico' in ultima_msg or 'o que faz' in ultima_msg:
            return """🏢 **SERVIÇOS FC SOLUÇÕES FINANCEIRAS**

**FC Soluções (Pessoa Jurídica):**
• Crédito empresarial
• Antecipação de recebíveis
• Consultoria financeira
• Gestão de cash flow

**RezetaBrasil (Pessoa Física):**
• Limpa nome
• Renegociação de dívidas
• Crédito pessoal
• Consultoria de crédito

Quer saber mais sobre algum serviço específico?"""

        else:
            # Resposta geral aleatória
            return random.choice(self.respostas_gerais)

    def build_messages(self, user_message: str, context: List[Dict] = None) -> List[Dict[str, str]]:
        """Monta lista de mensagens"""
        messages = [{"role": "system", "content": "VIVA Assistente"}]
        
        if context:
            for msg in context:
                if msg.get('tipo') == 'usuario':
                    messages.append({"role": "user", "content": msg.get('conteudo', '')})
                elif msg.get('tipo') == 'ia':
                    messages.append({"role": "assistant", "content": msg.get('conteudo', '')})
        
        messages.append({"role": "user", "content": user_message})
        return messages

    async def vision(self, image_base64: str, prompt: str) -> str:
        """Análise de imagem - modo local"""
        return f"📷 **Análise de Imagem**\n\nSolicitação: {prompt}\n\n(Imagem recebida para análise. Funcionalidade completa disponível com API ativada.)\n\n**Posso ajudar com:**\n• Descrição de elementos visuais\n• Sugestões de melhorias\n• Identificação de padrões\n• Análise de documentos"

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do serviço"""
        return {
            "api_configurada": True,
            "modelo": "VIVA Local (Sem API)",
            "tipo": "Templates pré-programados",
            "gratuito": True
        }


# Instância global
viva_local_service = VivaLocalService()

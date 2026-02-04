"""
🧠 CÉREBRO INSTITUCIONAL v2 - Simplificado
FC Soluções Financeiras + RezetaBrasil
Automania-AI
"""
from typing import Dict, Tuple


class BrainImageService:
    """
    Transforma prompts simples em campanhas visuais profissionais.
    Versão simplificada para FC e Rezeta.
    """
    
    # Contexto das empresas
    EMPRESAS = {
        'fc': {
            'nome': 'FC Soluções Financeiras',
            'publico': 'B2B, empresários, profissionais liberais',
            'paleta': '#071c4a (azul escuro), #00a3ff (azul claro), #727979 (cinza)',
            'estilo': 'corporativo, minimalista, elegante',
            'proibicao': 'NUNCA usar verde, NUNCA mencionar Rezeta',
            'logo': 'storage/logos/fc_logo.png'
        },
        'rezeta': {
            'nome': 'RezetaBrasil',
            'publico': 'B2C, negativados, limpar nome',
            'paleta': '#1E3A5F (azul marinho), #3DAA7F (verde esmeralda)',
            'estilo': 'promocional, overlays, chamativo',
            'campanhas': 'Limpa Nome, Diagnóstico 360, Crédito PJ',
            'logo': 'storage/logos/rezeta_logo.png'
        }
    }
    
    # Realismo criativo (breve)
    REALISMO = "fotografia comercial profissional, iluminação de estúdio, cores corporativas exatas, sem distorções, sem watermark, pessoas reais, expressões naturais"
    
    # Técnicas por formato
    FORMATO_TECNICAS = {
        '1:1': 'composição centralizada, lente 50mm, feed Instagram',
        '16:9': 'composição horizontal, lente 35mm, banners e stories',
        '9:16': 'composição vertical, lente 24mm, stories e reels'
    }
    
    def detectar_empresa(self, prompt: str) -> str:
        """Detecta qual empresa baseado no prompt."""
        prompt_lower = prompt.lower()
        
        # Palavras-chave Rezeta
        rezeta_keywords = ['rezeta', 'limpar nome', 'nome sujo', 'negativado', 
                          'serasa', 'spc', 'bacen', 'checkmark', 'check']
        
        # Palavras-chave FC
        fc_keywords = ['fc', 'soluções financeiras', 'empresário', 'pj', 
                      'crédito empresarial', 'consultoria']
        
        for kw in rezeta_keywords:
            if kw in prompt_lower:
                return 'rezeta'
        
        for kw in fc_keywords:
            if kw in prompt_lower:
                return 'fc'
        
        # Default: FC (mais conservador)
        return 'fc'
    
    def generate_technical_prompt(self, user_prompt: str, formato: str = '1:1', 
                                  empresa: str = None) -> Tuple[str, str]:
        """
        Gera prompt técnico profissional.
        
        Args:
            user_prompt: Prompt do usuário
            formato: 1:1, 16:9 ou 9:16
            empresa: 'fc' ou 'rezeta' (auto-detecta se não informado)
            
        Returns:
            Tuple (prompt_tecnico, negative_prompt)
        """
        # Detectar empresa
        if not empresa:
            empresa = self.detectar_empresa(user_prompt)
        
        emp = self.EMPRESAS[empresa]
        tecnica = self.FORMATO_TECNICAS.get(formato, self.FORMATO_TECNICAS['1:1'])
        
        # Construir prompt simplificado
        technical_prompt = f"""Professional marketing image for {emp['nome']}, {user_prompt}. 
Paleta: {emp['paleta']}. 
Estilo: {emp['estilo']}. 
{tecnica}. 
{self.REALISMO}"""
        
        # Negative prompt padrão
        negative_prompt = "blurry, low quality, distorted, deformed, ugly, watermark, signature, text overlay, cartoon, illustration, painting, drawing"
        
        return technical_prompt, negative_prompt


# Instância singleton
brain_service = BrainImageService()

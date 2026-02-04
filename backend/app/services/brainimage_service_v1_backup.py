"""
CÉREBRO INSTITUCIONAL - Serviço de Otimização de Prompts

Baseado em: docs/PROMPTS/BRAINIMAGE.md
Função: Diretor Criativo + Especialista em Realismo + Designer Corporativo
"""
import re
from typing import Dict, List, Tuple


class BrainImageService:
    """
    Transforma prompts simples em prompts técnicos profissionais
    seguindo as diretrizes do CÉREBRO INSTITUCIONAL.
    """
    
    # Palavras-chave para detectar tipo de campanha
    KEYWORD_MAP = {
        'consorcio': {
            'elements': ['família feliz', 'chaves de casa', 'carro novo', 'realização'],
            'colors': ['azul confiança', 'dourado sucesso', 'branco pureza'],
            'mood': 'esperança e realização de sonhos'
        },
        'financiamento': {
            'elements': ['documentos organizados', 'aperto de mão', 'crescimento'],
            'colors': ['azul corporativo', 'verde prosperidade'],
            'mood': 'segurança financeira e crescimento'
        },
        'limpa nome': {
            'elements': ['cadeado aberto', 'puzzle completo', 'caminho livre'],
            'colors': ['verde liberdade', 'azul tranquilidade'],
            'mood': 'liberdade financeira e alívio'
        },
        'emprestimo': {
            'elements': ['contando dinheiro', 'calculadora', 'assinatura contrato'],
            'colors': ['dourado riqueza', 'azul confiança'],
            'mood': 'oportunidade e crescimento'
        },
        'ano novo': {
            'elements': ['fogos de artifício', 'calendário', 'celebração', 'família reunida'],
            'colors': ['dourado festivo', 'prata elegância', 'vermelho energia'],
            'mood': 'celebração e renovação'
        },
        'campanha': {
            'elements': ['pessoas sorrindo', 'sucesso', 'conquista'],
            'colors': ['cores vibrantes', 'contraste alto'],
            'mood': 'positividade e resultados'
        }
    }
    
    # Técnicas fotográficas por formato
    FORMAT_TECHNIQUES = {
        '1:1': {
            'composition': 'composição centralizada, foco direto no produto/serviço',
            'lens': 'lente 50mm',
            'depth': 'profundidade de campo média',
            'use_case': 'feed Instagram, posts sociais'
        },
        '16:9': {
            'composition': 'composição horizontal panorâmica, espaço para texto',
            'lens': 'lente 35mm',
            'depth': 'profundidade de campo ampla',
            'use_case': 'banners, capas, stories horizontais'
        },
        '9:16': {
            'composition': 'composição vertical, hierarquia de cima para baixo',
            'lens': 'lente 24mm',
            'depth': 'profundidade progressiva',
            'use_case': 'stories verticais, reels, TikTok'
        }
    }
    
    # Estilos visuais institucionais
    STYLE_PRESETS = {
        'professional': 'fotografia comercial profissional, iluminação de estúdio, cores corporativas',
        'modern': 'design moderno e minimalista, espaço negativo, tipografia clean',
        'premium': 'acabamento premium, texturas sofisticadas, iluminação dramática',
        'friendly': 'atmosfera acolhedora, pessoas sorrindo, cores quentes',
        'corporate': 'ambiente corporativo, escritório moderno, executivos profissionais'
    }
    
    def __init__(self):
        """Initialize BrainImage service."""
        pass
    
    def analyze_prompt(self, user_prompt: str) -> Dict:
        """
        Analisa o prompt do usuário e extrai intenções.
        
        Args:
            user_prompt: Texto digitado pelo usuário
            
        Returns:
            Dicionário com análise do prompt
        """
        prompt_lower = user_prompt.lower()
        
        analysis = {
            'detected_keywords': [],
            'campaign_type': 'generic',
            'target_audience': 'geral',
            'objective': 'awareness',
            'tone': 'professional',
            'elements': [],
            'colors': [],
            'mood': 'profissional'
        }
        
        # Detecta palavras-chave
        for keyword, data in self.KEYWORD_MAP.items():
            if keyword in prompt_lower:
                analysis['detected_keywords'].append(keyword)
                analysis['campaign_type'] = keyword
                analysis['elements'] = data['elements']
                analysis['colors'] = data['colors']
                analysis['mood'] = data['mood']
        
        # Detecta objetivo
        if any(word in prompt_lower for word in ['venda', 'vender', 'compre', 'adquira']):
            analysis['objective'] = 'conversion'
        elif any(word in prompt_lower for word in ['parabenize', 'feliz', 'celebre']):
            analysis['objective'] = 'celebration'
        elif any(word in prompt_lower for word in ['ajuda', 'auxilie', 'solução']):
            analysis['objective'] = 'problem_solution'
        
        # Detecta tom
        if any(word in prompt_lower for word in ['elegante', 'sofisticado', 'premium']):
            analysis['tone'] = 'premium'
        elif any(word in prompt_lower for word in ['amigável', 'acolhedor', 'família']):
            analysis['tone'] = 'friendly'
        elif any(word in prompt_lower for word in ['moderno', 'atual', 'novo']):
            analysis['tone'] = 'modern'
        
        return analysis
    
    def generate_technical_prompt(
        self, 
        user_prompt: str, 
        formato: str = '1:1',
        style_preset: str = 'professional'
    ) -> Tuple[str, str]:
        """
        Gera prompt técnico profissional baseado no CÉREBRO INSTITUCIONAL.
        
        Args:
            user_prompt: Texto do usuário
            formato: Proporção da imagem (1:1, 16:9, 9:16)
            style_preset: Estilo visual ('professional', 'modern', 'premium', etc.)
            
        Returns:
            Tupla (prompt_final, negative_prompt)
        """
        # Analisa o prompt
        analysis = self.analyze_prompt(user_prompt)
        
        # Obtém técnicas do formato
        format_tech = self.FORMAT_TECHNIQUES.get(formato, self.FORMAT_TECHNIQUES['1:1'])
        
        # Obtém estilo
        style = self.STYLE_PRESETS.get(style_preset, self.STYLE_PRESETS['professional'])
        
        # Constrói o prompt técnico
        sections = []
        
        # 1. Elementos principais (do usuário + detectados)
        main_elements = [user_prompt]
        if analysis['elements']:
            main_elements.extend(analysis['elements'][:2])  # Top 2 elementos detectados
        
        sections.append(
            f"Professional marketing image for financial services campaign: "
            f"{', '.join(main_elements)}. "
        )
        
        # 2. Composição e técnica fotográfica
        sections.append(
            f"{format_tech['composition']}. "
            f"Shot with {format_tech['lens']}, {format_tech['depth']}. "
            f"Professional {format_tech['use_case']}. "
        )
        
        # 3. Estilo visual
        sections.append(
            f"{style}. "
            f"{analysis['mood'].capitalize()} atmosphere. "
        )
        
        # 4. Paleta de cores
        if analysis['colors']:
            sections.append(
                f"Color palette: {', '.join(analysis['colors'][:3])}. "
            )
        else:
            sections.append(
                "Color palette: corporate blue, professional white, trust gold. "
            )
        
        # 5. Iluminação e materiais
        sections.append(
            "Studio lighting setup with soft key light and subtle fill. "
            "High-quality materials, realistic textures, subtle film grain. "
        )
        
        # 6. Diretrizes de realismo
        sections.append(
            "Photorealistic rendering, physically accurate lighting, "
            "natural shadows, coherent scale and perspective. "
            "No AI artifacts, no distorted features, no watermark. "
        )
        
        # Monta prompt final
        final_prompt = " ".join(sections)
        
        # Negative prompt otimizado
        negative_prompt = (
            "blurry, low quality, distorted, deformed, ugly, duplicate, "
            "watermark, signature, text overlay, logo, cartoon, illustration, "
            "painting, drawing, sketch, artificial look, plastic skin, "
            "extra fingers, mutated hands, poorly drawn hands, "
            "poorly drawn face, mutation, deformed features, "
            "bad anatomy, gross proportions, malformed limbs, "
            "missing arms, missing legs, extra arms, extra legs, "
            "fused fingers, too many fingers, long neck, "
            "cross-eyed, mutated eyes, bad body proportions"
        )
        
        return final_prompt, negative_prompt
    
    def generate_variations(
        self, 
        user_prompt: str, 
        formato: str = '1:1'
    ) -> List[Dict]:
        """
        Gera variações criativas do prompt (A/B/C testing).
        
        Args:
            user_prompt: Texto do usuário
            formato: Proporção da imagem
            
        Returns:
            Lista de variações com brief
        """
        analysis = self.analyze_prompt(user_prompt)
        
        variations = [
            {
                'id': 'A',
                'name': 'Clássica Corporativa',
                'focus': 'executivos profissionais em ambiente corporativo',
                'style': 'corporate',
                'lighting': 'iluminação de escritório profissional'
            },
            {
                'id': 'B',
                'name': 'Moderna e Clean',
                'focus': 'design minimalista com elementos modernos',
                'style': 'modern',
                'lighting': 'luz natural suave e clean'
            },
            {
                'id': 'C',
                'name': 'Emocional e Acolhedora',
                'focus': 'família/pessoas felizes celebrando conquistas',
                'style': 'friendly',
                'lighting': 'luz quente e acolhedora'
            }
        ]
        
        # Gera prompts para cada variação
        results = []
        for var in variations:
            prompt, negative = self.generate_technical_prompt(
                f"{user_prompt}, {var['focus']}, {var['lighting']}",
                formato,
                var['style']
            )
            results.append({
                **var,
                'prompt': prompt,
                'negative_prompt': negative
            })
        
        return results
    
    def enhance_uploaded_image_prompt(
        self, 
        description: str,
        edit_request: str
    ) -> str:
        """
        Gera prompt para edição de imagem existente (IMG→IMG).
        
        Args:
            description: Descrição da imagem original
            edit_request: O que o usuário quer alterar
            
        Returns:
            Prompt técnico para edição
        """
        sections = [
            f"Edit professional image: {description}. ",
            f"Changes requested: {edit_request}. ",
            "Preserve original identity and composition. "
            "Maintain consistent lighting and perspective. "
            "Seamless integration of new elements. "
            "Professional retouching quality, no visible artifacts."
        ]
        
        return " ".join(sections)


# Instância singleton
brain_service = BrainImageService()

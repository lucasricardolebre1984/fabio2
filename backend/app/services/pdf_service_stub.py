"""
STUB temporário para PDF service - WeasyPrint com problemas no Windows
Será substituído pela implementação real após instalar GTK+
"""

class PDFService:
    async def generate_contrato_pdf(self, html_content: str, output_path: str = None) -> bytes:
        """Stub - retorna HTML como bytes para teste"""
        # Por enquanto, retorna o próprio HTML
        # Em produção, usar WeasyPrint ou outra lib
        return html_content.encode('utf-8')
    
    async def generate_from_template(self, template_data: dict, cliente_data: dict, contrato_data: dict) -> bytes:
        """Stub - retorna JSON como bytes para teste"""
        import json
        result = {
            "template": template_data.get('nome', 'template'),
            "cliente": cliente_data,
            "contrato": contrato_data,
            "message": "PDF generation disabled - GTK libraries not installed"
        }
        return json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8')

pdf_service = PDFService()

"""PDF service - Gera contratos em PDF usando WeasyPrint."""
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID

from jinja2 import Template
from weasyprint import HTML, CSS

from app.config import settings
from app.services.extenso_service import ExtensoService


class PDFService:
    """Service for generating PDF contracts."""
    
    # CSS institucional para contratos
    CSS_INSTITUCIONAL = """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "FC Soluções Financeiras";
            font-size: 10pt;
            color: #627d98;
        }
        @bottom-center {
            content: "(16) 99301-7396 | contato@fcsolucoesfinanceiras.com";
            font-size: 9pt;
            color: #718096;
        }
    }
    
    body {
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #1a202c;
    }
    
    .header {
        text-align: center;
        margin-bottom: 2cm;
        border-bottom: 2px solid #627d98;
        padding-bottom: 1cm;
    }
    
    .header h1 {
        font-size: 18pt;
        color: #102a43;
        margin: 0;
        text-transform: uppercase;
    }
    
    .header .subtitle {
        font-size: 12pt;
        color: #486581;
        margin-top: 0.5cm;
    }
    
    .partes {
        margin: 1cm 0;
    }
    
    .parte {
        margin-bottom: 0.8cm;
    }
    
    .parte-label {
        font-weight: bold;
        text-transform: uppercase;
        color: #102a43;
    }
    
    .clausula {
        margin: 1cm 0;
        text-align: justify;
    }
    
    .clausula-titulo {
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 0.3cm;
        color: #102a43;
    }
    
    .clausula-numero {
        color: #627d98;
    }
    
    .valor-destaque {
        font-weight: bold;
        color: #102a43;
    }
    
    .assinaturas {
        margin-top: 2cm;
        page-break-inside: avoid;
    }
    
    .assinatura-linha {
        border-top: 1px solid #000;
        width: 8cm;
        margin-top: 1.5cm;
        padding-top: 0.2cm;
        text-align: center;
    }
    
    .data-local {
        margin: 1cm 0;
        text-align: right;
    }
    
    .testemunhas {
        margin-top: 1cm;
    }
    """
    
    def __init__(self):
        self.storage_path = settings.STORAGE_LOCAL_PATH
        os.makedirs(self.storage_path, exist_ok=True)
    
    def generate_contrato_bacen(
        self,
        contrato_id: UUID,
        dados: Dict[str, Any]
    ) -> str:
        """
        Generate Bacen contract PDF.
        
        Args:
            contrato_id: Contract UUID
            dados: Contract data dictionary
            
        Returns:
            Path to generated PDF file
        """
        html_content = self._render_template_bacen(dados)
        
        # Generate filename
        filename = f"contrato_{dados.get('numero', str(contrato_id))}.pdf"
        filepath = os.path.join(self.storage_path, filename)
        
        # Generate PDF
        html = HTML(string=html_content)
        css = CSS(string=self.CSS_INSTITUCIONAL)
        html.write_pdf(filepath, stylesheets=[css])
        
        return filepath
    
    def _render_template_bacen(self, dados: Dict[str, Any]) -> str:
        """Render Bacen contract HTML template."""
        
        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contrato {{ numero }}</title>
        </head>
        <body>
            <div class="header">
                <h1>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</h1>
                <div class="subtitle">Remoção de Apontamentos SCR - Banco Central</div>
            </div>
            
            <div class="partes">
                <div class="parte">
                    <span class="parte-label">CONTRATANTE:</span><br>
                    <strong>Nome:</strong> {{ contratante_nome }}<br>
                    <strong>CPF/CNPJ:</strong> {{ contratante_documento }}<br>
                    <strong>E-mail:</strong> {{ contratante_email }}<br>
                    {% if contratante_telefone %}
                    <strong>Telefone:</strong> {{ contratante_telefone }}<br>
                    {% endif %}
                    <strong>Endereço:</strong> {{ contratante_endereco }}
                </div>
                
                <div class="parte">
                    <span class="parte-label">CONTRATADA:</span><br>
                    <strong>Nome:</strong> FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA<br>
                    <strong>CNPJ:</strong> 57.815.628/0001-62<br>
                    <strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com<br>
                    <strong>Endereço:</strong> Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, 
                    Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100
                </div>
            </div>
            
            <p>As partes acima identificadas têm, entre si, justo e acertado o presente 
            Contrato de Prestação de Serviços, que se regerá pelas cláusulas seguintes:</p>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA PRIMEIRA</span> - DO OBJETO
                </div>
                <p>O presente contrato tem como objeto a prestação de serviços de consultoria e 
                intermediação administrativa pela CONTRATADA em favor do(a) CONTRATANTE, 
                visando a adoção de procedimentos administrativos para a regularização de 
                apontamentos de prejuízo registrados no Sistema de Informações de Crédito 
                (SCR) do Banco Central do Brasil.</p>
                
                <p>Fica claro entre as partes que este serviço não se trata de quitação ou 
                pagamento de dívidas, mas sim de um procedimento administrativo para a 
                regularização dos registros no SCR.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA SEGUNDA</span> - DAS OBRIGAÇÕES DA CONTRATADA
                </div>
                <p>A CONTRATADA se compromete a:</p>
                <p>a) Realizar uma análise detalhada da situação do(a) CONTRATANTE junto ao SCR;<br>
                b) Elaborar e protocolar os requerimentos administrativos necessários;<br>
                c) Acompanhar o andamento dos procedimentos;<br>
                d) Manter o(a) CONTRATANTE informado sobre as etapas do processo.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA TERCEIRA</span> - DAS OBRIGAÇÕES DO(A) CONTRATANTE
                </div>
                <p>O(A) CONTRATANTE se compromete a:</p>
                <p>a) Fornecer todos os documentos e informações solicitados;<br>
                b) Efetuar o pagamento dos honorários nas datas acordadas;<br>
                c) Não tratar diretamente com as instituições financeiras sem anuência da CONTRATADA.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA QUARTA</span> - DO VALOR E DA FORMA DE PAGAMENTO
                </div>
                <p>Pelos serviços prestados, o(a) CONTRATANTE pagará à CONTRATADA o valor 
                total de <span class="valor-destaque">R$ {{ valor_total }} ({{ valor_total_extenso }})</span>, 
                a ser pago da seguinte forma:</p>
                
                <p><strong>Entrada:</strong> R$ {{ valor_entrada }} ({{ valor_entrada_extenso }}), 
                a ser paga no ato da assinatura deste contrato.</p>
                
                <p><strong>Parcelas:</strong> {{ qtd_parcelas }} ({{ qtd_parcelas_extenso }}) 
                parcelas de R$ {{ valor_parcela }} ({{ valor_parcela_extenso }}), com 
                vencimento em {{ prazo_1 }} ({{ prazo_1_extenso }}) e 
                {{ prazo_2 }} ({{ prazo_2_extenso }}) dias, respectivamente.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA QUINTA</span> - DO PRAZO DE EXECUÇÃO
                </div>
                <p>O prazo estimado para a conclusão dos serviços é de 45 (quarenta e cinco) 
                a 60 (sessenta) dias úteis, contados a partir da data de assinatura deste 
                instrumento e da confirmação do pagamento da entrada.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA SEXTA</span> - DA GARANTIA DE RESULTADO
                </div>
                <p>O serviço objeto deste contrato é de resultado. Caso a CONTRATADA não 
                comprove a conclusão do serviço no prazo máximo de 60 (sessenta) dias úteis, 
                o presente contrato será considerado automaticamente rescindido.</p>
                
                <p>Na hipótese de rescisão por descumprimento do prazo, a CONTRATADA deverá 
                realizar a devolução integral dos valores já pagos, no prazo de até 30 
                (trinta) dias úteis.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA SÉTIMA</span> - DO INADIMPLEMENTO
                </div>
                <p>Em caso de atraso no pagamento de qualquer parcela, o valor devido será 
                acrescido de:</p>
                <p>a) Multa de 10% (dez por cento) sobre o valor da parcela em atraso;<br>
                b) Juros de mora de 1% (um por cento) ao mês, calculados pro rata die;<br>
                c) Correção monetária pelo índice IPCA/IBGE.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA OITAVA</span> - DA ALOCAÇÃO DE RECURSOS
                </div>
                <p>Ao assinar este contrato, o(a) CONTRATANTE autoriza a alocação imediata 
                e irreversível dos recursos necessários para o protocolo e acompanhamento 
                do procedimento administrativo.</p>
                
                <p>O(A) CONTRATANTE manifesta seu pleno acordo de que, após a assinatura, 
                não haverá devolução dos valores pagos em caso de desistência unilateral.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA NONA</span> - DA CONFIDENCIALIDADE
                </div>
                <p>As partes se comprometem a manter em sigilo todas as informações e 
                documentos a que tiverem acesso em decorrência deste contrato.</p>
            </div>
            
            <div class="clausula">
                <div class="clausula-titulo">
                    <span class="clausula-numero">CLÁUSULA DÉCIMA</span> - DO FORO
                </div>
                <p>Para dirimir quaisquer controvérsias, as partes elegem o foro da 
                Comarca de São Paulo/SP.</p>
            </div>
            
            <div class="data-local">
                {{ local_assinatura }}, {{ data_assinatura }}.
            </div>
            
            <div class="assinaturas">
                <table style="width: 100%;">
                    <tr>
                        <td style="width: 50%; text-align: center;">
                            <div class="assinatura-linha">
                                {{ contratante_nome }}<br>
                                <strong>CONTRATANTE</strong>
                            </div>
                        </td>
                        <td style="width: 50%; text-align: center;">
                            <div class="assinatura-linha">
                                FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA<br>
                                <strong>CONTRATADA</strong>
                            </div>
                        </td>
                    </tr>
                </table>
                
                <div class="testemunhas">
                    <p><strong>Testemunhas:</strong></p>
                    <p>1. _________________________________<br>
                       Nome:<br>
                       CPF:</p>
                    <p>2. _________________________________<br>
                       Nome:<br>
                       CPF:</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_html)
        return template.render(**dados)

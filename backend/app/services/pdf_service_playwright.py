"""PDF Service using Playwright."""
from typing import Optional
from uuid import UUID
from datetime import datetime
import json

from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contrato import Contrato


class PDFService:
    """PDF generation service using Playwright."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_contrato_pdf(self, contrato_id: UUID) -> Optional[bytes]:
        """Generate PDF for a contract using Playwright."""
        import traceback
        
        try:
            # Get contract data directly to avoid circular import
            result = await self.db.execute(select(Contrato).where(Contrato.id == contrato_id))
            contrato = result.scalar_one_or_none()
            
            if not contrato:
                print(f"Contrato {contrato_id} não encontrado")
                return None
            
            # Generate HTML content
            html_content = self._generate_html(contrato)
            print(f"HTML gerado: {len(html_content)} caracteres")
            
            # Generate PDF using Playwright
            async with async_playwright() as p:
                print("Iniciando Playwright...")
                browser = await p.chromium.launch(headless=True)
                print("Browser iniciado")
                page = await browser.new_page()
                print("Página criada")
                
                # Set content
                await page.set_content(html_content)
                print("Conteúdo definido")
                
                # Generate PDF
                pdf_bytes = await page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '20mm',
                        'right': '15mm',
                        'bottom': '20mm',
                        'left': '15mm'
                    }
                )
                print(f"PDF gerado: {len(pdf_bytes)} bytes")
                
                await browser.close()
                return pdf_bytes
                
        except Exception as e:
            print(f"ERRO ao gerar PDF: {e}")
            traceback.print_exc()
            return None
    
    def _generate_html(self, contrato: Contrato) -> str:
        """Generate HTML for contract."""
        # Format values
        def format_currency(value):
            return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        def format_cpf(cpf):
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        def format_date(date_str):
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%d/%m/%Y')
            except:
                return date_str
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contrato {contrato.numero}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 20mm 15mm;
                }}
                body {{
                    font-family: 'Times New Roman', Times, serif;
                    font-size: 11pt;
                    line-height: 1.4;
                    color: #000;
                    max-width: 210mm;
                    margin: 0 auto;
                }}
                .header {{
                    display: flex;
                    align-items: flex-start;
                    justify-content: space-between;
                    border-bottom: 2px solid #000;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .logo-section {{
                    display: flex;
                    align-items: flex-start;
                    gap: 15px;
                }}
                .logo {{
                    width: 70px;
                    height: 70px;
                    background: #627d98;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .company-info h1 {{
                    font-size: 16pt;
                    margin: 0 0 5px 0;
                    font-weight: bold;
                }}
                .company-info p {{
                    margin: 2px 0;
                    font-size: 9pt;
                }}
                .tel {{
                    font-size: 10pt;
                    font-weight: bold;
                }}
                .title-section {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .title-section h2 {{
                    font-size: 14pt;
                    border-bottom: 2px solid #000;
                    display: inline-block;
                    padding-bottom: 5px;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 10pt;
                    color: #333;
                    margin-top: 8px;
                }}
                .contract-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 10pt;
                }}
                .contract-info span {{
                    margin: 0 15px;
                }}
                .parties {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 15px;
                }}
                .party-box {{
                    border: 2px solid #000;
                    padding: 10px;
                }}
                .party-box h3 {{
                    font-size: 10pt;
                    margin: 0 0 8px 0;
                    border-bottom: 1px solid #999;
                    padding-bottom: 3px;
                }}
                .party-box p {{
                    margin: 2px 0;
                    font-size: 9pt;
                }}
                .intro {{
                    text-align: justify;
                    margin-bottom: 15px;
                    font-size: 10pt;
                }}
                .clauses {{
                    text-align: justify;
                }}
                .clauses p {{
                    margin: 8px 0;
                    text-align: justify;
                }}
                .clauses strong {{
                    text-transform: uppercase;
                    font-weight: bold;
                }}
                .clauses ul {{
                    margin: 5px 0;
                    padding-left: 25px;
                }}
                .clauses li {{
                    margin: 3px 0;
                }}
                .signatures {{
                    margin-top: 30px;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 50px;
                }}
                .signature {{
                    text-align: center;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    margin-top: 50px;
                    padding-top: 5px;
                }}
                .witnesses {{
                    margin-top: 20px;
                    font-size: 9pt;
                }}
                .witness-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-top: 10px;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #ccc;
                    text-align: center;
                    font-size: 8pt;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo-section">
                    <div class="logo">FC</div>
                    <div class="company-info">
                        <h1>FC SOLUÇÕES FINANCEIRAS</h1>
                        <p>CNPJ: 57.815.628/0001-62</p>
                        <p>Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3</p>
                        <p>Jardim Nova Aliança Sul - Ribeirão Preto/SP - CEP 14022-100</p>
                        <p>contato@fcsolucoesfinanceiras.com</p>
                    </div>
                </div>
                <div class="tel">Tel: (16) 99301-7396</div>
            </div>

            <div class="title-section">
                <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</h2>
                <div class="subtitle">Bacen - Remoção SCR</div>
            </div>

            <div class="contract-info">
                <span><strong>Nº:</strong> {contrato.numero}</span>
                <span><strong>Data:</strong> {contrato.data_assinatura or format_date(contrato.created_at.isoformat())}</span>
            </div>

            <div class="parties">
                <div class="party-box">
                    <h3>CONTRATANTE</h3>
                    <p><strong>Nome:</strong> {contrato.contratante_nome}</p>
                    <p><strong>CPF/CNPJ:</strong> {format_cpf(contrato.contratante_documento)}</p>
                    <p><strong>E-mail:</strong> {contrato.contratante_email}</p>
                    {f'<p><strong>Contato:</strong> {contrato.contratante_telefone}</p>' if contrato.contratante_telefone else ''}
                    <p><strong>Endereço:</strong> {contrato.contratante_endereco}</p>
                </div>
                <div class="party-box">
                    <h3>CONTRATADA</h3>
                    <p><strong>Razão Social:</strong> FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</p>
                    <p><strong>CNPJ:</strong> 57.815.628/0001-62</p>
                    <p><strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com</p>
                    <p><strong>Contato:</strong> (16) 99301-7396</p>
                    <p><strong>Endereço:</strong> Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100</p>
                </div>
            </div>

            <div class="intro">
                As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços, 
                que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.
            </div>

            <div class="clauses">
                <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO</strong><br>
                O presente contrato tem como objeto a prestação de serviços de consultoria e intermediação administrativa 
                pela CONTRATADA em favor do(a) CONTRATANTE, visando a adoção de procedimentos administrativos para a 
                regularização de apontamentos de prejuízo registrados no Sistema de Informações de Crédito (SCR) do 
                Banco Central do Brasil, vinculados ao CPF/CNPJ do(a) CONTRATANTE.</p>

                <p>O serviço consiste na análise do caso, elaboração de requerimentos e acompanhamento do processo 
                administrativo junto às instituições financeiras credoras, buscando a baixa dos referidos apontamentos, 
                nos termos da regulamentação vigente.</p>

                <p>Fica claro entre as partes que este serviço não se trata de quitação ou pagamento de dívidas, 
                mas sim de um procedimento administrativo para a regularização dos registros no SCR.</p>

                <p><strong>CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA</strong><br>
                A CONTRATADA se compromete a:</p>
                <ul>
                    <li>Realizar uma análise detalhada da situação do(a) CONTRATANTE junto ao SCR.</li>
                    <li>Elaborar e protocolar os requerimentos administrativos necessários junto às instituições financeiras pertinentes.</li>
                    <li>Acompanhar o andamento dos procedimentos, empregando seus melhores esforços técnicos para a obtenção do resultado almejado.</li>
                    <li>Manter o(a) CONTRATANTE informado sobre as etapas e o andamento do processo.</li>
                    <li>Prestar o serviço dentro do mais alto padrão de ética e profissionalismo.</li>
                </ul>

                <p><strong>CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES DO(A) CONTRATANTE</strong><br>
                <strong>3.1.</strong> O(A) CONTRATANTE se compromete a:</p>
                <ul>
                    <li>Fornecer à CONTRATADA todos os documentos e informações solicitados, de forma completa e verdadeira, para a correta execução dos serviços.</li>
                    <li>Efetuar o pagamento dos honorários nas datas e valores acordados neste instrumento.</li>
                    <li>Não tratar diretamente com as instituições financeiras sobre o objeto deste contrato sem o prévio conhecimento e anuência da CONTRATADA.</li>
                </ul>

                <p><strong>CLÁUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO</strong><br>
                <strong>4.1.</strong> Pelos serviços prestados, o(a) CONTRATANTE pagará à CONTRATADA o valor total de 
                <strong>{format_currency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), a ser pago da seguinte forma:</p>
                <ul>
                    <li><strong>Entrada:</strong> {format_currency(contrato.valor_entrada)} ({contrato.valor_entrada_extenso}), a ser paga no ato da assinatura deste contrato.</li>
                    {f"<li><strong>Parcelas:</strong> {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de {format_currency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso}), com vencimento em {contrato.prazo_1} ({contrato.prazo_1_extenso}) e {contrato.prazo_2} ({contrato.prazo_2_extenso}) dias, respectivamente, a contar da data de assinatura.</li>" if contrato.qtd_parcelas > 0 else ''}
                </ul>

                <p><strong>CLÁUSULA QUINTA - DO PRAZO DE EXECUÇÃO</strong><br>
                O prazo estimado para a conclusão dos serviços é de 45 (quarenta e cinco) a 60 (sessenta) dias úteis, 
                contados a partir da data de assinatura deste instrumento e da confirmação do pagamento da entrada.</p>

                <p><strong>CLÁUSULA SEXTA - DA GARANTIA DE RESULTADO E POLÍTICA DE REEMBOLSO</strong><br>
                O serviço objeto deste contrato é de resultado, vinculado à efetiva baixa e atualização dos apontamentos 
                de prejuízo no Sistema de Informações de Crédito (SCR) do Banco Central, conforme o escopo definido na Cláusula Primeira.</p>

                <p>Caso a CONTRATADA não comprove a conclusão do serviço no prazo máximo de 60 (sessenta) dias úteis, 
                o presente contrato será considerado automaticamente rescindido por inadimplemento da CONTRATADA.</p>

                <p>Na hipótese de rescisão por descumprimento do prazo, a CONTRATADA deverá realizar a devolução integral 
                dos valores já pagos pelo(a) CONTRATANTE, no prazo de até 30 (trinta) dias úteis após o término do prazo contratual.</p>

                <p><strong>CLÁUSULA SÉTIMA - DO INADIMPLEMENTO DO(A) CONTRATANTE</strong><br>
                Em caso de atraso no pagamento de qualquer parcela, o valor devido será acrescido de:</p>
                <ul>
                    <li>Multa de 10% (dez por cento) sobre o valor da parcela em atraso;</li>
                    <li>Juros de mora de 1% (um por cento) ao mês, calculados pro rata die;</li>
                    <li>Correção monetária pelo índice IPCA/IBGE, ou outro que venha a substituí-lo.</li>
                </ul>

                <p>O atraso superior a 30 (trinta) dias no pagamento de qualquer parcela poderá ensejar a suspensão dos 
                serviços e, a critério da CONTRATADA, a rescisão do presente contrato.</p>

                <p><strong>CLÁUSULA OITAVA - DA ALOCAÇÃO DE RECURSOS E DA IRREVERSIBILIDADE DOS CUSTOS</strong><br>
                O(A) CONTRATANTE declara estar ciente de que o processo de contratação foi dividido em duas fases distintas: 
                (I) a fase de análise e onboarding, de caráter gratuito e sem compromisso; e (II) a fase de execução do serviço.</p>

                <p>Ao assinar este contrato, o(A) CONTRATANTE autoriza e a CONTRATADA se compromete a alocar, de forma 
                imediata e irreversível, os recursos humanos e materiais necessários para o protocolo e acompanhamento 
                do procedimento administrativo.</p>

                <p><strong>CLÁUSULA NONA - DA CONFIDENCIALIDADE</strong><br>
                As partes se comprometem a manter em sigilo todas as informações e documentos a que tiverem acesso em 
                decorrência deste contrato, não podendo divulgá-los a terceiros sem a prévia autorização da outra parte.</p>

                <p><strong>CLÁUSULA DÉCIMA - DO FORO</strong><br>
                Para dirimir quaisquer controvérsias oriundas do CONTRATO, as partes elegem o foro da Comarca de São Paulo/SP.</p>

                <p>E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias de igual teor e forma.</p>

                <p><strong>{contrato.local_assinatura or 'Ribeirão Preto/SP'}, {contrato.data_assinatura or format_date(contrato.created_at.isoformat())}.</strong></p>
            </div>

            <div class="signatures">
                <div class="signature">
                    <div class="signature-line">
                        <strong>{contrato.contratante_nome}</strong><br>
                        CPF: {format_cpf(contrato.contratante_documento)}<br>
                        <strong>CONTRATANTE</strong>
                    </div>
                </div>
                <div class="signature">
                    <div class="signature-line">
                        <strong>FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</strong><br>
                        CNPJ: 57.815.628/0001-62<br>
                        <strong>CONTRATADA</strong>
                    </div>
                </div>
            </div>

            <div class="witnesses">
                <strong>Testemunhas:</strong>
                <div class="witness-grid">
                    <div>
                        1. _______________________________________<br>
                        Nome:<br>
                        CPF:
                    </div>
                    <div>
                        2. _______________________________________<br>
                        Nome:<br>
                        CPF:
                    </div>
                </div>
            </div>

            <div class="footer">
                FC Soluções Financeiras - CNPJ: 57.815.628/0001-62<br>
                Documento gerado em {datetime.now().strftime('%d/%m/%Y')}
            </div>
        </body>
        </html>
        """
        return html

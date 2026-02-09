"""PDF Service using Playwright."""
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contrato import Contrato


class PDFService:
    """PDF generation service using Playwright."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _load_logo_data_uri() -> Optional[str]:
        possible_paths = [
            Path("C:/projetos/fabio2/contratos/logo2.png"),
            Path(__file__).resolve().parents[3] / "contratos" / "logo2.png",
            Path(__file__).resolve().parents[2] / "contratos" / "logo2.png",
            Path("C:/projetos/fabio2/contratos/logo2.jpeg"),
        ]
        for logo_path in possible_paths:
            try:
                if logo_path.exists():
                    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
                    mime = "image/png" if logo_path.suffix.lower() == ".png" else "image/jpeg"
                    return f"data:{mime};base64,{encoded}"
            except OSError:
                continue
        return None

    async def generate_contrato_pdf(self, contrato_id: UUID) -> Optional[bytes]:
        """Generate PDF for a contract using Playwright."""
        import traceback

        try:
            result = await self.db.execute(select(Contrato).where(Contrato.id == contrato_id))
            contrato = result.scalar_one_or_none()

            if not contrato:
                print(f"Contrato {contrato_id} não encontrado")
                return None

            html_content = self._generate_html(contrato)
            print(f"HTML gerado: {len(html_content)} caracteres")

            async with async_playwright() as p:
                print("Iniciando Playwright...")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.set_content(html_content)

                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "20mm",
                        "right": "15mm",
                        "bottom": "20mm",
                        "left": "15mm",
                    },
                )
                print(f"PDF gerado: {len(pdf_bytes)} bytes")

                await browser.close()
                return pdf_bytes

        except Exception as e:
            print(f"ERRO ao gerar PDF: {e}")
            traceback.print_exc()
            return None

    def _generate_html(self, contrato: Contrato) -> str:
        """Generate contract HTML."""

        def format_currency(value: float) -> str:
            return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def format_document(documento: str) -> str:
            clean = "".join(ch for ch in str(documento or "") if ch.isdigit())
            if len(clean) == 11:
                return f"{clean[:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:]}"
            if len(clean) == 14:
                return f"{clean[:2]}.{clean[2:5]}.{clean[5:8]}/{clean[8:12]}-{clean[12:]}"
            return str(documento or "")

        def format_date(date_str: str) -> str:
            try:
                dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
                return dt.strftime("%d/%m/%Y")
            except Exception:
                return str(date_str)

        def normalize_mojibake_text(value: Optional[str], fallback: str) -> str:
            text = str(value or "").strip()
            if not text:
                return fallback
            if "Ã" in text or "Â" in text:
                try:
                    return text.encode("latin-1").decode("utf-8")
                except UnicodeError:
                    return text
            return text

        template_id = str(contrato.template_id or "").lower()
        is_cadin = template_id == "cadin"
        subtitle = "CADIN - Regularização de pendências federais" if is_cadin else "Bacen - Remoção SCR"
        logo_data_uri = self._load_logo_data_uri()
        logo_html = (
            f'<img src="{logo_data_uri}" alt="FC Soluções Financeiras" />'
            if logo_data_uri
            else '<span style="font-size:20px;font-weight:700">FC</span>'
        )

        parcelas_bacen = (
            f"<li><strong>Parcelas:</strong> {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de {format_currency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso}), com vencimento em {contrato.prazo_1} ({contrato.prazo_1_extenso}) e {contrato.prazo_2} ({contrato.prazo_2_extenso}) dias, respectivamente, a contar da data de assinatura.</li>"
            if contrato.qtd_parcelas > 0
            else ""
        )

        parcelas_cadin = (
            f" e o saldo em {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de {format_currency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso})."
            if contrato.qtd_parcelas > 0
            else " com pagamento integral na assinatura."
        )

        bacen_clauses_html = f"""
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
                    {parcelas_bacen}
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

                <p>Ao assinar este contrato, o(a) CONTRATANTE autoriza e a CONTRATADA se compromete a alocar, de forma
                imediata e irreversível, os recursos humanos e materiais necessários para o protocolo e acompanhamento
                do procedimento administrativo.</p>

                <p><strong>CLÁUSULA NONA - DA CONFIDENCIALIDADE</strong><br>
                As partes se comprometem a manter em sigilo todas as informações e documentos a que tiverem acesso em
                decorrência deste contrato, não podendo divulgá-los a terceiros sem a prévia autorização da outra parte.</p>

                <p><strong>CLÁUSULA DÉCIMA - DO FORO</strong><br>
                Para dirimir quaisquer controvérsias oriundas do contrato, as partes elegem o foro da Comarca de São Paulo/SP.</p>
        """

        cadin_clauses_html = f"""
                <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO</strong><br>
                <strong>1.1.</strong> O presente instrumento tem por objeto a prestação de serviços de assessoria administrativa para a regularização de pendências do(a) CONTRATANTE junto ao Cadastro Informativo de Créditos não Quitados do Setor Público Federal (CADIN), visando à adoção dos procedimentos necessários para obtenção da Certidão Negativa de Débitos (CND) ou documento equivalente, referente às dívidas federais constatadas até a data de assinatura deste contrato.</p>

                <p><strong>§1º.</strong> O serviço inclui análise dos débitos, negociação junto aos órgãos credores para obtenção de descontos e formalização de parcelamentos, conforme as condições e programas de anistia disponibilizados pelo governo.</p>

                <p><strong>§2º.</strong> Fica expressamente claro que a CONTRATADA não se responsabiliza pela quitação das dívidas do(a) CONTRATANTE, mas sim pela prestação de serviços de assessoria para negociação e regularização dos apontamentos no CADIN.</p>

                <p><strong>§3º.</strong> Débitos que surgirem ou forem inscritos no CADIN após a data de assinatura deste contrato não estarão cobertos por este instrumento.</p>

                <p><strong>1.2.</strong> Os serviços contratados não representam garantia de aprovação de crédito para o(a) CONTRATANTE, mas um meio para regularização da situação fiscal perante os órgãos federais.</p>

                <p><strong>CLÁUSULA SEGUNDA - DAS DESPESAS E HONORÁRIOS</strong><br>
                <strong>2.1.</strong> Como contraprestação pelos serviços descritos na Cláusula 1ª, o(a) CONTRATANTE pagará à CONTRATADA o valor total de <strong>{format_currency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), sendo entrada de <strong>{format_currency(contrato.valor_entrada)}</strong> ({contrato.valor_entrada_extenso}){parcelas_cadin}</p>

                <p><strong>2.2.</strong> Em caso de atraso superior a 30 (trinta) dias no pagamento de qualquer parcela, o serviço será suspenso. Persistindo a inadimplência, o(a) CONTRATANTE perderá o direito à continuidade do serviço e aos valores já pagos, e as demais parcelas em aberto poderão ser protestadas.</p>

                <p><strong>2.3.</strong> No caso de solicitação de cancelamento pelo(a) CONTRATANTE, será cobrada multa de 30% (trinta por cento) sobre o valor total das parcelas em aberto.</p>

                <p><strong>2.4.</strong> A execução dos serviços terá início imediato após a assinatura deste contrato e confirmação do pagamento da primeira parcela ou do valor integral, conforme modalidade escolhida.</p>

                <p><strong>2.5.</strong> Havendo parcelamento, o não pagamento de qualquer parcela acarretará acréscimo de juros de 2% (dois por cento) ao mês, multa de 10% (dez por cento) e correção monetária.</p>

                <p><strong>2.6.</strong> O não pagamento de uma parcela acarreta vencimento antecipado das vincendas, podendo a CONTRATADA promover cobrança e protesto dos títulos em aberto perante o foro da comarca de Ribeirão Preto/SP.</p>

                <p><strong>2.7.</strong> A rescisão do presente contrato, solicitada pela CONTRATANTE após o início da prestação dos serviços, implica multa compensatória de 30% (trinta por cento) do valor acordado, sem direito a ressarcimento dos valores já pagos.</p>

                <p><strong>CLÁUSULA TERCEIRA - DO PRAZO E GARANTIA</strong><br>
                <strong>3.1.</strong> A CONTRATADA realizará os procedimentos de regularização no prazo de até 45 (quarenta e cinco) dias úteis, contados da data de confirmação do pagamento e assinatura deste contrato. Este prazo poderá ser prorrogado em função da complexidade dos débitos ou de prazos dos órgãos públicos.</p>

                <p><strong>§1º - GARANTIA DE RESULTADO:</strong> caso o serviço não seja executado no prazo estabelecido, a CONTRATADA garantirá a devolução integral do valor pago no prazo de até 30 (trinta) dias úteis após o término do prazo estipulado.</p>

                <p><strong>3.2.</strong> A CONTRATADA oferece garantia de acompanhamento pelo período de 1 (um) ano contado da data de efetiva regularização dos apontamentos. Durante este período, caso os apontamentos referentes às dívidas tratadas neste contrato retornem ao CADIN, a CONTRATADA realizará novamente o processo sem custo adicional.</p>

                <p><strong>§2º - ABRANGÊNCIA DA GARANTIA:</strong> a garantia aplica-se exclusivamente às dívidas e restrições identificadas e tratadas no âmbito deste contrato. Dívidas ou restrições que surgirem após a assinatura deste instrumento não estão cobertas.</p>

                <p><strong>CLÁUSULA QUARTA - DA PROTEÇÃO DE DADOS (LGPD)</strong><br>
                <strong>4.1.</strong> Em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), a CONTRATADA tratará os dados pessoais do(a) CONTRATANTE com a finalidade exclusiva de executar este contrato, nos termos do art. 7º, incisos II, V e X.</p>

                <p><strong>§1º.</strong> A CONTRATADA adota medidas de segurança para proteger os dados e os eliminará após o término do serviço, ressalvadas as obrigações legais de guarda.</p>

                <p><strong>§2º.</strong> O(A) CONTRATANTE pode exercer seus direitos de titular (acesso, correção, eliminação etc.) a qualquer momento pelo e-mail: contato@fcsolucoesfinanceiras.com.</p>

                <p><strong>CLÁUSULA QUINTA - DO FORO</strong><br>
                <strong>5.1.</strong> Para dirimir quaisquer controvérsias oriundas deste contrato, as partes elegem o foro da comarca de Ribeirão Preto/SP, ressalvada a faculdade do(a) CONTRATANTE de propor ação no foro de seu domicílio, conforme o Código de Defesa do Consumidor.</p>
        """

        clauses_html = cadin_clauses_html if is_cadin else bacen_clauses_html
        contrato_data = contrato.data_assinatura or format_date(contrato.created_at.isoformat())
        local_assinatura = normalize_mojibake_text(
            contrato.local_assinatura, "Ribeirão Preto/SP"
        )

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
                    font-size: 12pt;
                    line-height: 1.4;
                    color: #000;
                    max-width: 210mm;
                    margin: 0 auto;
                }}
                .header-band {{
                    background: #1e3a5f;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    gap: 14px;
                    padding: 10px 14px;
                    margin-bottom: 18px;
                }}
                .header-band .logo {{
                    width: 88px;
                    height: 88px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                .header-band .logo img {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    display: block;
                }}
                .header-band h1 {{
                    margin: 0;
                    font-size: 22pt;
                    letter-spacing: 0.2px;
                    font-weight: 700;
                    color: #fff;
                }}
                .title-section {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .title-section h2 {{
                    font-size: 16pt;
                    border-bottom: 2px solid #000;
                    display: inline-block;
                    padding-bottom: 5px;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 11pt;
                    color: #333;
                    margin-top: 8px;
                }}
                .contract-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 11pt;
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
                    font-size: 11pt;
                    margin: 0 0 8px 0;
                    border-bottom: 1px solid #999;
                    padding-bottom: 3px;
                }}
                .party-box p {{
                    margin: 2px 0;
                    font-size: 10pt;
                }}
                .intro {{
                    text-align: justify;
                    margin-bottom: 15px;
                    font-size: 11pt;
                }}
                .clauses {{
                    text-align: justify;
                }}
                .clauses p {{
                    margin: 8px 0;
                    text-align: justify;
                }}
                .clauses strong {{
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
            <div class="header-band">
                <div class="logo">{logo_html}</div>
                <h1>F C Soluções Financeiras</h1>
            </div>

            <div class="title-section">
                <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</h2>
                <div class="subtitle">{subtitle}</div>
            </div>

            <div class="contract-info">
                <span><strong>Nº:</strong> {contrato.numero}</span>
                <span><strong>Data:</strong> {contrato_data}</span>
            </div>

            <div class="parties">
                <div class="party-box">
                    <h3>CONTRATANTE</h3>
                    <p><strong>Nome:</strong> {contrato.contratante_nome}</p>
                    <p><strong>CPF/CNPJ:</strong> {format_document(contrato.contratante_documento)}</p>
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
                {clauses_html}

                <p>E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias de igual teor e forma.</p>
                <p><strong>{local_assinatura}, {contrato_data}.</strong></p>
            </div>

            <div class="signatures">
                <div class="signature">
                    <div class="signature-line">
                        <strong>{contrato.contratante_nome}</strong><br>
                        CPF/CNPJ: {format_document(contrato.contratante_documento)}<br>
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

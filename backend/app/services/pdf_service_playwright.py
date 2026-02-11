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
                print(f"Contrato {contrato_id} nÃ£o encontrado")
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
            if "Ãƒ" in text or "Ã‚" in text:
                try:
                    return text.encode("latin-1").decode("utf-8")
                except UnicodeError:
                    return text
            return text

        template_id = str(contrato.template_id or "").lower()
        is_cadin = template_id == "cadin"
        is_cnh = template_id == "cnh"
        subtitle = "CADIN - Regularizacao de pendencias federais" if is_cadin else ("CNH - Cassacao/Suspensao e Recurso de Multas" if is_cnh else "Bacen - Remocao SCR")
        logo_data_uri = self._load_logo_data_uri()
        logo_html = (
            f'<img src="{logo_data_uri}" alt="FC SoluÃ§Ãµes Financeiras" />'
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
                <p><strong>CLÃUSULA PRIMEIRA - DO OBJETO</strong><br>
                O presente contrato tem como objeto a prestaÃ§Ã£o de serviÃ§os de consultoria e intermediaÃ§Ã£o administrativa
                pela CONTRATADA em favor do(a) CONTRATANTE, visando a adoÃ§Ã£o de procedimentos administrativos para a
                regularizaÃ§Ã£o de apontamentos de prejuÃ­zo registrados no Sistema de InformaÃ§Ãµes de CrÃ©dito (SCR) do
                Banco Central do Brasil, vinculados ao CPF/CNPJ do(a) CONTRATANTE.</p>

                <p>O serviÃ§o consiste na anÃ¡lise do caso, elaboraÃ§Ã£o de requerimentos e acompanhamento do processo
                administrativo junto Ã s instituiÃ§Ãµes financeiras credoras, buscando a baixa dos referidos apontamentos,
                nos termos da regulamentaÃ§Ã£o vigente.</p>

                <p>Fica claro entre as partes que este serviÃ§o nÃ£o se trata de quitaÃ§Ã£o ou pagamento de dÃ­vidas,
                mas sim de um procedimento administrativo para a regularizaÃ§Ã£o dos registros no SCR.</p>

                <p><strong>CLÃUSULA SEGUNDA - DAS OBRIGAÃ‡Ã•ES DA CONTRATADA</strong><br>
                A CONTRATADA se compromete a:</p>
                <ul>
                    <li>Realizar uma anÃ¡lise detalhada da situaÃ§Ã£o do(a) CONTRATANTE junto ao SCR.</li>
                    <li>Elaborar e protocolar os requerimentos administrativos necessÃ¡rios junto Ã s instituiÃ§Ãµes financeiras pertinentes.</li>
                    <li>Acompanhar o andamento dos procedimentos, empregando seus melhores esforÃ§os tÃ©cnicos para a obtenÃ§Ã£o do resultado almejado.</li>
                    <li>Manter o(a) CONTRATANTE informado sobre as etapas e o andamento do processo.</li>
                    <li>Prestar o serviÃ§o dentro do mais alto padrÃ£o de Ã©tica e profissionalismo.</li>
                </ul>

                <p><strong>CLÃUSULA TERCEIRA - DAS OBRIGAÃ‡Ã•ES DO(A) CONTRATANTE</strong><br>
                <strong>3.1.</strong> O(A) CONTRATANTE se compromete a:</p>
                <ul>
                    <li>Fornecer Ã  CONTRATADA todos os documentos e informaÃ§Ãµes solicitados, de forma completa e verdadeira, para a correta execuÃ§Ã£o dos serviÃ§os.</li>
                    <li>Efetuar o pagamento dos honorÃ¡rios nas datas e valores acordados neste instrumento.</li>
                    <li>NÃ£o tratar diretamente com as instituiÃ§Ãµes financeiras sobre o objeto deste contrato sem o prÃ©vio conhecimento e anuÃªncia da CONTRATADA.</li>
                </ul>

                <p><strong>CLÃUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO</strong><br>
                <strong>4.1.</strong> Pelos serviÃ§os prestados, o(a) CONTRATANTE pagarÃ¡ Ã  CONTRATADA o valor total de
                <strong>{format_currency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), a ser pago da seguinte forma:</p>
                <ul>
                    <li><strong>Entrada:</strong> {format_currency(contrato.valor_entrada)} ({contrato.valor_entrada_extenso}), a ser paga no ato da assinatura deste contrato.</li>
                    {parcelas_bacen}
                </ul>

                <p><strong>CLÃUSULA QUINTA - DO PRAZO DE EXECUÃ‡ÃƒO</strong><br>
                O prazo estimado para a conclusÃ£o dos serviÃ§os Ã© de 45 (quarenta e cinco) a 60 (sessenta) dias Ãºteis,
                contados a partir da data de assinatura deste instrumento e da confirmaÃ§Ã£o do pagamento da entrada.</p>

                <p><strong>CLÃUSULA SEXTA - DA GARANTIA DE RESULTADO E POLÃTICA DE REEMBOLSO</strong><br>
                O serviÃ§o objeto deste contrato Ã© de resultado, vinculado Ã  efetiva baixa e atualizaÃ§Ã£o dos apontamentos
                de prejuÃ­zo no Sistema de InformaÃ§Ãµes de CrÃ©dito (SCR) do Banco Central, conforme o escopo definido na ClÃ¡usula Primeira.</p>

                <p>Caso a CONTRATADA nÃ£o comprove a conclusÃ£o do serviÃ§o no prazo mÃ¡ximo de 60 (sessenta) dias Ãºteis,
                o presente contrato serÃ¡ considerado automaticamente rescindido por inadimplemento da CONTRATADA.</p>

                <p>Na hipÃ³tese de rescisÃ£o por descumprimento do prazo, a CONTRATADA deverÃ¡ realizar a devoluÃ§Ã£o integral
                dos valores jÃ¡ pagos pelo(a) CONTRATANTE, no prazo de atÃ© 30 (trinta) dias Ãºteis apÃ³s o tÃ©rmino do prazo contratual.</p>

                <p><strong>CLÃUSULA SÃ‰TIMA - DO INADIMPLEMENTO DO(A) CONTRATANTE</strong><br>
                Em caso de atraso no pagamento de qualquer parcela, o valor devido serÃ¡ acrescido de:</p>
                <ul>
                    <li>Multa de 10% (dez por cento) sobre o valor da parcela em atraso;</li>
                    <li>Juros de mora de 1% (um por cento) ao mÃªs, calculados pro rata die;</li>
                    <li>CorreÃ§Ã£o monetÃ¡ria pelo Ã­ndice IPCA/IBGE, ou outro que venha a substituÃ­-lo.</li>
                </ul>

                <p>O atraso superior a 30 (trinta) dias no pagamento de qualquer parcela poderÃ¡ ensejar a suspensÃ£o dos
                serviÃ§os e, a critÃ©rio da CONTRATADA, a rescisÃ£o do presente contrato.</p>

                <p><strong>CLÃUSULA OITAVA - DA ALOCAÃ‡ÃƒO DE RECURSOS E DA IRREVERSIBILIDADE DOS CUSTOS</strong><br>
                O(A) CONTRATANTE declara estar ciente de que o processo de contrataÃ§Ã£o foi dividido em duas fases distintas:
                (I) a fase de anÃ¡lise e onboarding, de carÃ¡ter gratuito e sem compromisso; e (II) a fase de execuÃ§Ã£o do serviÃ§o.</p>

                <p>Ao assinar este contrato, o(a) CONTRATANTE autoriza e a CONTRATADA se compromete a alocar, de forma
                imediata e irreversÃ­vel, os recursos humanos e materiais necessÃ¡rios para o protocolo e acompanhamento
                do procedimento administrativo.</p>

                <p><strong>CLÃUSULA NONA - DA CONFIDENCIALIDADE</strong><br>
                As partes se comprometem a manter em sigilo todas as informaÃ§Ãµes e documentos a que tiverem acesso em
                decorrÃªncia deste contrato, nÃ£o podendo divulgÃ¡-los a terceiros sem a prÃ©via autorizaÃ§Ã£o da outra parte.</p>

                <p><strong>CLÃUSULA DÃ‰CIMA - DO FORO</strong><br>
                Para dirimir quaisquer controvÃ©rsias oriundas do contrato, as partes elegem o foro da Comarca de SÃ£o Paulo/SP.</p>
        """

        cadin_clauses_html = f"""
                <p><strong>CLÃUSULA PRIMEIRA - DO OBJETO</strong><br>
                <strong>1.1.</strong> O presente instrumento tem por objeto a prestaÃ§Ã£o de serviÃ§os de assessoria administrativa para a regularizaÃ§Ã£o de pendÃªncias do(a) CONTRATANTE junto ao Cadastro Informativo de CrÃ©ditos nÃ£o Quitados do Setor PÃºblico Federal (CADIN), visando Ã  adoÃ§Ã£o dos procedimentos necessÃ¡rios para obtenÃ§Ã£o da CertidÃ£o Negativa de DÃ©bitos (CND) ou documento equivalente, referente Ã s dÃ­vidas federais constatadas atÃ© a data de assinatura deste contrato.</p>

                <p><strong>Â§1Âº.</strong> O serviÃ§o inclui anÃ¡lise dos dÃ©bitos, negociaÃ§Ã£o junto aos Ã³rgÃ£os credores para obtenÃ§Ã£o de descontos e formalizaÃ§Ã£o de parcelamentos, conforme as condiÃ§Ãµes e programas de anistia disponibilizados pelo governo.</p>

                <p><strong>Â§2Âº.</strong> Fica expressamente claro que a CONTRATADA nÃ£o se responsabiliza pela quitaÃ§Ã£o das dÃ­vidas do(a) CONTRATANTE, mas sim pela prestaÃ§Ã£o de serviÃ§os de assessoria para negociaÃ§Ã£o e regularizaÃ§Ã£o dos apontamentos no CADIN.</p>

                <p><strong>Â§3Âº.</strong> DÃ©bitos que surgirem ou forem inscritos no CADIN apÃ³s a data de assinatura deste contrato nÃ£o estarÃ£o cobertos por este instrumento.</p>

                <p><strong>1.2.</strong> Os serviÃ§os contratados nÃ£o representam garantia de aprovaÃ§Ã£o de crÃ©dito para o(a) CONTRATANTE, mas um meio para regularizaÃ§Ã£o da situaÃ§Ã£o fiscal perante os Ã³rgÃ£os federais.</p>

                <p><strong>CLÃUSULA SEGUNDA - DAS DESPESAS E HONORÃRIOS</strong><br>
                <strong>2.1.</strong> Como contraprestaÃ§Ã£o pelos serviÃ§os descritos na ClÃ¡usula 1Âª, o(a) CONTRATANTE pagarÃ¡ Ã  CONTRATADA o valor total de <strong>{format_currency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), sendo entrada de <strong>{format_currency(contrato.valor_entrada)}</strong> ({contrato.valor_entrada_extenso}){parcelas_cadin}</p>

                <p><strong>2.2.</strong> Em caso de atraso superior a 30 (trinta) dias no pagamento de qualquer parcela, o serviÃ§o serÃ¡ suspenso. Persistindo a inadimplÃªncia, o(a) CONTRATANTE perderÃ¡ o direito Ã  continuidade do serviÃ§o e aos valores jÃ¡ pagos, e as demais parcelas em aberto poderÃ£o ser protestadas.</p>

                <p><strong>2.3.</strong> No caso de solicitaÃ§Ã£o de cancelamento pelo(a) CONTRATANTE, serÃ¡ cobrada multa de 30% (trinta por cento) sobre o valor total das parcelas em aberto.</p>

                <p><strong>2.4.</strong> A execuÃ§Ã£o dos serviÃ§os terÃ¡ inÃ­cio imediato apÃ³s a assinatura deste contrato e confirmaÃ§Ã£o do pagamento da primeira parcela ou do valor integral, conforme modalidade escolhida.</p>

                <p><strong>2.5.</strong> Havendo parcelamento, o nÃ£o pagamento de qualquer parcela acarretarÃ¡ acrÃ©scimo de juros de 2% (dois por cento) ao mÃªs, multa de 10% (dez por cento) e correÃ§Ã£o monetÃ¡ria.</p>

                <p><strong>2.6.</strong> O nÃ£o pagamento de uma parcela acarreta vencimento antecipado das vincendas, podendo a CONTRATADA promover cobranÃ§a e protesto dos tÃ­tulos em aberto perante o foro da comarca de RibeirÃ£o Preto/SP.</p>

                <p><strong>2.7.</strong> A rescisÃ£o do presente contrato, solicitada pela CONTRATANTE apÃ³s o inÃ­cio da prestaÃ§Ã£o dos serviÃ§os, implica multa compensatÃ³ria de 30% (trinta por cento) do valor acordado, sem direito a ressarcimento dos valores jÃ¡ pagos.</p>

                <p><strong>CLÃUSULA TERCEIRA - DO PRAZO E GARANTIA</strong><br>
                <strong>3.1.</strong> A CONTRATADA realizarÃ¡ os procedimentos de regularizaÃ§Ã£o no prazo de atÃ© 45 (quarenta e cinco) dias Ãºteis, contados da data de confirmaÃ§Ã£o do pagamento e assinatura deste contrato. Este prazo poderÃ¡ ser prorrogado em funÃ§Ã£o da complexidade dos dÃ©bitos ou de prazos dos Ã³rgÃ£os pÃºblicos.</p>

                <p><strong>Â§1Âº - GARANTIA DE RESULTADO:</strong> caso o serviÃ§o nÃ£o seja executado no prazo estabelecido, a CONTRATADA garantirÃ¡ a devoluÃ§Ã£o integral do valor pago no prazo de atÃ© 30 (trinta) dias Ãºteis apÃ³s o tÃ©rmino do prazo estipulado.</p>

                <p><strong>3.2.</strong> A CONTRATADA oferece garantia de acompanhamento pelo perÃ­odo de 1 (um) ano contado da data de efetiva regularizaÃ§Ã£o dos apontamentos. Durante este perÃ­odo, caso os apontamentos referentes Ã s dÃ­vidas tratadas neste contrato retornem ao CADIN, a CONTRATADA realizarÃ¡ novamente o processo sem custo adicional.</p>

                <p><strong>Â§2Âº - ABRANGÃŠNCIA DA GARANTIA:</strong> a garantia aplica-se exclusivamente Ã s dÃ­vidas e restriÃ§Ãµes identificadas e tratadas no Ã¢mbito deste contrato. DÃ­vidas ou restriÃ§Ãµes que surgirem apÃ³s a assinatura deste instrumento nÃ£o estÃ£o cobertas.</p>

                <p><strong>CLÃUSULA QUARTA - DA PROTEÃ‡ÃƒO DE DADOS (LGPD)</strong><br>
                <strong>4.1.</strong> Em conformidade com a Lei Geral de ProteÃ§Ã£o de Dados (Lei nÂº 13.709/2018), a CONTRATADA tratarÃ¡ os dados pessoais do(a) CONTRATANTE com a finalidade exclusiva de executar este contrato, nos termos do art. 7Âº, incisos II, V e X.</p>

                <p><strong>Â§1Âº.</strong> A CONTRATADA adota medidas de seguranÃ§a para proteger os dados e os eliminarÃ¡ apÃ³s o tÃ©rmino do serviÃ§o, ressalvadas as obrigaÃ§Ãµes legais de guarda.</p>

                <p><strong>Â§2Âº.</strong> O(A) CONTRATANTE pode exercer seus direitos de titular (acesso, correÃ§Ã£o, eliminaÃ§Ã£o etc.) a qualquer momento pelo e-mail: contato@fcsolucoesfinanceiras.com.</p>

                <p><strong>CLÃUSULA QUINTA - DO FORO</strong><br>
                <strong>5.1.</strong> Para dirimir quaisquer controvÃ©rsias oriundas deste contrato, as partes elegem o foro da comarca de RibeirÃ£o Preto/SP, ressalvada a faculdade do(a) CONTRATANTE de propor aÃ§Ã£o no foro de seu domicÃ­lio, conforme o CÃ³digo de Defesa do Consumidor.</p>
        """

        cnh_clauses_html = f"""
                <p><strong>CLAUSULA PRIMEIRA - DO OBJETO</strong><br>
                Prestacao de servicos de assessoria tecnica para defesa administrativa e judicial contra suspensao/cassacao de CNH e multas de transito.</p>

                <p><strong>CLAUSULA SEGUNDA - OBRIGACOES DA CONTRATADA</strong><br>
                Analise tecnica, elaboracao/protocolo de recursos e acompanhamento processual ate decisao final.</p>

                <p><strong>CLAUSULA TERCEIRA - OBRIGACOES DO(A) CONTRATANTE</strong><br>
                Fornecer documentacao veridica, efetuar pagamentos nas datas pactuadas e comparecer a diligencias quando convocado(a).</p>

                <p><strong>CLAUSULA QUARTA - VALOR E FORMA DE PAGAMENTO</strong><br>
                Valor total de <strong>{format_currency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), com entrada de
                <strong>{format_currency(contrato.valor_entrada)}</strong> ({contrato.valor_entrada_extenso}){" e saldo em " + str(contrato.qtd_parcelas) + " parcelas." if contrato.qtd_parcelas > 0 else " com pagamento integral na assinatura."}</p>

                <p><strong>CLAUSULA QUINTA - PRAZO DE EXECUCAO</strong><br>
                Protocolo das medidas administrativas em ate 15 dias uteis apos assinatura, pagamento e entrega da documentacao completa.</p>

                <p><strong>CLAUSULA SEXTA - GARANTIA DE ENTREGA</strong><br>
                Se houver atraso por culpa da CONTRATADA no protocolo do servico, devolucao integral em ate 10 dias uteis, sem garantia de deferimento de merito.</p>

                <p><strong>CLAUSULA SETIMA - INADIMPLEMENTO</strong><br>
                Em atraso: multa de 20%, juros de 1% ao mes pro rata die e correcao pelo IPCA/IBGE. Atraso superior a 30 dias suspende os servicos.</p>

                <p><strong>CLAUSULA OITAVA - RESCISAO</strong><br>
                Rescisao apos inicio dos servicos implica multa de 20% do valor total, salvo inadimplemento da CONTRATADA.</p>

                <p><strong>CLAUSULA NONA - LGPD E CONFIDENCIALIDADE</strong><br>
                Tratamento de dados para execucao do contrato, conforme Lei 13.709/2018, com dever de sigilo entre as partes.</p>

                <p><strong>CLAUSULA DECIMA - DO FORO</strong><br>
                Foro da comarca de Ribeirao Preto/SP, ressalvado o foro do domicilio do(a) CONTRATANTE conforme CDC.</p>
        """

        clauses_html = (
            cadin_clauses_html
            if is_cadin
            else cnh_clauses_html
            if is_cnh
            else bacen_clauses_html
        )
        contrato_data = contrato.data_assinatura or format_date(contrato.created_at.isoformat())
        local_assinatura = normalize_mojibake_text(
            contrato.local_assinatura, "RibeirÃ£o Preto/SP"
        )
        dados_extras = contrato.dados_extras if isinstance(contrato.dados_extras, dict) else {}
        cnh_numero = str(dados_extras.get("cnh_numero") or "").strip()

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
                <h1>F C SoluÃ§Ãµes Financeiras</h1>
            </div>

            <div class="title-section">
                <h2>CONTRATO DE PRESTAÃ‡ÃƒO DE SERVIÃ‡OS</h2>
                <div class="subtitle">{subtitle}</div>
            </div>

            <div class="contract-info">
                <span><strong>NÂº:</strong> {contrato.numero}</span>
                <span><strong>Data:</strong> {contrato_data}</span>
            </div>

            <div class="parties">
                <div class="party-box">
                    <h3>CONTRATANTE</h3>
                    <p><strong>Nome:</strong> {contrato.contratante_nome}</p>
                    <p><strong>CPF/CNPJ:</strong> {format_document(contrato.contratante_documento)}</p>
                    {f'<p><strong>CNH:</strong> {cnh_numero}</p>' if is_cnh and cnh_numero else ''}
                    <p><strong>E-mail:</strong> {contrato.contratante_email}</p>
                    {f'<p><strong>Contato:</strong> {contrato.contratante_telefone}</p>' if contrato.contratante_telefone else ''}
                    <p><strong>EndereÃ§o:</strong> {contrato.contratante_endereco}</p>
                </div>
                <div class="party-box">
                    <h3>CONTRATADA</h3>
                    <p><strong>RazÃ£o Social:</strong> FC SERVIÃ‡OS E SOLUÃ‡Ã•ES ADMINISTRATIVAS LTDA</p>
                    <p><strong>CNPJ:</strong> 57.815.628/0001-62</p>
                    <p><strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com</p>
                    <p><strong>Contato:</strong> (16) 99301-7396</p>
                    <p><strong>EndereÃ§o:</strong> Rua Maria das GraÃ§as de Negreiros Bonilha, nÂº 30, sala 3, Jardim Nova AlianÃ§a Sul, RibeirÃ£o Preto/SP, CEP 14022-100</p>
                </div>
            </div>

            <div class="intro">
                As partes acima identificadas tÃªm, entre si, justo e acertado o presente Contrato de PrestaÃ§Ã£o de ServiÃ§os,
                que se regerÃ¡ pelas clÃ¡usulas seguintes e pelas condiÃ§Ãµes descritas no presente.
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
                        <strong>FC SERVIÃ‡OS E SOLUÃ‡Ã•ES ADMINISTRATIVAS LTDA</strong><br>
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
                FC SoluÃ§Ãµes Financeiras - CNPJ: 57.815.628/0001-62<br>
                Documento gerado em {datetime.now().strftime('%d/%m/%Y')}
            </div>
        </body>
        </html>
        """
        return html



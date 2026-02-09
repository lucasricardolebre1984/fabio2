/**
 * Gera PDF via impressao do navegador.
 */
function normalizeMojibakeText(value?: string | null): string {
  const text = String(value || '').trim()
  if (!text) return ''
  if (!/[\u00C3\u00C2]/.test(text)) return text

  try {
    const bytes = Uint8Array.from(text, (char) => char.charCodeAt(0))
    return new TextDecoder('utf-8').decode(bytes)
  } catch {
    return text
  }
}

export function generateContractPDF(contractData: any) {
  const printWindow = window.open('', '_blank')

  if (!printWindow) {
    alert('Por favor, permita popups para gerar o PDF')
    return
  }

  const templateId = String(contractData?.template_id || '').toLowerCase()
  const isCadin = templateId === 'cadin'
  const normalizedLocalAssinatura =
    normalizeMojibakeText(contractData.local_assinatura) || 'Ribeir\u00E3o Preto/SP'
  const contractSubtitle = isCadin
    ? 'CADIN - Regularização de pendências federais'
    : 'Bacen - Remoção SCR'
  const logoUrl = `${window.location.origin}/logo2.png`

  const clausesHtml = isCadin
    ? `
      <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO</strong><br>
      <strong>1.1.</strong> O presente instrumento tem por objeto a prestação de serviços de assessoria administrativa para a regularização de pendências do(a) CONTRATANTE junto ao Cadastro Informativo de Créditos não Quitados do Setor Público Federal (CADIN), visando à adoção dos procedimentos necessários para obtenção da Certidão Negativa de Débitos (CND) ou documento equivalente, referente às dívidas federais constatadas até a data de assinatura deste contrato.</p>

      <p><strong>§1º.</strong> O serviço inclui análise dos débitos, negociação junto aos órgãos credores para obtenção de descontos e formalização de parcelamentos, conforme as condições e programas de anistia disponibilizados pelo governo.</p>

      <p><strong>§2º.</strong> Fica expressamente claro que a CONTRATADA não se responsabiliza pela quitação das dívidas do(a) CONTRATANTE, mas sim pela prestação de serviços de assessoria para negociação e regularização dos apontamentos no CADIN.</p>

      <p><strong>§3º.</strong> Débitos que surgirem ou forem inscritos no CADIN após a data de assinatura deste contrato não estarão cobertos por este instrumento.</p>

      <p><strong>1.2.</strong> Os serviços contratados não representam garantia de aprovação de crédito para o(a) CONTRATANTE, mas um meio para regularização da situação fiscal perante os órgãos federais.</p>

      <p><strong>CLÁUSULA SEGUNDA - DAS DESPESAS E HONORÁRIOS</strong><br>
      <strong>2.1.</strong> Como contraprestação pelos serviços descritos na Cláusula 1ª, o(a) CONTRATANTE pagará à CONTRATADA o valor total de <strong>${contractData.valor_total}</strong> (${contractData.valor_total_extenso}), sendo entrada de <strong>${contractData.valor_entrada}</strong> (${contractData.valor_entrada_extenso})${contractData.qtd_parcelas > 0 ? ` e o saldo em ${contractData.qtd_parcelas} (${contractData.qtd_parcelas_extenso}) parcelas de ${contractData.valor_parcela} (${contractData.valor_parcela_extenso}).` : ' com pagamento integral na assinatura.'}</p>

      <p><strong>2.2.</strong> Em caso de atraso superior a 30 (trinta) dias no pagamento de qualquer parcela, o serviço será suspenso. Persistindo a inadimplência, o(a) CONTRATANTE perderá o direito à continuidade do serviço e aos valores já pagos, e as demais parcelas em aberto poderão ser protestadas.</p>

      <p><strong>2.3.</strong> No caso de solicitação de cancelamento pelo(a) CONTRATANTE, será cobrada multa de 30% (trinta por cento) sobre o valor total das parcelas em aberto.</p>

      <p><strong>2.4.</strong> A execução dos serviços terá início imediato após a assinatura deste contrato e confirmação do pagamento da primeira parcela ou do valor integral, conforme modalidade escolhida.</p>

      <p><strong>2.5.</strong> Havendo parcelamento, o não pagamento de qualquer parcela acarretará acréscimo de juros de 2% (dois por cento) ao mês, multa de 10% (dez por cento) e correção monetária.</p>

      <p><strong>2.6.</strong> O não pagamento de uma parcela acarreta vencimento antecipado das vincendas, podendo a CONTRATADA promover cobrança e protesto dos títulos em aberto perante o foro da comarca de Ribeirão Preto/SP.</p>

      <p><strong>2.7.</strong> A rescisão solicitada pelo(a) CONTRATANTE após o início da prestação dos serviços implica multa compensatória de 30% (trinta por cento) do valor acordado, sem direito a ressarcimento dos valores já pagos.</p>

      <p><strong>CLÁUSULA TERCEIRA - DO PRAZO E GARANTIA</strong><br>
      <strong>3.1.</strong> A CONTRATADA realizará os procedimentos no prazo de até 45 (quarenta e cinco) dias úteis, contados da confirmação do pagamento e assinatura deste contrato, podendo ser prorrogado conforme complexidade dos débitos ou prazos dos órgãos.</p>

      <p><strong>§1º - GARANTIA DE RESULTADO:</strong> Caso o serviço não seja executado no prazo estabelecido, a CONTRATADA garantirá devolução integral do valor pago em até 30 (trinta) dias úteis após o término do prazo.</p>

      <p><strong>3.2.</strong> A CONTRATADA oferece garantia de acompanhamento por 1 (um) ano, contado da data de efetiva regularização dos apontamentos. Se os apontamentos das dívidas tratadas neste contrato retornarem ao CADIN nesse período, o processo será refeito sem custo adicional.</p>

      <p><strong>§2º - ABRANGÊNCIA DA GARANTIA:</strong> A garantia aplica-se exclusivamente às dívidas e restrições identificadas e tratadas no âmbito deste contrato. Dívidas ou restrições posteriores não estão cobertas.</p>

      <p><strong>CLÁUSULA QUARTA - DA PROTEÇÃO DE DADOS (LGPD)</strong><br>
      <strong>4.1.</strong> Em conformidade com a Lei nº 13.709/2018 (LGPD), a CONTRATADA tratará os dados pessoais do(a) CONTRATANTE com finalidade exclusiva de execução contratual, nos termos do art. 7º, incisos II, V e X.</p>

      <p><strong>§1º.</strong> A CONTRATADA adota medidas de segurança para proteger os dados e os eliminará após o término do serviço, ressalvadas as obrigações legais de guarda.</p>

      <p><strong>§2º.</strong> O(A) CONTRATANTE pode exercer direitos de titular (acesso, correção, eliminação etc.) a qualquer momento pelo e-mail: contato@fcsolucoesfinanceiras.com.</p>

      <p><strong>CLÁUSULA QUINTA - DO FORO</strong><br>
      <strong>5.1.</strong> Para dirimir quaisquer controvérsias oriundas deste contrato, as partes elegem o foro da comarca de Ribeirão Preto/SP, ressalvada a faculdade do(a) CONTRATANTE de propor ação no foro de seu domicílio, conforme previsto no Código de Defesa do Consumidor.</p>
    `
    : `
      <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO</strong><br>
      O presente contrato tem como objeto a prestação de serviços de consultoria e intermediação administrativa
      pela CONTRATADA em favor do(a) CONTRATANTE, visando à adoção de procedimentos administrativos para a
      regularização de apontamentos de prejuízo registrados no Sistema de Informações de Crédito (SCR) do
      Banco Central do Brasil.</p>

      <p><strong>CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA</strong><br>
      A CONTRATADA se compromete a realizar análise detalhada, elaborar e protocolar requerimentos,
      acompanhar o andamento e manter o(a) CONTRATANTE informado sobre todo o processo.</p>

      <p><strong>CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES DO(A) CONTRATANTE</strong><br>
      O(A) CONTRATANTE se compromete a fornecer todos os documentos solicitados, efetuar o pagamento
      dos honorários nas datas acordadas e não tratar diretamente com instituições financeiras.</p>

      <p><strong>CLÁUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO</strong><br>
      <strong>4.1.</strong> Pelos serviços prestados, o(a) CONTRATANTE pagará à CONTRATADA o valor total de
      <strong>${contractData.valor_total}</strong> (${contractData.valor_total_extenso}), sendo:
      <ul>
        <li><strong>Entrada:</strong> ${contractData.valor_entrada} (${contractData.valor_entrada_extenso}), no ato da assinatura.</li>
        ${contractData.qtd_parcelas > 0 ? `<li><strong>Parcelas:</strong> ${contractData.qtd_parcelas} parcelas de ${contractData.valor_parcela} (${contractData.valor_parcela_extenso}).</li>` : ''}
      </ul>
      </p>

      <p><strong>CLÁUSULA QUINTA - DO PRAZO DE EXECUÇÃO</strong><br>
      O prazo estimado para conclusão é de ${contractData.prazo_1} a ${contractData.prazo_2} dias úteis,
      contados a partir da assinatura e confirmação do pagamento da entrada.</p>

      <p><strong>CLÁUSULA SEXTA - DA GARANTIA</strong><br>
      O serviço é de resultado. Caso não haja conclusão em 60 dias, o contrato será rescindido
      e os valores pagos serão reembolsados integralmente.</p>

      <p><strong>CLÁUSULA SÉTIMA - DO INADIMPLEMENTO</strong><br>
      Em caso de atraso, aplicam-se multa de 10%, juros de 1% ao mês e correção monetária pelo IPCA.</p>

      <p><strong>CLÁUSULA OITAVA - DA CONFIDENCIALIDADE</strong><br>
      As partes se comprometem a manter sigilo sobre todas as informações.</p>

      <p><strong>CLÁUSULA NONA - DO FORO</strong><br>
      Fica eleito o foro da Comarca de São Paulo/SP.</p>
    `

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Contrato ${contractData.numero}</title>
      <style>
        @page { size: A4; margin: 14mm; }
        * { font-family: 'Times New Roman', Times, serif !important; }
        body {
          font-size: 12pt;
          line-height: 1.4;
          max-width: 210mm;
          margin: 0 auto;
          padding: 20px;
        }
        .title { text-align: center; margin-bottom: 20px; }
        .title h2 { font-size: 16pt; border-bottom: 2px solid #000; display: inline-block; padding-bottom: 5px; margin: 0; }
        .parties { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .party-box { border: 2px solid #000; padding: 10px; }
        .party-box h3 { font-size: 11pt; margin: 0 0 8px 0; border-bottom: 1px solid #999; padding-bottom: 3px; }
        .party-box p { margin: 2px 0; font-size: 10pt; }
        .clauses p { margin: 8px 0; text-align: justify; }
        .clauses strong { text-transform: uppercase; }
        .signatures { margin-top: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 50px; }
        .signature { text-align: center; }
        .signature-line { border-top: 1px solid #000; margin-top: 50px; padding-top: 5px; }
        ul { margin: 5px 0; padding-left: 25px; }
        li { margin: 3px 0; }
        @media print { body { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
      </style>
    </head>
    <body>
      <div style="background: #1e3a5f; color: white; padding: 15px 20px; margin: -20px -20px 20px -20px; display: flex; align-items: center; gap: 15px;">
        <div style="flex-shrink: 0;">
          <img src="${logoUrl}" alt="FC Soluções Financeiras" style="height: 78px; width: auto; display: block;" />
        </div>
        <div style="flex: 1;">
          <h1 style="font-size: 22pt; font-weight: bold; margin: 0; color: white;">F C Soluções Financeiras</h1>
        </div>
      </div>

      <div class="title">
        <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</h2>
        <div style="font-size: 11pt; color: #333; margin-top: 8px;">${contractSubtitle}</div>
      </div>

      <div style="text-align: center; margin-bottom: 20px; font-size: 11pt;">
        <span><strong>Nº:</strong> ${contractData.numero}</span>
        <span style="margin: 0 15px;"><strong>Data:</strong> ${contractData.data_assinatura || new Date().toLocaleDateString('pt-BR')}</span>
      </div>

      <div class="parties">
        <div class="party-box">
          <h3>CONTRATANTE</h3>
          <p><strong>Nome:</strong> ${contractData.contratante_nome}</p>
          <p><strong>CPF/CNPJ:</strong> ${contractData.contratante_documento}</p>
          <p><strong>E-mail:</strong> ${contractData.contratante_email}</p>
          ${contractData.contratante_telefone ? `<p><strong>Contato:</strong> ${contractData.contratante_telefone}</p>` : ''}
          <p><strong>Endereço:</strong> ${contractData.contratante_endereco}</p>
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

      <p style="text-align: justify; margin-bottom: 15px; font-size: 11pt;">
        As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços,
        que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.
      </p>

      <div class="clauses" style="font-size: 11pt;">
        ${clausesHtml}
        <p>E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias.</p>
        <p style="margin-top: 20px;"><strong>${normalizedLocalAssinatura}, ${contractData.data_assinatura || new Date().toLocaleDateString('pt-BR')}.</strong></p>
      </div>

      <div class="signatures">
        <div class="signature">
          <div class="signature-line">
            <strong>${contractData.contratante_nome}</strong><br>
            CPF: ${contractData.contratante_documento}<br>
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

      <script>
        window.onload = function() {
          setTimeout(function() {
            window.print();
          }, 500);
        };
      </script>
    </body>
    </html>
  `

  printWindow.document.write(html)
  printWindow.document.close()
}

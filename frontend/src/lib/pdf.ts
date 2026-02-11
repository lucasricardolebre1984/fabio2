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
  const isCnh = templateId === 'cnh'
  const normalizedLocalAssinatura =
    normalizeMojibakeText(contractData.local_assinatura) || 'Ribeir\u00E3o Preto/SP'
  const contractSubtitle = isCadin
    ? 'CADIN - Regularizacao de pendencias federais'
    : isCnh
      ? 'CNH - Cassacao/Suspensao e Recurso de Multas'
      : 'Bacen - Remocao SCR'
  const logoUrl = `${window.location.origin}/logo2.png`

  const clausesHtml = isCadin
    ? `
      <p><strong>CLAUSULA PRIMEIRA - DO OBJETO</strong><br>
      <strong>1.1.</strong> O presente instrumento tem por objeto a prestacao de servicos de assessoria administrativa para regularizacao de pendencias no CADIN.</p>
      <p><strong>1.2.</strong> O servico compreende analise de debitos, negociacao e formalizacao de parcelamentos, conforme regras dos orgaos.</p>
      <p><strong>CLAUSULA SEGUNDA - DAS DESPESAS E HONORARIOS</strong><br>
      <strong>2.1.</strong> Valor total <strong>${contractData.valor_total}</strong> (${contractData.valor_total_extenso}), com entrada de <strong>${contractData.valor_entrada}</strong> (${contractData.valor_entrada_extenso})${contractData.qtd_parcelas > 0 ? ` e saldo em ${contractData.qtd_parcelas} parcelas de ${contractData.valor_parcela}.` : ' com pagamento integral na assinatura.'}</p>
      <p><strong>CLAUSULA TERCEIRA - PRAZO E GARANTIA</strong><br>
      Prazo de ate 45 dias uteis para execucao, com garantia de devolucao integral se houver descumprimento de prazo por culpa da CONTRATADA.</p>
      <p><strong>CLAUSULA QUARTA - LGPD</strong><br>
      Dados tratados para execucao contratual conforme Lei 13.709/2018.</p>
      <p><strong>CLAUSULA QUINTA - FORO</strong><br>
      Foro da comarca de Ribeirao Preto/SP, ressalvado o foro do domicilio do consumidor.</p>
    `
    : isCnh
      ? `
      <p><strong>CLAUSULA PRIMEIRA - DO OBJETO</strong><br>
      Prestacao de servicos de assessoria tecnica para defesa administrativa e judicial contra suspensao/cassacao de CNH e multas de transito.</p>
      <p><strong>CLAUSULA SEGUNDA - OBRIGACOES DA CONTRATADA</strong><br>
      Analise tecnica, elaboracao/protocolo de recursos e acompanhamento processual ate decisao final.</p>
      <p><strong>CLAUSULA TERCEIRA - OBRIGACOES DO(A) CONTRATANTE</strong><br>
      Fornecer documentos veridicos, efetuar pagamentos nas datas e atender diligencias quando convocado(a).</p>
      <p><strong>CLAUSULA QUARTA - VALOR E PAGAMENTO</strong><br>
      Valor total <strong>${contractData.valor_total}</strong> (${contractData.valor_total_extenso}), com entrada de <strong>${contractData.valor_entrada}</strong> (${contractData.valor_entrada_extenso})${contractData.qtd_parcelas > 0 ? ` e saldo em ${contractData.qtd_parcelas} parcelas de ${contractData.valor_parcela}.` : ' com pagamento integral na assinatura.'}</p>
      <p><strong>CLAUSULA QUINTA - PRAZO</strong><br>
      A CONTRATADA executara a fase administrativa em ate 15 dias uteis apos assinatura, pagamento e entrega documental.</p>
      <p><strong>CLAUSULA SEXTA - GARANTIA DE ENTREGA</strong><br>
      Se nao houver protocolo no prazo por culpa da CONTRATADA, devolucao integral em ate 10 dias uteis.</p>
      <p><strong>CLAUSULA SETIMA - INADIMPLEMENTO</strong><br>
      Multa de 20%, juros de 1% ao mes e correcao pelo IPCA. Atraso prolongado implica suspensao e perda do direito ao servico.</p>
      <p><strong>CLAUSULA OITAVA - RESCISAO</strong><br>
      Rescisao pelo(a) CONTRATANTE apos inicio do servico gera multa de 20%, salvo inadimplemento da CONTRATADA.</p>
      <p><strong>CLAUSULA NONA - LGPD E CONFIDENCIALIDADE</strong><br>
      Dados tratados somente para execucao contratual, com sigilo das informacoes.</p>
      <p><strong>CLAUSULA DECIMA - FORO</strong><br>
      Foro da comarca de Ribeirao Preto/SP, ressalvado o foro do domicilio do(a) CONTRATANTE.</p>
    `
      : `
      <p><strong>CLAUSULA PRIMEIRA - DO OBJETO</strong><br>
      O presente contrato tem como objeto a prestacao de servicos de consultoria e intermediacao administrativa para regularizacao de apontamentos no SCR.</p>
      <p><strong>CLAUSULA SEGUNDA - OBRIGACOES DA CONTRATADA</strong><br>
      Analise tecnica, protocolo de requerimentos e acompanhamento do processo.</p>
      <p><strong>CLAUSULA TERCEIRA - OBRIGACOES DO(A) CONTRATANTE</strong><br>
      Fornecer documentos, efetuar pagamentos e manter alinhamento operacional com a CONTRATADA.</p>
      <p><strong>CLAUSULA QUARTA - VALOR E PAGAMENTO</strong><br>
      Valor total <strong>${contractData.valor_total}</strong> (${contractData.valor_total_extenso}), com entrada de ${contractData.valor_entrada} e ${contractData.qtd_parcelas} parcelas quando aplicavel.</p>
      <p><strong>CLAUSULA QUINTA - PRAZO E GARANTIA</strong><br>
      Prazo estimado entre ${contractData.prazo_1} e ${contractData.prazo_2} dias uteis, com garantia contratual de execucao.</p>
      <p><strong>CLAUSULA SEXTA - INADIMPLEMENTO E FORO</strong><br>
      Em atraso aplicam-se multa, juros e correcao monetaria; foro eleito conforme clausula contratual.</p>
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
          ${isCnh && contractData?.dados_extras?.cnh_numero ? `<p><strong>CNH:</strong> ${contractData.dados_extras.cnh_numero}</p>` : ''}
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


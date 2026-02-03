/**
 * Gerar PDF do contrato usando impressão do navegador
 * Solução simples e funcional - não requer backend
 */

export function generateContractPDF(contractData: any) {
  // Abrir em nova janela com apenas o conteúdo do contrato
  const printWindow = window.open('', '_blank');
  
  if (!printWindow) {
    alert('Por favor, permita popups para gerar o PDF');
    return;
  }

  // Criar HTML limpo para impressão
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Contrato ${contractData.numero}</title>
      <style>
        @page { size: A4; margin: 15mm; }
        body { 
          font-family: 'Times New Roman', serif; 
          font-size: 11pt; 
          line-height: 1.4;
          max-width: 210mm;
          margin: 0 auto;
          padding: 20px;
        }
        .header { display: flex; align-items: flex-start; gap: 15px; border-bottom: 2px solid #000; padding-bottom: 15px; margin-bottom: 20px; }
        .logo { width: 70px; height: 70px; background: #627d98; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; font-weight: bold; }
        .company-info h1 { font-size: 16pt; margin: 0 0 5px 0; }
        .company-info p { margin: 2px 0; font-size: 9pt; }
        .title { text-align: center; margin-bottom: 20px; }
        .title h2 { font-size: 14pt; border-bottom: 2px solid #000; display: inline-block; padding-bottom: 5px; margin: 0; }
        .parties { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .party-box { border: 2px solid #000; padding: 10px; }
        .party-box h3 { font-size: 10pt; margin: 0 0 8px 0; border-bottom: 1px solid #999; padding-bottom: 3px; }
        .party-box p { margin: 2px 0; font-size: 9pt; }
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
      <div class="header">
        <div class="logo">FC</div>
        <div class="company-info">
          <h1>FC SOLUÇÕES FINANCEIRAS</h1>
          <p>CNPJ: 57.815.628/0001-62</p>
          <p>Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3</p>
          <p>Jardim Nova Aliança Sul - Ribeirão Preto/SP - CEP 14022-100</p>
          <p>contato@fcsolucoesfinanceiras.com</p>
        </div>
        <div style="margin-left: auto; font-size: 10pt; font-weight: bold;">Tel: (16) 99301-7396</div>
      </div>

      <div class="title">
        <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</h2>
        <div style="font-size: 10pt; color: #333; margin-top: 8px;">Bacen - Remoção SCR</div>
      </div>

      <div style="text-align: center; margin-bottom: 20px; font-size: 10pt;">
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

      <p style="text-align: justify; margin-bottom: 15px; font-size: 10pt;">
        As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços, 
        que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.
      </p>

      <div class="clauses" style="font-size: 10pt;">
        <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO</strong><br>
        O presente contrato tem como objeto a prestação de serviços de consultoria e intermediação administrativa 
        pela CONTRATADA em favor do(a) CONTRATANTE, visando a adoção de procedimentos administrativos para a 
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

        <p>E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias.</p>

        <p style="margin-top: 20px;"><strong>${contractData.local_assinatura || 'Ribeirão Preto/SP'}, ${contractData.data_assinatura || new Date().toLocaleDateString('pt-BR')}.</strong></p>
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
        // Imprimir automaticamente após carregar
        window.onload = function() {
          setTimeout(function() {
            window.print();
          }, 500);
        };
      </script>
    </body>
    </html>
  `;

  printWindow.document.write(html);
  printWindow.document.close();
}

/**
 * Gera PDF via impressão do navegador.
 */

interface TemplateClause {
  numero?: string
  titulo?: string
  conteudo?: string
  paragrafos?: string[]
}

interface ContractTemplatePayload {
  subtitulo?: string
  clausulas?: TemplateClause[]
}

const CP1252_UNICODE_TO_BYTE: Record<number, number> = {
  0x20ac: 0x80,
  0x201a: 0x82,
  0x0192: 0x83,
  0x201e: 0x84,
  0x2026: 0x85,
  0x2020: 0x86,
  0x2021: 0x87,
  0x02c6: 0x88,
  0x2030: 0x89,
  0x0160: 0x8a,
  0x2039: 0x8b,
  0x0152: 0x8c,
  0x017d: 0x8e,
  0x2018: 0x91,
  0x2019: 0x92,
  0x201c: 0x93,
  0x201d: 0x94,
  0x2022: 0x95,
  0x2013: 0x96,
  0x2014: 0x97,
  0x02dc: 0x98,
  0x2122: 0x99,
  0x0161: 0x9a,
  0x203a: 0x9b,
  0x0153: 0x9c,
  0x017e: 0x9e,
  0x0178: 0x9f,
}

function mojibakeScore(text: string): number {
  const markers = text.match(/[ÃÂâ�]/g)
  return markers ? markers.length : 0
}

function decodeMojibakeOnce(text: string): string {
  const bytes: number[] = []
  for (const char of text) {
    const code = char.charCodeAt(0)
    if (code <= 0xff) {
      bytes.push(code)
      continue
    }

    const mapped = CP1252_UNICODE_TO_BYTE[code]
    if (mapped === undefined) {
      return text
    }
    bytes.push(mapped)
  }

  try {
    return new TextDecoder('utf-8').decode(Uint8Array.from(bytes))
  } catch {
    return text
  }
}

function normalizeMojibakeText(value?: string | null): string {
  const text = String(value || '').trim()
  if (!text) return ''
  if (mojibakeScore(text) === 0) return text

  let normalized = text
  for (let i = 0; i < 2; i += 1) {
    const candidate = decodeMojibakeOnce(normalized)
    if (mojibakeScore(candidate) >= mojibakeScore(normalized)) break
    normalized = candidate
  }

  return normalized
}

function normalizeMarkdownInline(value: string): string {
  return value
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/__(.*?)__/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .trim()
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function formatCurrency(value: unknown): string {
  const numeric = Number(value || 0)
  return `R$ ${numeric.toFixed(2).replace('.', ',')}`
}

function formatDocument(documento?: string): string {
  const clean = String(documento || '').replace(/\D/g, '')
  if (clean.length === 11) {
    return `${clean.slice(0, 3)}.${clean.slice(3, 6)}.${clean.slice(6, 9)}-${clean.slice(9)}`
  }
  if (clean.length === 14) {
    return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}/${clean.slice(8, 12)}-${clean.slice(12)}`
  }
  return String(documento || '')
}

function formatPrazoDisplay(value: unknown): string {
  const numeric = Number(value || 0)
  return numeric > 0 ? String(numeric) : 'à vista'
}

function formatPrazoExtensoDisplay(value: unknown, extenso: unknown): string {
  const numeric = Number(value || 0)
  if (numeric <= 0) return 'à vista'
  return String(extenso || '')
}

function replaceTemplateTokens(value: string, contractData: any): string {
  const mapped: Record<string, string> = {
    '[NOME COMPLETO DO CLIENTE]': String(contractData?.contratante_nome || ''),
    '[NÚMERO DO DOCUMENTO]': formatDocument(contractData?.contratante_documento),
    '[NUMERO DO DOCUMENTO]': formatDocument(contractData?.contratante_documento),
    '[E-MAIL DO CLIENTE]': String(contractData?.contratante_email || ''),
    '[TELEFONE DO CLIENTE]': String(contractData?.contratante_telefone || '-'),
    '[ENDEREÇO COMPLETO DO CLIENTE]': String(contractData?.contratante_endereco || ''),
    '[ENDERECO COMPLETO DO CLIENTE]': String(contractData?.contratante_endereco || ''),
    '[VALOR]': formatCurrency(contractData?.valor_total),
    '[VALOR EXTENSO]': String(contractData?.valor_total_extenso || ''),
    '[VALOR ENTRADA]': formatCurrency(contractData?.valor_entrada),
    '[VALOR ENTRADA EXTENSO]': String(contractData?.valor_entrada_extenso || ''),
    '[QTD PARCELAS]': String(contractData?.qtd_parcelas || ''),
    '[QTD PARCELAS EXTENSO]': String(contractData?.qtd_parcelas_extenso || ''),
    '[VALOR PARCELA]': formatCurrency(contractData?.valor_parcela),
    '[VALOR PARCELA EXTENSO]': String(contractData?.valor_parcela_extenso || ''),
    '[PRAZO 1]': formatPrazoDisplay(contractData?.prazo_1),
    '[PRAZO 1 EXTENSO]': formatPrazoExtensoDisplay(contractData?.prazo_1, contractData?.prazo_1_extenso),
    '[PRAZO 2]': formatPrazoDisplay(contractData?.prazo_2),
    '[PRAZO 2 EXTENSO]': formatPrazoExtensoDisplay(contractData?.prazo_2, contractData?.prazo_2_extenso),
  }

  return Object.entries(mapped).reduce((acc, [token, replacement]) => {
    return acc.split(token).join(replacement)
  }, value)
}

function getClauseContent(clause?: TemplateClause): string {
  const content = String(clause?.conteudo || '').trim()
  if (content) return content

  if (Array.isArray(clause?.paragrafos)) {
    return clause.paragrafos
      .map((line) => String(line || '').trim())
      .filter(Boolean)
      .join('\n\n')
  }

  return ''
}

function buildClausesHtml(contractData: any, templateData?: ContractTemplatePayload | null): string {
  const clauses = Array.isArray(templateData?.clausulas) ? templateData!.clausulas : []
  if (!clauses.length) {
    return `
      <p><strong>CLÁUSULAS</strong><br>
      Template sem cláusulas estruturadas para renderização de PDF.</p>
    `
  }

  return clauses
    .map((clause) => {
      const heading = [clause?.numero, clause?.titulo]
        .filter(Boolean)
        .map((part) => normalizeMojibakeText(String(part)))
        .join(' - ')

      const text = replaceTemplateTokens(normalizeMojibakeText(getClauseContent(clause)), contractData)
      const lines = text.split('\n')

      const htmlLines: string[] = []
      let listItems: string[] = []

      const flushList = () => {
        if (!listItems.length) return
        htmlLines.push(`<ul>${listItems.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`)
        listItems = []
      }

      lines.forEach((rawLine) => {
        const line = normalizeMarkdownInline(rawLine)
        if (!line || line === '---') {
          flushList()
          return
        }

        if (/^[-*]\s+/.test(line)) {
          listItems.push(line.replace(/^[-*]\s+/, '').trim())
          return
        }

        flushList()
        htmlLines.push(`<p>${escapeHtml(line)}</p>`)
      })

      flushList()

      return `
        <div class="clause-block">
          ${heading ? `<p><strong>${escapeHtml(heading)}</strong></p>` : ''}
          ${htmlLines.join('')}
        </div>
      `
    })
    .join('')
}

export function generateContractPDF(contractData: any, templateData?: ContractTemplatePayload | null) {
  const printWindow = window.open('', '_blank')

  if (!printWindow) {
    alert('Por favor, permita popups para gerar o PDF')
    return
  }

  const templateId = String(contractData?.template_id || '').toLowerCase()
  const subtitleFromTemplate = normalizeMojibakeText(templateData?.subtitulo)
  const normalizedLocalAssinatura = normalizeMojibakeText(contractData?.local_assinatura) || 'Ribeirão Preto/SP'
  const contractSubtitle =
    subtitleFromTemplate ||
    (templateId === 'cadin'
      ? 'CADIN - Regularização de pendências federais'
      : templateId === 'cnh'
        ? 'CNH - Cassação/Suspensão e Recurso de Multas'
        : 'Bacen - Remoção SCR')

  const logoUrl = `${window.location.origin}/logo2.png`
  const clausesHtml = buildClausesHtml(contractData, templateData)

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Contrato ${escapeHtml(String(contractData?.numero || ''))}</title>
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
        .clauses ul { margin: 6px 0; padding-left: 24px; }
        .clauses li { margin: 3px 0; }
        .clause-block { margin-bottom: 10px; }
        .signatures { margin-top: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 50px; }
        .signature { text-align: center; }
        .signature-line { border-top: 1px solid #000; margin-top: 50px; padding-top: 5px; }
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
        <div style="font-size: 11pt; color: #333; margin-top: 8px;">${escapeHtml(contractSubtitle)}</div>
      </div>

      <div style="text-align: center; margin-bottom: 20px; font-size: 11pt;">
        <span><strong>Nº:</strong> ${escapeHtml(String(contractData?.numero || ''))}</span>
        <span style="margin: 0 15px;"><strong>Data:</strong> ${escapeHtml(String(contractData?.data_assinatura || new Date().toLocaleDateString('pt-BR')))}</span>
      </div>

      <div class="parties">
        <div class="party-box">
          <h3>CONTRATANTE</h3>
          <p><strong>Nome:</strong> ${escapeHtml(String(contractData?.contratante_nome || ''))}</p>
          <p><strong>CPF/CNPJ:</strong> ${escapeHtml(formatDocument(contractData?.contratante_documento))}</p>
          <p><strong>E-mail:</strong> ${escapeHtml(String(contractData?.contratante_email || ''))}</p>
          ${contractData?.contratante_telefone ? `<p><strong>Contato:</strong> ${escapeHtml(String(contractData.contratante_telefone))}</p>` : ''}
          <p><strong>Endereço:</strong> ${escapeHtml(String(contractData?.contratante_endereco || ''))}</p>
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
        <p style="margin-top: 20px;"><strong>${escapeHtml(normalizedLocalAssinatura)}, ${escapeHtml(String(contractData?.data_assinatura || new Date().toLocaleDateString('pt-BR')))}.</strong></p>
      </div>

      <div class="signatures">
        <div class="signature">
          <div class="signature-line">
            <strong>${escapeHtml(String(contractData?.contratante_nome || ''))}</strong><br>
            CPF/CNPJ: ${escapeHtml(formatDocument(contractData?.contratante_documento))}<br>
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

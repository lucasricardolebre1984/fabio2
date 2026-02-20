'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { ArrowLeft, Download, Edit, Mail, Printer } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { contratosApi } from '@/lib/api'
import { formatCPF, formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

interface Contrato {
  id: string
  numero: string
  template_id: string
  template_nome: string
  status: string
  contratante_nome: string
  contratante_documento: string
  contratante_email: string
  contratante_telefone?: string
  contratante_endereco: string
  valor_total: number
  valor_entrada: number
  qtd_parcelas: number
  valor_parcela: number
  prazo_1: number
  prazo_2: number
  local_assinatura: string
  data_assinatura: string
  valor_total_extenso: string
  valor_entrada_extenso: string
  qtd_parcelas_extenso: string
  valor_parcela_extenso: string
  prazo_1_extenso: string
  prazo_2_extenso: string
  dados_extras?: Record<string, unknown>
  created_at: string
  updated_at?: string
  cliente_nome?: string
}

interface TemplateClause {
  numero?: string
  titulo?: string
  conteudo?: string
  paragrafos?: string[]
}

interface ContratoTemplateData {
  id: string
  nome: string
  tipo: string
  descricao?: string
  categoria?: string
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

function formatExtraLabel(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatPrazoDisplay(value: number): string {
  return Number(value || 0) > 0 ? String(value) : 'à vista'
}

function formatPrazoExtensoDisplay(value: number, extenso?: string): string {
  if (Number(value || 0) <= 0) return 'à vista'
  return String(extenso || '')
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

export default function VisualizarContratoPage() {
  const params = useParams()
  const router = useRouter()
  const [contrato, setContrato] = useState<Contrato | null>(null)
  const [templateData, setTemplateData] = useState<ContratoTemplateData | null>(null)
  const [loading, setLoading] = useState(true)

  const carregarContrato = useCallback(async () => {
    try {
      const id = params.id as string
      const data = await contratosApi.getById(id)
      setContrato(data)

      try {
        const template = await contratosApi.getTemplate(String(data?.template_id || '').toLowerCase())
        setTemplateData(template)
      } catch {
        setTemplateData(null)
      }
    } catch {
      toast.error('Erro ao carregar contrato')
    } finally {
      setLoading(false)
    }
  }, [params.id])

  useEffect(() => {
    void carregarContrato()
  }, [carregarContrato])

  const handlePrint = async () => {
    try {
      const { generateContractPDF } = await import('@/lib/pdf')
      generateContractPDF(contrato, templateData)
      toast.success('PDF aberto para visualização!')
    } catch {
      toast.error('Erro ao gerar PDF')
    }
  }

  const handleDownload = async () => {
    try {
      const { generateContractPDF } = await import('@/lib/pdf')
      generateContractPDF(contrato, templateData)
      toast.success('PDF aberto para download!')
    } catch {
      toast.error('Erro ao gerar PDF')
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      rascunho: 'bg-yellow-100 text-yellow-800',
      ativo: 'bg-green-100 text-green-800',
      cancelado: 'bg-red-100 text-red-800',
      concluido: 'bg-blue-100 text-blue-800',
    }
    return variants[status] || 'bg-gray-100 text-gray-800'
  }

  const contractSubtitle = useMemo(() => {
    const fromTemplate = normalizeMojibakeText(templateData?.subtitulo)
    if (fromTemplate) return fromTemplate

    const templateId = String(contrato?.template_id || '').toLowerCase()
    if (templateId === 'cadin') return 'CADIN - Regularização de pendências federais'
    if (templateId === 'cnh') return 'CNH - Cassação/Suspensão e Recurso de Multas'
    return 'Bacen - Remoção SCR'
  }, [contrato?.template_id, templateData?.subtitulo])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-[#627d98]"></div>
      </div>
    )
  }

  if (!contrato) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-gray-500">
        <p>Contrato não encontrado</p>
        <Button variant="outline" className="mt-4" onClick={() => router.push('/contratos/lista')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
      </div>
    )
  }

  const localAssinatura = normalizeMojibakeText(contrato.local_assinatura) || 'Ribeirão Preto/SP'
  const clauses = Array.isArray(templateData?.clausulas) ? templateData!.clausulas : []

  const replaceTemplateTokens = (value: string) => {
    const cnhNumero =
      contrato.dados_extras &&
      typeof contrato.dados_extras === 'object' &&
      'cnh_numero' in contrato.dados_extras
        ? String(contrato.dados_extras.cnh_numero || '-')
        : '-'

    const mapped: Record<string, string> = {
      '[NOME COMPLETO DO CLIENTE]': contrato.contratante_nome,
      '[NÚMERO DO DOCUMENTO]': formatCPF(contrato.contratante_documento),
      '[NUMERO DO DOCUMENTO]': formatCPF(contrato.contratante_documento),
      '[E-MAIL DO CLIENTE]': contrato.contratante_email,
      '[TELEFONE DO CLIENTE]': contrato.contratante_telefone || '-',
      '[ENDEREÇO COMPLETO DO CLIENTE]': contrato.contratante_endereco,
      '[ENDERECO COMPLETO DO CLIENTE]': contrato.contratante_endereco,
      '[NÚMERO CNH]': cnhNumero,
      '[NUMERO CNH]': cnhNumero,
      '[VALOR]': formatCurrency(contrato.valor_total),
      '[VALOR EXTENSO]': contrato.valor_total_extenso,
      '[VALOR ENTRADA]': formatCurrency(contrato.valor_entrada),
      '[VALOR ENTRADA EXTENSO]': contrato.valor_entrada_extenso,
      '[QTD PARCELAS]': String(contrato.qtd_parcelas),
      '[QTD PARCELAS EXTENSO]': contrato.qtd_parcelas_extenso,
      '[VALOR PARCELA]': formatCurrency(contrato.valor_parcela),
      '[VALOR PARCELA EXTENSO]': contrato.valor_parcela_extenso,
      '[PRAZO 1]': formatPrazoDisplay(contrato.prazo_1),
      '[PRAZO 1 EXTENSO]': formatPrazoExtensoDisplay(contrato.prazo_1, contrato.prazo_1_extenso),
      '[PRAZO 2]': formatPrazoDisplay(contrato.prazo_2),
      '[PRAZO 2 EXTENSO]': formatPrazoExtensoDisplay(contrato.prazo_2, contrato.prazo_2_extenso),
    }

    return Object.entries(mapped).reduce((acc, [token, replacement]) => {
      return acc.split(token).join(replacement)
    }, value)
  }

  const renderClauseBody = (content?: string) => {
    const text = replaceTemplateTokens(normalizeMojibakeText(content || ''))
    const lines = text.split('\n')

    const nodes: JSX.Element[] = []
    let bullets: string[] = []

    const flushBullets = (keyPrefix: string) => {
      if (!bullets.length) return
      nodes.push(
        <ul key={`${keyPrefix}-list-${nodes.length}`} className="list-disc space-y-1 pl-6">
          {bullets.map((item, idx) => (
            <li key={`${keyPrefix}-item-${idx}`}>{normalizeMarkdownInline(item)}</li>
          ))}
        </ul>
      )
      bullets = []
    }

    lines.forEach((rawLine, idx) => {
      const line = normalizeMarkdownInline(rawLine)
      if (!line || line === '---') {
        flushBullets(`flush-${idx}`)
        return
      }

      if (/^[-*]\s+/.test(line)) {
        bullets.push(line.replace(/^[-*]\s+/, '').trim())
        return
      }

      flushBullets(`line-${idx}`)
      nodes.push(
        <p key={`paragraph-${idx}`}>
          {line}
        </p>
      )
    })

    flushBullets('end')
    return nodes
  }

  const extraEntries = Object.entries(contrato.dados_extras || {}).filter(
    ([key, value]) => key !== 'forma_pagamento' && value != null && String(value).trim() !== ''
  )

  const renderContratoPreview = () => {
    return (
      <div className="min-h-[1120px] bg-white p-10 shadow-sm [font-family:'Times_New_Roman',Times,serif_!important]">
        <div className="-mx-10 -mt-10 mb-8 bg-[#1e3a5f] px-8 py-5 text-white">
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0">
              <Image
                src="/logo2-tight.png"
                alt="FC Soluções Financeiras"
                width={92}
                height={92}
                className="h-[92px] w-[92px] object-contain"
                priority
              />
            </div>
            <div className="flex-1">
              <h1 className="text-[2rem] font-bold tracking-wide">F C Soluções Financeiras</h1>
            </div>
          </div>
        </div>

        <div className="mb-8 text-center">
          <h2 className="inline-block border-b-2 border-gray-800 pb-2 text-2xl font-bold uppercase tracking-wider text-gray-900">
            Contrato de Prestação de Serviços
          </h2>
          <p className="mt-2 font-semibold text-gray-600">{contractSubtitle}</p>
          <div className="mt-5 flex justify-center gap-10 text-base">
            <span>
              <strong>Nº:</strong> {contrato.numero}
            </span>
            <span>
              <strong>Data:</strong> {contrato.data_assinatura || formatDate(contrato.created_at)}
            </span>
          </div>
        </div>

        <div className="mb-7 grid grid-cols-2 gap-6 text-base">
          <div className="border-2 border-gray-800 p-4">
            <h3 className="mb-3 border-b border-gray-400 pb-1 font-bold uppercase text-gray-900">Contratante</h3>
            <p><strong>Nome:</strong> {contrato.contratante_nome}</p>
            <p><strong>CPF/CNPJ:</strong> {formatCPF(contrato.contratante_documento)}</p>
            <p><strong>E-mail:</strong> {contrato.contratante_email}</p>
            {contrato.contratante_telefone && <p><strong>Contato:</strong> {contrato.contratante_telefone}</p>}
            <p><strong>Endereço:</strong> {contrato.contratante_endereco}</p>
            {extraEntries.map(([key, value]) => (
              <p key={key}><strong>{formatExtraLabel(key)}:</strong> {String(value)}</p>
            ))}
          </div>

          <div className="border-2 border-gray-800 p-4">
            <h3 className="mb-3 border-b border-gray-400 pb-1 font-bold uppercase text-gray-900">Contratada</h3>
            <p><strong>Razão Social:</strong> FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</p>
            <p><strong>CNPJ:</strong> 57.815.628/0001-62</p>
            <p><strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com</p>
            <p><strong>Contato:</strong> (16) 99301-7396</p>
            <p><strong>Endereço:</strong> Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100</p>
          </div>
        </div>

        <p className="mb-7 text-justify text-base leading-relaxed">
          As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços,
          que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.
        </p>

        <div className="space-y-4 text-justify text-base leading-relaxed">
          {clauses.length > 0 ? (
            clauses.map((clause, idx) => {
              const headingParts = [clause.numero, clause.titulo].filter(Boolean)
              const heading = headingParts.join(' - ')

              return (
                <div key={`clause-${idx}`} className="space-y-2">
                  {heading ? <p><strong className="uppercase text-gray-900">{normalizeMojibakeText(heading)}</strong></p> : null}
                  {renderClauseBody(getClauseContent(clause))}
                </div>
              )
            })
          ) : (
            <p>
              <strong className="uppercase text-gray-900">Cláusulas não cadastradas</strong><br />
              Este template ainda não possui cláusulas estruturadas para visualização.
            </p>
          )}

          <p className="mt-6">E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias de igual teor e forma.</p>
          <p className="mt-4 font-semibold">{localAssinatura}, {contrato.data_assinatura || formatDate(contrato.created_at)}.</p>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-8">
          <div className="text-center">
            <div className="mt-16 border-t-2 border-black pt-2">
              <p className="text-base font-bold">{contrato.contratante_nome}</p>
              <p className="text-xs text-gray-600">CPF: {formatCPF(contrato.contratante_documento)}</p>
              <p className="mt-1 text-xs font-semibold uppercase text-gray-500">CONTRATANTE</p>
            </div>
          </div>
          <div className="text-center">
            <div className="mt-16 border-t-2 border-black pt-2">
              <p className="text-base font-bold">FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</p>
              <p className="text-xs text-gray-600">CNPJ: 57.815.628/0001-62</p>
              <p className="mt-1 text-xs font-semibold uppercase text-gray-500">CONTRATADA</p>
            </div>
          </div>
        </div>

        <div className="mt-8 text-base">
          <p className="mb-2 font-bold">Testemunhas:</p>
          <div className="grid grid-cols-2 gap-8">
            <div>
              <p>1. _______________________________________</p>
              <p className="mt-1 text-xs text-gray-600">Nome:</p>
              <p className="text-xs text-gray-600">CPF:</p>
            </div>
            <div>
              <p>2. _______________________________________</p>
              <p className="mt-1 text-xs text-gray-600">Nome:</p>
              <p className="text-xs text-gray-600">CPF:</p>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t border-gray-300 pt-3 text-center text-xs text-gray-500">
          <p>FC Soluções Financeiras - CNPJ: 57.815.628/0001-62</p>
          <p>Documento gerado em {formatDate(new Date().toISOString())}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => router.push('/contratos/lista')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Contrato {contrato.numero}</h1>
            <p className="text-sm text-gray-500">Criado em {formatDate(contrato.created_at)}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getStatusBadge(contrato.status)}>{contrato.status.toUpperCase()}</Badge>
        </div>
      </div>

      <div className="mb-6 flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => router.push(`/contratos/${contrato.id}/editar`)}>
          <Edit className="mr-2 h-4 w-4" />
          Editar
        </Button>
        <Button variant="outline" size="sm" onClick={handlePrint}>
          <Printer className="mr-2 h-4 w-4" />
          Visualizar PDF
        </Button>
        <Button variant="outline" size="sm" onClick={handleDownload}>
          <Download className="mr-2 h-4 w-4" />
          Download
        </Button>
        <Button variant="outline" size="sm" onClick={() => toast.info('Funcionalidade em desenvolvimento')}>
          <Mail className="mr-2 h-4 w-4" />
          Enviar
        </Button>
      </div>

      <Tabs defaultValue="preview" className="flex-1">
        <TabsList>
          <TabsTrigger value="preview">Visualização</TabsTrigger>
          <TabsTrigger value="data">Dados</TabsTrigger>
        </TabsList>

        <TabsContent value="preview" className="mt-4">
          <Card>
            <CardContent className="p-0">{renderContratoPreview()}</CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="mt-4">
          <Card>
            <CardContent className="p-6">
              <h3 className="mb-4 font-semibold">Dados do Contrato</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Número:</span><span className="font-medium">{contrato.numero}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Template:</span><span className="font-medium">{contrato.template_nome}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Status:</span><span className="font-medium capitalize">{contrato.status}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Contratante:</span><span className="font-medium">{contrato.contratante_nome}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">CPF/CNPJ:</span><span className="font-medium">{formatCPF(contrato.contratante_documento)}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Valor Total:</span><span className="font-medium">{formatCurrency(contrato.valor_total)}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Entrada:</span><span className="font-medium">{formatCurrency(contrato.valor_entrada)}</span></div>
                <div className="flex justify-between border-b py-2"><span className="text-gray-500">Parcelas:</span><span className="font-medium">{contrato.qtd_parcelas}x</span></div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

'use client'

import Link from 'next/link'
import { useCallback, useEffect, useMemo, useState } from 'react'
import Image from 'next/image'
import { BarChart3, Bot, MessageCircle, QrCode, RefreshCw, Send, ShieldCheck, UserRound } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/api'

type WhatsAppStatus = {
  conectado?: boolean
  estado?: string | null
  numero?: string | null
  nome_perfil?: string | null
  instance_name?: string
  erro?: string
  instances_disponiveis?: string[]
}

type ConnectResponse = {
  sucesso: boolean
  conectado?: boolean
  qr_code?: string | null
  mensagem?: string
  erro?: string
  instance_name?: string
}

type WhatsAppConversa = {
  id: string
  numero_telefone: string
  nome_contato: string | null
  instance_name: string
  status: 'ativa' | 'arquivada' | 'aguardando' | string
  ultima_mensagem_em: string | null
  created_at: string
}

type WhatsAppChatStats = {
  conversas_ativas: number
  mensagens_hoje: number
  status?: string
}

type HandoffItem = {
  id: string
  status: 'pending' | 'sent' | 'failed' | string
}

type HandoffListResponse = {
  items: HandoffItem[]
  total: number
  page: number
  page_size: number
}

export default function WhatsAppPage() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [crmLoading, setCrmLoading] = useState(true)
  const [statusData, setStatusData] = useState<WhatsAppStatus | null>(null)
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [chatStats, setChatStats] = useState<WhatsAppChatStats>({ conversas_ativas: 0, mensagens_hoje: 0 })
  const [conversasRecentes, setConversasRecentes] = useState<WhatsAppConversa[]>([])
  const [showingArchivedFallback, setShowingArchivedFallback] = useState(false)
  const [funnelCounts, setFunnelCounts] = useState({
    ativa: 0,
    aguardando: 0,
    arquivada: 0,
    total: 0,
  })
  const [handoffCounts, setHandoffCounts] = useState({
    pending: 0,
    sent: 0,
    failed: 0,
    total: 0,
  })

  const qrSrc = useMemo(() => {
    if (!qrCode) return null
    if (qrCode.startsWith('data:image')) return qrCode
    return `data:image/png;base64,${qrCode}`
  }, [qrCode])

  const carregarStatus = useCallback(async () => {
    try {
      const response = await api.get('/whatsapp/status')
      setStatusData(response.data)
      if (response.data?.conectado) {
        setQrCode(null)
      }
    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Falha ao consultar status do WhatsApp'
      toast({ title: 'Erro no status', description: String(detail), variant: 'destructive' })
    }
  }, [toast])

  const carregarCrm = useCallback(async () => {
    setCrmLoading(true)
    try {
      const [statsResp, ativasResp, aguardandoResp, arquivadasResp, handoffResp] = await Promise.all([
        api.get<WhatsAppChatStats>('/whatsapp-chat/status'),
        api.get<WhatsAppConversa[]>('/whatsapp-chat/conversas', { params: { status: 'ativa', limit: 100 } }),
        api.get<WhatsAppConversa[]>('/whatsapp-chat/conversas', { params: { status: 'aguardando', limit: 100 } }),
        api.get<WhatsAppConversa[]>('/whatsapp-chat/conversas', { params: { status: 'arquivada', limit: 100 } }),
        api.get<HandoffListResponse>('/viva/handoff'),
      ])

      const ativas = ativasResp.data || []
      const aguardando = aguardandoResp.data || []
      const arquivadas = arquivadasResp.data || []
      const handoffItems = handoffResp.data?.items || []
      const abertas = [...ativas, ...aguardando]

      setChatStats(statsResp.data || { conversas_ativas: 0, mensagens_hoje: 0 })
      if (abertas.length > 0) {
        setConversasRecentes(abertas.slice(0, 8))
        setShowingArchivedFallback(false)
      } else {
        setConversasRecentes(arquivadas.slice(0, 8))
        setShowingArchivedFallback(arquivadas.length > 0)
      }
      setFunnelCounts({
        ativa: ativas.length,
        aguardando: aguardando.length,
        arquivada: arquivadas.length,
        total: ativas.length + aguardando.length + arquivadas.length,
      })

      setHandoffCounts({
        pending: handoffItems.filter((item) => item.status === 'pending').length,
        sent: handoffItems.filter((item) => item.status === 'sent').length,
        failed: handoffItems.filter((item) => item.status === 'failed').length,
        total: handoffResp.data?.total || handoffItems.length,
      })
    } catch (error) {
      toast({
        title: 'Falha ao carregar CRM do WhatsApp',
        description: 'Nao foi possivel montar o funil completo no momento.',
        variant: 'destructive',
      })
    } finally {
      setCrmLoading(false)
    }
  }, [toast])

  useEffect(() => {
    const run = async () => {
      await Promise.all([carregarStatus(), carregarCrm()])
      setLoading(false)
    }
    run()
  }, [carregarStatus, carregarCrm])

  useEffect(() => {
    const timer = setInterval(() => {
      void Promise.all([carregarStatus(), carregarCrm()])
    }, 15000)

    return () => clearInterval(timer)
  }, [carregarStatus, carregarCrm])

  const handleConectar = async () => {
    setActionLoading(true)
    try {
      const response = await api.post<ConnectResponse>('/whatsapp/conectar')
      const data = response.data
      if (!data.sucesso) {
        toast({
          title: 'Falha ao conectar',
          description: data.erro || 'Nao foi possivel iniciar conexao',
          variant: 'destructive',
        })
      } else {
        if (data.qr_code) {
          setQrCode(data.qr_code)
        }
        toast({
          title: data.conectado ? 'WhatsApp conectado' : 'Conexao iniciada',
          description: data.mensagem || 'Escaneie o QR Code no aplicativo',
        })
      }
      await Promise.all([carregarStatus(), carregarCrm()])
    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Erro ao conectar WhatsApp'
      toast({ title: 'Erro ao conectar', description: String(detail), variant: 'destructive' })
    } finally {
      setActionLoading(false)
    }
  }

  const handleDesconectar = async () => {
    setActionLoading(true)
    try {
      const response = await api.post('/whatsapp/desconectar')
      if (response.data?.sucesso) {
        setQrCode(null)
        toast({ title: 'WhatsApp desconectado' })
      } else {
        toast({
          title: 'Falha ao desconectar',
          description: response.data?.erro || 'Nao foi possivel desconectar',
          variant: 'destructive',
        })
      }
      await Promise.all([carregarStatus(), carregarCrm()])
    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Erro ao desconectar WhatsApp'
      toast({ title: 'Erro ao desconectar', description: String(detail), variant: 'destructive' })
    } finally {
      setActionLoading(false)
    }
  }

  const conectado = Boolean(statusData?.conectado)

  const taxaFechamento = useMemo(() => {
    if (!funnelCounts.total) return 0
    return Math.round((funnelCounts.arquivada / funnelCounts.total) * 100)
  }, [funnelCounts])

  const formatarNumero = (numero: string) => {
    const digits = String(numero || '').replace(/\D/g, '')
    if (digits.length === 13) {
      return `+${digits.slice(0, 2)} (${digits.slice(2, 4)}) ${digits.slice(4, 9)}-${digits.slice(9)}`
    }
    return numero
  }

  const formatarData = (data: string | null) => {
    if (!data) return '-'
    const dt = new Date(data)
    return dt.toLocaleString('pt-BR')
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">WhatsApp</h1>
        <p className="mt-1 text-sm text-gray-600">
          CRM institucional da persona Viviane + conexao Evolution API
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary-600" />
            Funil operacional (Fabio {'>'} VIVA {'>'} Viviane)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {showingArchivedFallback && (
            <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
              Exibindo conversas arquivadas (nenhuma conversa ativa no momento).
            </div>
          )}
          {crmLoading ? (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Carregando funil e metricas...
            </div>
          ) : (
            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-lg border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">Leads no funil</p>
                <p className="mt-1 text-2xl font-bold text-slate-900">{funnelCounts.total}</p>
              </div>
              <div className="rounded-lg border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">Em atendimento</p>
                <p className="mt-1 text-2xl font-bold text-blue-600">{funnelCounts.ativa}</p>
              </div>
              <div className="rounded-lg border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">Aguardando retorno</p>
                <p className="mt-1 text-2xl font-bold text-amber-600">{funnelCounts.aguardando}</p>
              </div>
              <div className="rounded-lg border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">Concluidas</p>
                <p className="mt-1 text-2xl font-bold text-emerald-600">{funnelCounts.arquivada}</p>
              </div>
              <div className="rounded-lg border bg-white p-4 md:col-span-2">
                <p className="text-xs uppercase tracking-wide text-gray-500">Mensagens hoje</p>
                <p className="mt-1 text-2xl font-bold text-slate-900">{chatStats.mensagens_hoje}</p>
              </div>
              <div className="rounded-lg border bg-white p-4 md:col-span-2">
                <p className="text-xs uppercase tracking-wide text-gray-500">Taxa de fechamento</p>
                <p className="mt-1 text-2xl font-bold text-slate-900">{taxaFechamento}%</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary-600" />
            Persona Viviane (handoff de agenda)
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Pendentes</p>
            <p className="mt-1 text-2xl font-bold text-amber-600">{handoffCounts.pending}</p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Enviados</p>
            <p className="mt-1 text-2xl font-bold text-emerald-600">{handoffCounts.sent}</p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Falhas</p>
            <p className="mt-1 text-2xl font-bold text-rose-600">{handoffCounts.failed}</p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Total handoff</p>
            <p className="mt-1 text-2xl font-bold text-slate-900">{handoffCounts.total}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Status da conexao</span>
            <Badge variant={conectado ? 'default' : 'secondary'}>
              {conectado ? 'Conectado' : 'Desconectado'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2 text-sm text-gray-700 md:grid-cols-2">
            <p>
              <strong>Instancia:</strong> {statusData?.instance_name || '-'}
            </p>
            <p>
              <strong>Estado:</strong> {statusData?.estado || '-'}
            </p>
            <p>
              <strong>Numero:</strong> {statusData?.numero || '-'}
            </p>
            <p>
              <strong>Perfil:</strong> {statusData?.nome_perfil || '-'}
            </p>
          </div>

          {statusData?.erro && (
            <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {statusData.erro}
            </div>
          )}

          {statusData?.instances_disponiveis && statusData.instances_disponiveis.length > 0 && (
            <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">
              Instancias detectadas: {statusData.instances_disponiveis.join(', ')}
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            <Button onClick={handleConectar} disabled={actionLoading}>
              Conectar WhatsApp
            </Button>
            <Button variant="outline" onClick={handleDesconectar} disabled={actionLoading || !conectado}>
              Desconectar
            </Button>
            <Button variant="ghost" onClick={() => Promise.all([carregarStatus(), carregarCrm()])} disabled={actionLoading}>
              Atualizar status
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <UserRound className="h-5 w-5 text-primary-600" />
              Ultimas conversas em atendimento
            </span>
            <Button asChild variant="outline" size="sm">
              <Link href="/whatsapp/conversas">
                <Send className="mr-2 h-4 w-4" />
                Abrir central de conversas
              </Link>
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {crmLoading ? (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Carregando conversas...
            </div>
          ) : conversasRecentes.length === 0 ? (
            <p className="text-sm text-gray-500">Nenhuma conversa ativa encontrada.</p>
          ) : (
            <div className="space-y-2">
              {conversasRecentes.map((conversa) => (
                <div key={conversa.id} className="flex items-center justify-between rounded-md border bg-white p-3">
                  <div>
                    <p className="font-medium text-slate-900">{conversa.nome_contato || 'Contato sem nome'}</p>
                    <p className="text-xs text-gray-500">{formatarNumero(conversa.numero_telefone)}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline">{conversa.status}</Badge>
                    <p className="mt-1 text-xs text-gray-500">{formatarData(conversa.ultima_mensagem_em)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5 text-primary-600" />
            QR Code de conexao
          </CardTitle>
        </CardHeader>
        <CardContent>
          {qrSrc ? (
            <div className="flex flex-col items-center gap-3">
              <Image src={qrSrc} alt="QR Code WhatsApp" width={288} height={288} className="h-72 w-72 rounded-lg border bg-white p-2" unoptimized />
              <p className="text-sm text-gray-600">Escaneie com o WhatsApp no aparelho principal.</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 py-8 text-center text-gray-500">
              <MessageCircle className="h-10 w-10" />
              <p>Sem QR Code pendente no momento.</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary-600" />
            Governanca de personas
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>Fabio:</strong> decisor e operador.
          </p>
          <p>
            <strong>VIVA:</strong> assistente interna para dados/agenda/campanhas.
          </p>
          <p>
            <strong>Viviane:</strong> atendimento externo WhatsApp via handoff.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { MessageCircle, QrCode, RefreshCw } from 'lucide-react'

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

export default function WhatsAppPage() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [statusData, setStatusData] = useState<WhatsAppStatus | null>(null)
  const [qrCode, setQrCode] = useState<string | null>(null)

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

  useEffect(() => {
    const run = async () => {
      await carregarStatus()
      setLoading(false)
    }
    run()
  }, [carregarStatus])

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
      await carregarStatus()
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
      await carregarStatus()
    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Erro ao desconectar WhatsApp'
      toast({ title: 'Erro ao desconectar', description: String(detail), variant: 'destructive' })
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-primary-600" />
      </div>
    )
  }

  const conectado = Boolean(statusData?.conectado)

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">WhatsApp</h1>
        <p className="mt-1 text-sm text-gray-600">Conexao institucional com Evolution API</p>
      </header>

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
            <Button variant="ghost" onClick={carregarStatus} disabled={actionLoading}>
              Atualizar status
            </Button>
          </div>
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
              <img src={qrSrc} alt="QR Code WhatsApp" className="h-72 w-72 rounded-lg border bg-white p-2" />
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
    </div>
  )
}

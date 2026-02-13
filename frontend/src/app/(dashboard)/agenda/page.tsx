'use client'

import { FormEvent, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { CalendarPlus, CheckCircle2, Link2, Loader2, RefreshCw, Trash2, Unlink } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { agendaApi, googleCalendarApi } from '@/lib/api'

interface Evento {
  id: string
  titulo: string
  descricao?: string | null
  tipo: 'reuniao' | 'ligacao' | 'prazo' | 'outro'
  data_inicio: string
  concluido: boolean
}

interface GoogleCalendarStatus {
  configured: boolean
  connected: boolean
  calendar_id?: string | null
  scope?: string | null
  expires_at?: string | null
}

const formInicial = {
  titulo: '',
  descricao: '',
  tipo: 'outro',
  data_inicio: '',
}

const tipoLabel: Record<string, string> = {
  reuniao: 'Reuniao',
  ligacao: 'Ligacao',
  prazo: 'Prazo',
  outro: 'Outro',
}

export default function AgendaPage() {
  const searchParams = useSearchParams()
  const [eventos, setEventos] = useState<Evento[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(true)
  const [googleActionLoading, setGoogleActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [form, setForm] = useState(formInicial)
  const [googleStatus, setGoogleStatus] = useState<GoogleCalendarStatus>({
    configured: false,
    connected: false,
  })

  const loadEventos = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await agendaApi.getAll()
      setEventos(Array.isArray(response?.items) ? response.items : [])
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao carregar agenda.')
    } finally {
      setLoading(false)
    }
  }

  const loadGoogleStatus = async () => {
    setGoogleLoading(true)
    try {
      const status = await googleCalendarApi.getStatus()
      setGoogleStatus({
        configured: Boolean(status?.configured),
        connected: Boolean(status?.connected),
        calendar_id: status?.calendar_id ?? null,
        scope: status?.scope ?? null,
        expires_at: status?.expires_at ?? null,
      })
    } catch {
      setGoogleStatus({
        configured: false,
        connected: false,
      })
    } finally {
      setGoogleLoading(false)
    }
  }

  useEffect(() => {
    void loadEventos()
    void loadGoogleStatus()
  }, [])

  useEffect(() => {
    const googleStatusParam = searchParams.get('google_calendar')
    if (!googleStatusParam) return

    if (googleStatusParam === 'connected') {
      setNotice('Google Calendar conectado com sucesso.')
      setError('')
      void loadGoogleStatus()
      return
    }

    if (googleStatusParam === 'error') {
      const detail = searchParams.get('detail')
      const decoded = detail
        ? decodeURIComponent(detail.replace(/\+/g, ' '))
        : 'Falha ao conectar Google Calendar.'
      setError(decoded)
      setNotice('')
      void loadGoogleStatus()
    }
  }, [searchParams])

  const handleGoogleConnect = async () => {
    setGoogleActionLoading(true)
    setError('')
    setNotice('')
    try {
      const data = await googleCalendarApi.getConnectUrl()
      const url = String(data?.url || '')
      if (!url) {
        throw new Error('URL de conexao invalida.')
      }
      window.location.href = url
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Falha ao iniciar conexao com Google Calendar.')
    } finally {
      setGoogleActionLoading(false)
    }
  }

  const handleGoogleDisconnect = async () => {
    setGoogleActionLoading(true)
    setError('')
    setNotice('')
    try {
      await googleCalendarApi.disconnect()
      setNotice('Google Calendar desconectado com sucesso.')
      await loadGoogleStatus()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao desconectar Google Calendar.')
    } finally {
      setGoogleActionLoading(false)
    }
  }

  const handleSyncEventoGoogle = async (id: string) => {
    setError('')
    setNotice('')
    try {
      const result = await googleCalendarApi.syncAgendaEvent(id)
      if (result?.synced) {
        setNotice('Compromisso sincronizado com Google Calendar.')
      } else {
        setNotice(`Sincronizacao nao executada: ${String(result?.reason || 'sem motivo informado')}.`)
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao sincronizar compromisso com Google Calendar.')
    }
  }

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    setNotice('')
    try {
      await agendaApi.create({
        titulo: form.titulo,
        descricao: form.descricao || null,
        tipo: form.tipo,
        data_inicio: new Date(form.data_inicio).toISOString(),
        data_fim: null,
        cliente_id: null,
        contrato_id: null,
      })
      setForm(formInicial)
      setNotice('Compromisso criado com sucesso.')
      await loadEventos()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao criar compromisso.')
    } finally {
      setSaving(false)
    }
  }

  const handleConcluir = async (id: string) => {
    try {
      await agendaApi.conclude(id)
      await loadEventos()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao concluir compromisso.')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await agendaApi.delete(id)
      await loadEventos()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao excluir compromisso.')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Agenda</h1>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6 text-sm text-red-700">{error}</CardContent>
        </Card>
      )}

      {notice && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6 text-sm text-green-700">{notice}</CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Integracao Google Calendar</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {googleLoading ? (
            <div className="flex items-center text-sm text-gray-500">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Verificando conexao Google Calendar...
            </div>
          ) : (
            <>
              {!googleStatus.configured ? (
                <p className="text-sm text-amber-700">
                  Google Calendar ainda nao configurado no backend (faltam credenciais OAuth).
                </p>
              ) : googleStatus.connected ? (
                <div className="space-y-1 text-sm text-gray-700">
                  <p>Conectado: sim</p>
                  <p>Calendario: {googleStatus.calendar_id || 'primary'}</p>
                  {googleStatus.expires_at && (
                    <p>Token expira em: {new Date(googleStatus.expires_at).toLocaleString('pt-BR')}</p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-700">Conectado: nao</p>
              )}
            </>
          )}

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleGoogleConnect}
              disabled={googleLoading || googleActionLoading || !googleStatus.configured}
            >
              <Link2 className="mr-2 h-4 w-4" />
              Conectar Google
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleGoogleDisconnect}
              disabled={googleLoading || googleActionLoading || !googleStatus.connected}
            >
              <Unlink className="mr-2 h-4 w-4" />
              Desconectar
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Novo compromisso</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 md:grid-cols-2" onSubmit={handleCreate}>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="titulo">Titulo</Label>
              <Input
                id="titulo"
                required
                value={form.titulo}
                onChange={(event) => setForm((prev) => ({ ...prev, titulo: event.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="tipo">Tipo</Label>
              <select
                id="tipo"
                className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.tipo}
                onChange={(event) => setForm((prev) => ({ ...prev, tipo: event.target.value }))}
              >
                <option value="outro">Outro</option>
                <option value="reuniao">Reuniao</option>
                <option value="ligacao">Ligacao</option>
                <option value="prazo">Prazo</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_inicio">Data e hora</Label>
              <Input
                id="data_inicio"
                type="datetime-local"
                required
                value={form.data_inicio}
                onChange={(event) => setForm((prev) => ({ ...prev, data_inicio: event.target.value }))}
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="descricao">Descricao</Label>
              <textarea
                id="descricao"
                className="min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.descricao}
                onChange={(event) => setForm((prev) => ({ ...prev, descricao: event.target.value }))}
              />
            </div>

            <div className="md:col-span-2 flex justify-end">
              <Button type="submit" disabled={saving}>
                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CalendarPlus className="mr-2 h-4 w-4" />}
                Salvar compromisso
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Compromissos</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Carregando agenda...
            </div>
          ) : eventos.length === 0 ? (
            <div className="py-8 text-center text-gray-500">Nenhum compromisso agendado.</div>
          ) : (
            <div className="space-y-3">
              {eventos.map((evento) => (
                <div key={evento.id} className="rounded-lg border p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-gray-900">{evento.titulo}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(evento.data_inicio).toLocaleString('pt-BR')}
                      </p>
                      {evento.descricao && (
                        <p className="mt-1 text-sm text-gray-600">{evento.descricao}</p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{tipoLabel[evento.tipo] || 'Outro'}</Badge>
                      {evento.concluido ? (
                        <Badge className="bg-green-600">Concluido</Badge>
                      ) : (
                        <Badge className="bg-yellow-500">Pendente</Badge>
                      )}
                    </div>
                  </div>

                  <div className="mt-3 flex justify-end gap-2">
                    {googleStatus.connected && (
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => handleSyncEventoGoogle(evento.id)}
                      >
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Sincronizar Google
                      </Button>
                    )}
                    {!evento.concluido && (
                      <Button type="button" variant="outline" onClick={() => handleConcluir(evento.id)}>
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Concluir
                      </Button>
                    )}
                    <Button type="button" variant="outline" onClick={() => handleDelete(evento.id)}>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Excluir
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

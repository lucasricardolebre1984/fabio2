'use client'

import { Suspense, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { CalendarDays, Download, Megaphone, RefreshCw, X } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'

type CampanhaModo = 'FC' | 'REZETA'

interface CampanhaItem {
  id: string
  modo: CampanhaModo
  titulo: string
  briefing?: string | null
  mensagem_original?: string | null
  image_url: string
  overlay: {
    headline?: string
    subheadline?: string
    cta?: string
    [key: string]: unknown
  }
  meta: Record<string, unknown>
  created_at: string
}

interface CampanhaListResponse {
  items: CampanhaItem[]
  total: number
}

const modoLabel: Record<CampanhaModo, string> = {
  FC: 'FC Solucoes',
  REZETA: 'RezetaBrasil',
}

function CampanhasPageContent() {
  const searchParams = useSearchParams()
  const selectedId = searchParams.get('id')

  const [modo, setModo] = useState<'ALL' | CampanhaModo>('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<CampanhaItem[]>([])
  const [total, setTotal] = useState(0)
  const [imagemAtiva, setImagemAtiva] = useState<CampanhaItem | null>(null)

  const baixarImagem = (item: CampanhaItem) => {
    const link = document.createElement('a')
    link.href = item.image_url
    link.download = `${(item.titulo || 'campanha').replace(/[^a-zA-Z0-9-_]/g, '_')}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const params = useMemo(() => {
    if (modo === 'ALL') return { limit: 80 }
    return { modo, limit: 80 }
  }, [modo])

  const loadCampanhas = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get<CampanhaListResponse>('/viva/campanhas', { params })
      setItems(response.data.items || [])
      setTotal(response.data.total || 0)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao carregar campanhas.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCampanhas()
  }, [modo])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campanhas IA</h1>
          <p className="text-gray-500">
            Historico de criativos gerados pela VIVA e salvos automaticamente.
          </p>
        </div>
        <Button variant="outline" onClick={loadCampanhas} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant={modo === 'ALL' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setModo('ALL')}
        >
          Todas
        </Button>
        <Button
          variant={modo === 'FC' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setModo('FC')}
        >
          FC
        </Button>
        <Button
          variant={modo === 'REZETA' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setModo('REZETA')}
        >
          Rezeta
        </Button>
        <span className="ml-2 text-sm text-gray-500">Total: {total}</span>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">{error}</div>
      )}

      {loading ? (
        <div className="rounded-xl border bg-white p-6 text-gray-500">Carregando campanhas...</div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border bg-white p-10 text-center">
          <Megaphone className="mx-auto mb-3 h-10 w-10 text-gray-300" />
          <p className="text-gray-600">Nenhuma campanha salva ainda.</p>
          <p className="text-sm text-gray-400">Gere uma imagem no menu Imagens FC ou Imagens Rezeta na VIVA.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => {
            const isSelected = selectedId === item.id
            return (
              <article
                key={item.id}
                className={`overflow-hidden rounded-xl border bg-white shadow-sm ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
              >
                <div className="relative aspect-square bg-gray-100">
                  <img
                    src={item.image_url}
                    alt={item.titulo}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="space-y-2 p-4">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        item.modo === 'FC' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {modoLabel[item.modo]}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gray-500">
                      <CalendarDays className="h-3 w-3" />
                      {new Date(item.created_at).toLocaleString('pt-BR')}
                    </span>
                  </div>

                  <h2 className="line-clamp-2 text-sm font-semibold text-gray-900">{item.titulo}</h2>

                  {item.overlay?.subheadline && (
                    <p className="line-clamp-2 text-sm text-gray-600">{item.overlay.subheadline}</p>
                  )}

                  {item.briefing && (
                    <p className="line-clamp-3 text-xs text-gray-500">{item.briefing}</p>
                  )}

                  <div className="flex items-center justify-end gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setImagemAtiva(item)}
                    >
                      <Download className="mr-1 h-3 w-3" />
                      Abrir imagem
                    </Button>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      )}

      {imagemAtiva && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setImagemAtiva(null)}
        >
          <div
            className="relative w-full max-w-5xl rounded-lg bg-white p-3 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setImagemAtiva(null)}
              className="absolute right-3 top-3 rounded-md p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              aria-label="Fechar"
            >
              <X className="h-5 w-5" />
            </button>
            <img
              src={imagemAtiva.image_url}
              alt={imagemAtiva.titulo}
              className="mx-auto max-h-[80vh] w-auto max-w-full rounded-md object-contain"
            />
            <div className="mt-3 flex justify-end">
              <Button size="sm" onClick={() => baixarImagem(imagemAtiva)}>
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function CampanhasPage() {
  return (
    <Suspense
      fallback={
        <div className="rounded-xl border bg-white p-6 text-gray-500">Carregando campanhas...</div>
      }
    >
      <CampanhasPageContent />
    </Suspense>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Plus, 
  Upload, 
  Image as ImageIcon, 
  CheckCircle, 
  Trash2, 
  Filter,
  Grid3X3,
  List
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { toast } from 'sonner'
import { api } from '@/lib/api'

interface Imagem {
  id: string
  nome: string
  descricao?: string
  url: string
  tipo: 'gerada' | 'upload'
  formato: '1:1' | '16:9' | '9:16'
  status: 'rascunho' | 'aprovada'
  prompt?: string
  created_at: string
}

export default function ImagensPage() {
  const router = useRouter()
  const [imagens, setImagens] = useState<Imagem[]>([])
  const [loading, setLoading] = useState(true)
  const [filtroStatus, setFiltroStatus] = useState<string>('todas')
  const [filtroTipo, setFiltroTipo] = useState<string>('todas')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  useEffect(() => {
    carregarImagens()
  }, [filtroStatus, filtroTipo])

  const carregarImagens = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filtroStatus !== 'todas') params.append('status', filtroStatus)
      if (filtroTipo !== 'todas') params.append('tipo', filtroTipo)
      
      const response = await api.get(`/imagens?${params}`)
      setImagens(response.data.items || [])
    } catch (error) {
      console.error('Erro ao carregar imagens:', error)
      toast.error('Erro ao carregar imagens')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta imagem?')) return
    
    try {
      await api.delete(`/imagens/${id}`)
      toast.success('Imagem excluída com sucesso')
      carregarImagens()
    } catch (error) {
      console.error('Erro ao excluir:', error)
      toast.error('Erro ao excluir imagem')
    }
  }

  const handleAprovar = async (id: string) => {
    try {
      await api.post(`/imagens/${id}/aprovar`)
      toast.success('Imagem aprovada e movida para campanhas')
      carregarImagens()
    } catch (error) {
      console.error('Erro ao aprovar:', error)
      toast.error('Erro ao aprovar imagem')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getImageUrl = (url: string) => {
    // Remove 'storage/' prefix if present and add proper path
    const cleanUrl = url.replace(/^storage\//, '')
    return `http://localhost:8000/storage/${cleanUrl}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Imagens</h1>
          <p className="text-gray-500 mt-1">
            Gerencie imagens para campanhas de marketing
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => router.push('/imagens/upload')}
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload
          </Button>
          <Button
            onClick={() => router.push('/imagens/gerar')}
          >
            <Plus className="w-4 h-4 mr-2" />
            Gerar com IA
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 bg-white p-4 rounded-lg border">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-500">Filtros:</span>
        </div>
        
        <Select value={filtroStatus} onValueChange={setFiltroStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todas">Todos status</SelectItem>
            <SelectItem value="rascunho">Rascunho</SelectItem>
            <SelectItem value="aprovada">Aprovada</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filtroTipo} onValueChange={setFiltroTipo}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todas">Todos tipos</SelectItem>
            <SelectItem value="gerada">Gerada por IA</SelectItem>
            <SelectItem value="upload">Upload</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex-1" />

        <div className="flex gap-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('grid')}
          >
            <Grid3X3 className="w-4 h-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('list')}
          >
            <List className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="todas" className="w-full">
        <TabsList>
          <TabsTrigger value="todas">Todas</TabsTrigger>
          <TabsTrigger value="geradas">Geradas por IA</TabsTrigger>
          <TabsTrigger value="uploads">Uploads</TabsTrigger>
          <TabsTrigger value="campanhas">Campanhas</TabsTrigger>
        </TabsList>

        <TabsContent value="todas" className="mt-6">
          {renderContent()}
        </TabsContent>
        <TabsContent value="geradas" className="mt-6">
          {renderContent('gerada')}
        </TabsContent>
        <TabsContent value="uploads" className="mt-6">
          {renderContent('upload')}
        </TabsContent>
        <TabsContent value="campanhas" className="mt-6">
          {renderContent(undefined, 'aprovada')}
        </TabsContent>
      </Tabs>
    </div>
  )

  function renderContent(filterTipo?: string, filterStatus?: string) {
    let filteredImages = imagens
    
    if (filterTipo) {
      filteredImages = filteredImages.filter(img => img.tipo === filterTipo)
    }
    if (filterStatus) {
      filteredImages = filteredImages.filter(img => img.status === filterStatus)
    }

    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
        </div>
      )
    }

    if (filteredImages.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <ImageIcon className="w-12 h-12 mb-4 opacity-50" />
          <p>Nenhuma imagem encontrada</p>
          <p className="text-sm mt-1">
            Gere uma imagem com IA ou faça upload de um arquivo
          </p>
        </div>
      )
    }

    if (viewMode === 'grid') {
      return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredImages.map((imagem) => (
            <Card key={imagem.id} className="overflow-hidden group">
              <div className="aspect-square relative bg-gray-100">
                <img
                  src={getImageUrl(imagem.url)}
                  alt={imagem.nome}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="%23f3f4f6" width="100" height="100"/><text fill="%239ca3af" x="50" y="50" text-anchor="middle">Imagem</text></svg>'
                  }}
                />
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  {imagem.status === 'rascunho' && (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleAprovar(imagem.id)}
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Aprovar
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(imagem.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                {imagem.status === 'aprovada' && (
                  <div className="absolute top-2 right-2">
                    <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                      Campanha
                    </span>
                  </div>
                )}
              </div>
              <CardContent className="p-3">
                <h3 className="font-medium text-sm truncate">{imagem.nome}</h3>
                <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                  <span className={imagem.tipo === 'gerada' ? 'text-purple-600' : 'text-blue-600'}>
                    {imagem.tipo === 'gerada' ? 'IA' : 'Upload'}
                  </span>
                  <span>{imagem.formato}</span>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  {formatDate(imagem.created_at)}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )
    }

    return (
      <div className="space-y-2">
        {filteredImages.map((imagem) => (
          <div
            key={imagem.id}
            className="flex items-center gap-4 p-4 bg-white rounded-lg border hover:shadow-md transition-shadow"
          >
            <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
              <img
                src={getImageUrl(imagem.url)}
                alt={imagem.nome}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-medium truncate">{imagem.nome}</h3>
              <p className="text-sm text-gray-500">
                {imagem.tipo === 'gerada' ? 'Gerada por IA' : 'Upload manual'} • {imagem.formato}
              </p>
              <p className="text-xs text-gray-400">
                {formatDate(imagem.created_at)}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {imagem.status === 'aprovada' ? (
                <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
                  Campanha
                </span>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAprovar(imagem.id)}
                >
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Aprovar
                </Button>
              )}
              <Button
                size="sm"
                variant="destructive"
                onClick={() => handleDelete(imagem.id)}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    )
  }
}

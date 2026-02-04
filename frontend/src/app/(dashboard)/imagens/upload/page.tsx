'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Upload, X, Image as ImageIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { toast } from 'sonner'
import { api } from '@/lib/api'

export default function UploadImagemPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    nome: '',
    formato: '1:1',
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      toast.error('Formato não suportado. Use: JPG, PNG ou WebP')
      return
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Arquivo muito grande. Máximo: 10MB')
      return
    }

    setSelectedFile(file)
    setPreview(URL.createObjectURL(file))
    
    // Auto-fill name from filename
    if (!formData.nome) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
      setFormData(prev => ({ ...prev, nome: nameWithoutExt }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedFile) {
      toast.error('Selecione um arquivo')
      return
    }

    if (!formData.nome.trim()) {
      toast.error('Digite um nome para a imagem')
      return
    }

    try {
      setLoading(true)
      
      const data = new FormData()
      data.append('file', selectedFile)
      data.append('nome', formData.nome)
      data.append('formato', formData.formato)

      const response = await api.post('/imagens/upload', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.success) {
        toast.success('Imagem enviada com sucesso!')
        router.push('/imagens')
      }
    } catch (error) {
      console.error('Erro ao fazer upload:', error)
      toast.error('Erro ao enviar imagem. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const clearSelection = () => {
    setSelectedFile(null)
    setPreview(null)
    if (preview) {
      URL.revokeObjectURL(preview)
    }
  }

  const formatos = [
    { value: '1:1', label: 'Quadrado (1:1) - Feed Instagram' },
    { value: '16:9', label: 'Paisagem (16:9) - Banner/Story' },
    { value: '9:16', label: 'Retrato (9:16) - Story Vertical' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => router.push('/imagens')}
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Upload de Imagem</h1>
          <p className="text-gray-500 mt-1">
            Faça upload de imagens do seu computador
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Selecionar Arquivo</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* File Upload Area */}
              <div className="space-y-2">
                <Label>Arquivo *</Label>
                <div 
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
                  onClick={() => document.getElementById('file-input')?.click()}
                >
                  {preview ? (
                    <div className="relative">
                      <img
                        src={preview}
                        alt="Preview"
                        className="max-h-48 mx-auto rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          clearSelection()
                        }}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                      <p className="text-gray-600 font-medium">
                        Clique para selecionar ou arraste aqui
                      </p>
                      <p className="text-sm text-gray-400 mt-1">
                        JPG, PNG ou WebP (máx. 10MB)
                      </p>
                    </>
                  )}
                  <input
                    id="file-input"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="nome">Nome da Imagem *</Label>
                <Input
                  id="nome"
                  placeholder="Ex: Logo Campanha 2026"
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="formato">Formato</Label>
                <Select
                  value={formData.formato}
                  onValueChange={(value) => setFormData({ ...formData, formato: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {formatos.map((f) => (
                      <SelectItem key={f.value} value={f.value}>
                        {f.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="pt-4">
                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading || !selectedFile}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 mr-2 animate-spin rounded-full border-b-2 border-white" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Fazer Upload
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>Dicas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <ImageIcon className="w-5 h-5 text-primary-500 mt-0.5" />
              <div>
                <h4 className="font-medium">Formatos Suportados</h4>
                <p className="text-sm text-gray-500">
                  JPG, PNG e WebP. Recomendamos WebP para melhor qualidade e tamanho.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-500 text-white text-xs flex items-center justify-center mt-0.5">
                1:1
              </div>
              <div>
                <h4 className="font-medium">Formato Quadrado (1:1)</h4>
                <p className="text-sm text-gray-500">
                  Ideal para feed do Instagram e posts em geral.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-500 text-white text-xs flex items-center justify-center mt-0.5">
                16:9
              </div>
              <div>
                <h4 className="font-medium">Formato Paisagem (16:9)</h4>
                <p className="text-sm text-gray-500">
                  Ideal para banners, capas e stories horizontais.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-primary-500 text-white text-xs flex items-center justify-center mt-0.5">
                9:16
              </div>
              <div>
                <h4 className="font-medium">Formato Retrato (9:16)</h4>
                <p className="text-sm text-gray-500">
                  Ideal para stories verticais do Instagram e WhatsApp.
                </p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
              <h4 className="font-medium text-blue-900">Workflow Recomendado</h4>
              <ol className="text-sm text-blue-700 mt-2 space-y-1 list-decimal list-inside">
                <li>Faça upload ou gere a imagem</li>
                <li>Visualize na galeria</li>
                <li>Aprove para campanha quando estiver pronta</li>
                <li>Use em seus materiais de marketing</li>
              </ol>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

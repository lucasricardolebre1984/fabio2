'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Wand2, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { toast } from 'sonner'
import { api } from '@/lib/api'

export default function GerarImagemPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [generatedImage, setGeneratedImage] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    nome: '',
    prompt: '',
    formato: '1:1',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.prompt.trim()) {
      toast.error('Digite um prompt para gerar a imagem')
      return
    }

    try {
      setLoading(true)
      const response = await api.post('/imagens/gerar', {
        prompt: formData.prompt,
        formato: formData.formato,
        nome: formData.nome || undefined,
      })

      if (response.data.success) {
        setGeneratedImage(response.data.imagem.url)
        toast.success('Imagem gerada com sucesso!')
      }
    } catch (error) {
      console.error('Erro ao gerar imagem:', error)
      toast.error('Erro ao gerar imagem. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const formatos = [
    { value: '1:1', label: 'Quadrado (1:1) - Feed Instagram', dimensions: '1024x1024' },
    { value: '16:9', label: 'Paisagem (16:9) - Banner/Story', dimensions: '1024x576' },
    { value: '9:16', label: 'Retrato (9:16) - Story Vertical', dimensions: '576x1024' },
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
          <h1 className="text-2xl font-bold text-gray-900">Gerar Imagem com IA</h1>
          <p className="text-gray-500 mt-1">
            Use a IA HuggingFace para criar imagens profissionais
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Configurações</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome da Imagem (opcional)</Label>
                <Input
                  id="nome"
                  placeholder="Ex: Campanha Fevereiro 2026"
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="prompt">Prompt *</Label>
                <Textarea
                  id="prompt"
                  placeholder="Descreva a imagem que você quer gerar. Ex: Professional business flyer for financial services, clean design, blue colors, modern office background..."
                  value={formData.prompt}
                  onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                  rows={6}
                  required
                />
                <p className="text-xs text-gray-500">
                  Seja específico sobre o estilo, cores, composição e elementos visuais.
                </p>
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
                        {f.label} ({f.dimensions})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="pt-4">
                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Gerando imagem... (30-60s)
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4 mr-2" />
                      Gerar Imagem
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Preview */}
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            {generatedImage ? (
              <div className="space-y-4">
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={`http://localhost:8000/storage/${generatedImage}`}
                    alt="Imagem gerada"
                    className="w-full h-full object-contain"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => router.push('/imagens')}
                  >
                    Ver na Galeria
                  </Button>
                  <Button
                    className="flex-1"
                    onClick={() => setGeneratedImage(null)}
                  >
                    Gerar Outra
                  </Button>
                </div>
              </div>
            ) : (
              <div className="aspect-square bg-gray-50 rounded-lg flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <Wand2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>A imagem gerada aparecerá aqui</p>
                  <p className="text-sm mt-1">
                    Preencha o prompt e clique em Gerar
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

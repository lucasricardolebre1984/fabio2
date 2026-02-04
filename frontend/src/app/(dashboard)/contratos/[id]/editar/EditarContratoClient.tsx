'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import { contratosApi } from '@/lib/api'
import { formatCurrency, formatCPF } from '@/lib/utils'
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
}

export default function EditarContratoClient() {
  const params = useParams()
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [contrato, setContrato] = useState<Contrato | null>(null)
  const [formData, setFormData] = useState<Partial<Contrato>>({})

  useEffect(() => {
    carregarContrato()
  }, [])

  const carregarContrato = async () => {
    try {
      const id = params.id as string
      const data = await contratosApi.getById(id)
      setContrato(data)
      setFormData({
        contratante_nome: data.contratante_nome,
        contratante_email: data.contratante_email,
        contratante_telefone: data.contratante_telefone || '',
        contratante_endereco: data.contratante_endereco,
        valor_total: data.valor_total,
        valor_entrada: data.valor_entrada,
        qtd_parcelas: data.qtd_parcelas,
        valor_parcela: data.valor_parcela,
        prazo_1: data.prazo_1,
        prazo_2: data.prazo_2,
        local_assinatura: data.local_assinatura,
        data_assinatura: data.data_assinatura,
      })
    } catch (error) {
      toast.error('Erro ao carregar contrato')
      router.push('/contratos/lista')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      const id = params.id as string
      await contratosApi.update(id, formData)
      toast.success('Contrato atualizado com sucesso!')
      router.push(`/contratos/${id}`)
    } catch (error: any) {
      toast.error('Erro ao atualizar contrato: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#627d98]"></div>
      </div>
    )
  }

  if (!contrato) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>Contrato não encontrado</p>
        <Button 
          variant="outline" 
          className="mt-4"
          onClick={() => router.push('/contratos/lista')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => router.push(`/contratos/${contrato.id}`)}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Editar Contrato
          </h1>
          <p className="text-sm text-gray-500">
            {contrato.numero} - {contrato.template_nome}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Dados do Cliente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome Completo</Label>
                <Input
                  id="nome"
                  value={formData.contratante_nome || ''}
                  onChange={(e) => handleChange('contratante_nome', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cpf">CPF</Label>
                <Input
                  id="cpf"
                  value={formatCPF(contrato.contratante_documento)}
                  disabled
                  className="bg-gray-50"
                />
                <p className="text-xs text-gray-500">CPF não pode ser alterado</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.contratante_email || ''}
                  onChange={(e) => handleChange('contratante_email', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="telefone">Telefone</Label>
                <Input
                  id="telefone"
                  value={formData.contratante_telefone || ''}
                  onChange={(e) => handleChange('contratante_telefone', e.target.value)}
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="endereco">Endereço Completo</Label>
                <Input
                  id="endereco"
                  value={formData.contratante_endereco || ''}
                  onChange={(e) => handleChange('contratante_endereco', e.target.value)}
                  required
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Dados Financeiros</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="valor_total">Valor Total</Label>
                <Input
                  id="valor_total"
                  type="number"
                  step="0.01"
                  value={formData.valor_total || ''}
                  onChange={(e) => handleChange('valor_total', parseFloat(e.target.value))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="valor_entrada">Valor Entrada</Label>
                <Input
                  id="valor_entrada"
                  type="number"
                  step="0.01"
                  value={formData.valor_entrada || ''}
                  onChange={(e) => handleChange('valor_entrada', parseFloat(e.target.value))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="qtd_parcelas">Quantidade de Parcelas</Label>
                <Input
                  id="qtd_parcelas"
                  type="number"
                  min="1"
                  max="99"
                  value={formData.qtd_parcelas || ''}
                  onChange={(e) => handleChange('qtd_parcelas', parseInt(e.target.value))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="valor_parcela">Valor da Parcela</Label>
                <Input
                  id="valor_parcela"
                  type="number"
                  step="0.01"
                  value={formData.valor_parcela || ''}
                  onChange={(e) => handleChange('valor_parcela', parseFloat(e.target.value))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prazo_1">Prazo Mínimo (dias)</Label>
                <Input
                  id="prazo_1"
                  type="number"
                  value={formData.prazo_1 || ''}
                  onChange={(e) => handleChange('prazo_1', parseInt(e.target.value))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prazo_2">Prazo Máximo (dias)</Label>
                <Input
                  id="prazo_2"
                  type="number"
                  value={formData.prazo_2 || ''}
                  onChange={(e) => handleChange('prazo_2', parseInt(e.target.value))}
                  required
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Dados da Assinatura</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="local_assinatura">Local</Label>
                <Input
                  id="local_assinatura"
                  value={formData.local_assinatura || ''}
                  onChange={(e) => handleChange('local_assinatura', e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="data_assinatura">Data</Label>
                <Input
                  id="data_assinatura"
                  value={formData.data_assinatura || ''}
                  onChange={(e) => handleChange('data_assinatura', e.target.value)}
                  required
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Button 
            type="button"
            variant="outline"
            onClick={() => router.push(`/contratos/${contrato.id}`)}
          >
            Cancelar
          </Button>
          <Button 
            type="submit"
            disabled={saving}
            className="bg-[#627d98] hover:bg-[#4a6078]"
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Salvando...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Salvar Alterações
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}

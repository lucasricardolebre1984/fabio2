'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'

export default function NovoContratoPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [checkingCliente, setCheckingCliente] = useState(false)
  const [error, setError] = useState('')
  const [clienteHint, setClienteHint] = useState('')
  
  // Form state
  const [formData, setFormData] = useState({
    contratante_nome: '',
    contratante_documento: '',
    contratante_email: '',
    contratante_telefone: '',
    contratante_endereco: '',
    valor_total: '',
    valor_entrada: '',
    qtd_parcelas: '',
    prazo_1: '',
    prazo_2: '',
    local_assinatura: 'Ribeirão Preto/SP',
    data_assinatura: new Date().toLocaleDateString('pt-BR'),
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target
    if (id === 'contratante_documento') {
      setClienteHint('')
    }
    setFormData(prev => ({ ...prev, [id]: value }))
  }

  const normalizeDocument = (value: string) => {
    return (value || '').replace(/\D/g, '')
  }

  const buscarClientePorDocumento = async () => {
    const documento = normalizeDocument(formData.contratante_documento)
    if (documento.length < 11) return

    setCheckingCliente(true)
    setClienteHint('')
    setError('')

    try {
      const response = await api.get(`/clientes/documento/${documento}`)
      const cliente = response.data

      setFormData(prev => ({
        ...prev,
        contratante_nome: cliente?.nome || prev.contratante_nome,
        contratante_email: cliente?.email || prev.contratante_email,
        contratante_telefone: cliente?.telefone || prev.contratante_telefone,
        contratante_endereco: cliente?.endereco || prev.contratante_endereco,
      }))
      setClienteHint('Cliente existente encontrado. Dados preenchidos automaticamente.')
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setClienteHint('Documento sem cadastro previo. O cliente sera criado junto com o contrato.')
      } else {
        setError(err?.response?.data?.detail || 'Falha ao buscar cliente por documento.')
      }
    } finally {
      setCheckingCliente(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const contratoData = {
        template_id: 'bacen',
        contratante_nome: formData.contratante_nome,
        contratante_documento: formData.contratante_documento,
        contratante_email: formData.contratante_email,
        contratante_telefone: formData.contratante_telefone,
        contratante_endereco: formData.contratante_endereco,
        valor_total: parseFloat(formData.valor_total),
        valor_entrada: parseFloat(formData.valor_entrada) || 0,
        qtd_parcelas: parseInt(formData.qtd_parcelas),
        valor_parcela: 0,
        prazo_1: parseInt(formData.prazo_1),
        prazo_2: parseInt(formData.prazo_2),
        local_assinatura: formData.local_assinatura,
        data_assinatura: formData.data_assinatura,
        valor_total_extenso: null,
        valor_entrada_extenso: null,
        qtd_parcelas_extenso: null,
        valor_parcela_extenso: null,
        prazo_1_extenso: null,
        prazo_2_extenso: null,
      }

      console.log('Enviando dados:', contratoData)
      const response = await api.post('/contratos', contratoData)
      console.log('Sucesso:', response.data)
      alert('Contrato criado com sucesso!')
      router.push('/contratos')
    } catch (err: any) {
      console.error('Erro completo:', err)
      
      // Tratar diferentes tipos de erro
      let errorMessage = 'Erro ao criar contrato'
      
      if (err.response) {
        const { status, data } = err.response
        
        if (status === 422 && data?.detail) {
          // Erro de validação do Pydantic
          if (Array.isArray(data.detail)) {
            // Pydantic v2 retorna array de erros
            errorMessage = data.detail.map((e: any) => {
              const field = e.loc?.join('.') || 'campo'
              return `${field}: ${e.msg}`
            }).join(', ')
          } else if (typeof data.detail === 'string') {
            errorMessage = data.detail
          } else {
            errorMessage = JSON.stringify(data.detail)
          }
        } else if (data?.detail) {
          errorMessage = String(data.detail)
        } else if (data?.message) {
          errorMessage = String(data.message)
        } else {
          errorMessage = `Erro ${status}: ${JSON.stringify(data)}`
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-4 mb-8">
        <Link href="/contratos">
          <Button variant="outline" size="icon">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Novo Contrato</h1>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Contrato de Adesão ao Bacen</CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-lg text-sm">
              <strong>Erro:</strong> {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="contratante_nome">Nome do Cliente</Label>
              <Input 
                id="contratante_nome" 
                placeholder="Nome completo" 
                required 
                value={formData.contratante_nome}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="contratante_documento">CPF/CNPJ</Label>
              <Input 
                id="contratante_documento" 
                placeholder="000.000.000-00" 
                required 
                value={formData.contratante_documento}
                onChange={handleChange}
                onBlur={buscarClientePorDocumento}
              />
              {checkingCliente && (
                <p className="text-xs text-gray-500">Buscando cliente...</p>
              )}
              {!checkingCliente && clienteHint && (
                <p className="text-xs text-blue-700">{clienteHint}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contratante_email">Email</Label>
                <Input 
                  id="contratante_email" 
                  type="email"
                  placeholder="email@exemplo.com" 
                  required 
                  value={formData.contratante_email}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="contratante_telefone">Telefone</Label>
                <Input 
                  id="contratante_telefone" 
                  placeholder="(00) 00000-0000" 
                  value={formData.contratante_telefone}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="contratante_endereco">Endereço Completo</Label>
              <Input 
                id="contratante_endereco" 
                placeholder="Rua, número, bairro, cidade - Estado, CEP" 
                required 
                value={formData.contratante_endereco}
                onChange={handleChange}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="valor_total">Valor Total (R$)</Label>
                <Input 
                  id="valor_total" 
                  type="number" 
                  step="0.01" 
                  placeholder="0,00" 
                  required 
                  value={formData.valor_total}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="valor_entrada">Valor Entrada (R$)</Label>
                <Input 
                  id="valor_entrada" 
                  type="number" 
                  step="0.01" 
                  placeholder="0,00" 
                  value={formData.valor_entrada}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="qtd_parcelas">Qtd. Parcelas</Label>
                <Input 
                  id="qtd_parcelas" 
                  type="number" 
                  min={1} 
                  max={99}
                  placeholder="12" 
                  required 
                  value={formData.qtd_parcelas}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prazo_1">Prazo 1 (dias)</Label>
                <Input 
                  id="prazo_1" 
                  type="number" 
                  min={1}
                  placeholder="30" 
                  required 
                  value={formData.prazo_1}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prazo_2">Prazo 2 (dias)</Label>
                <Input 
                  id="prazo_2" 
                  type="number" 
                  min={1}
                  placeholder="60" 
                  required 
                  value={formData.prazo_2}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="flex justify-end pt-4 gap-4">
              <Link href="/contratos">
                <Button type="button" variant="outline">
                  Cancelar
                </Button>
              </Link>
              <Button type="submit" disabled={loading}>
                {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Criar Contrato
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

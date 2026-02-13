'use client'

import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'

const TEMPLATE_LABELS: Record<string, string> = {
  bacen: 'Contrato de Adesão ao Bacen',
  cadin: 'Instrumento de Prestação de Serviços - CADIN PF/PJ',
  cnh: 'Contrato de Prestação de Serviços - CNH Cassada e Recurso de Multas',
  aumento_score: 'Contrato de Prestação de Serviços - Aumento de Score',
  diagnostico360: 'Contrato de Prestação de Serviços - Diagnóstico 360',
  limpa_nome_standard: 'Contrato de Prestação de Serviços - Limpa Nome Standard',
  limpa_nome_express: 'Contrato de Prestação de Serviços - Limpa Nome Express',
  rating_convencional: 'Contrato de Prestação de Serviços - Execução de Rating',
  rating_express_pj: 'Contrato de Prestação de Serviços - Rating Express PJ',
  rating_full_pj: 'Contrato de Prestação de Serviços - Rating Full PJ',
  ccf: 'Contrato de Prestação de Serviços - Regularização CCF (Cheques sem Fundos)',
  certificado_digital: 'Contrato de Prestação de Serviços - Certificado Digital',
  remocao_proposta: 'Contrato de Prestação de Serviços - Remoção de Propostas Serasa',
  revisional: 'Contrato de Prestação de Serviços - Ação Revisional e Suspensão de Busca e Apreensão',
  jusbrasil: 'Contrato de Prestação de Serviços - Jusbrasil/Escavador',
}

const AVAILABLE_TEMPLATES = Object.keys(TEMPLATE_LABELS)

function NovoContratoPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const templateQuery = (searchParams.get('template') || 'bacen').toLowerCase()
  const selectedTemplate = AVAILABLE_TEMPLATES.includes(templateQuery) ? templateQuery : 'bacen'
  const tituloTemplate = TEMPLATE_LABELS[selectedTemplate] || TEMPLATE_LABELS.bacen

  const [loading, setLoading] = useState(false)
  const [checkingCliente, setCheckingCliente] = useState(false)
  const [error, setError] = useState('')
  const [clienteHint, setClienteHint] = useState('')

  const [formData, setFormData] = useState({
    contratante_nome: '',
    contratante_documento: '',
    cnh_numero: '',
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
    setFormData((prev) => ({ ...prev, [id]: value }))
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

      setFormData((prev) => ({
        ...prev,
        contratante_nome: cliente?.nome || prev.contratante_nome,
        contratante_email: cliente?.email || prev.contratante_email,
        contratante_telefone: cliente?.telefone || prev.contratante_telefone,
        contratante_endereco: cliente?.endereco || prev.contratante_endereco,
      }))
      setClienteHint('Cliente existente encontrado. Dados preenchidos automaticamente.')
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setClienteHint('Documento sem cadastro prévio. O cliente será criado junto com o contrato.')
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
        template_id: selectedTemplate,
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
        dados_extras:
          selectedTemplate === 'cadin'
            ? {
                forma_pagamento: `Entrada ${formData.valor_entrada || '0'} + ${formData.qtd_parcelas || '0'} parcelas`,
              }
            : selectedTemplate === 'cnh'
              ? {
                  cnh_numero: formData.cnh_numero || null,
                }
              : null,
      }

      await api.post('/contratos', contratoData)
      alert('Contrato criado com sucesso!')
      router.push('/contratos')
    } catch (err: any) {
      let errorMessage = 'Erro ao criar contrato'

      if (err.response) {
        const { status, data } = err.response

        if (status === 422 && data?.detail) {
          if (Array.isArray(data.detail)) {
            errorMessage = data.detail
              .map((item: any) => {
                const field = item.loc?.join('.') || 'campo'
                return `${field}: ${item.msg}`
              })
              .join(', ')
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
      <div className="mb-8 flex items-center gap-4">
        <Link href="/contratos">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Novo Contrato</h1>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>{tituloTemplate}</CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-600">
              <strong>Erro:</strong> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="contratante_nome">Nome do Cliente</Label>
              <Input id="contratante_nome" placeholder="Nome completo" required value={formData.contratante_nome} onChange={handleChange} />
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
              {checkingCliente && <p className="text-xs text-gray-500">Buscando cliente...</p>}
              {!checkingCliente && clienteHint && <p className="text-xs text-blue-700">{clienteHint}</p>}
            </div>

            {selectedTemplate === 'cnh' && (
              <div className="space-y-2">
                <Label htmlFor="cnh_numero">Número da CNH (opcional)</Label>
                <Input id="cnh_numero" placeholder="00000000000" value={formData.cnh_numero} onChange={handleChange} />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contratante_email">Email</Label>
                <Input id="contratante_email" type="email" placeholder="email@exemplo.com" required value={formData.contratante_email} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="contratante_telefone">Telefone</Label>
                <Input id="contratante_telefone" placeholder="(00) 00000-0000" value={formData.contratante_telefone} onChange={handleChange} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="contratante_endereco">Endereço Completo</Label>
              <Input id="contratante_endereco" placeholder="Rua, número, bairro, cidade - Estado, CEP" required value={formData.contratante_endereco} onChange={handleChange} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="valor_total">Valor Total (R$)</Label>
                <Input id="valor_total" type="number" step="0.01" placeholder="0,00" required value={formData.valor_total} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="valor_entrada">Valor Entrada (R$)</Label>
                <Input id="valor_entrada" type="number" step="0.01" placeholder="0,00" value={formData.valor_entrada} onChange={handleChange} />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="qtd_parcelas">Qtd. Parcelas</Label>
                <Input id="qtd_parcelas" type="number" min={1} max={99} placeholder="12" required value={formData.qtd_parcelas} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prazo_1">Prazo 1 (dias)</Label>
                <Input id="prazo_1" type="number" min={1} placeholder="30" required value={formData.prazo_1} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="prazo_2">Prazo 2 (dias)</Label>
                <Input id="prazo_2" type="number" min={1} placeholder="60" required value={formData.prazo_2} onChange={handleChange} />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <Link href="/contratos">
                <Button type="button" variant="outline">
                  Cancelar
                </Button>
              </Link>
              <Button type="submit" disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Criar Contrato
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default function NovoContratoPage() {
  return (
    <Suspense fallback={<div className="p-6 text-gray-500">Carregando formulário...</div>}>
      <NovoContratoPageContent />
    </Suspense>
  )
}

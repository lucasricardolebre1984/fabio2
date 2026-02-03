'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Plus, 
  FileText, 
  User, 
  Pencil, 
  Trash2, 
  Printer, 
  Eye, 
  ArrowLeft,
  Search
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

interface Contrato {
  id: string
  numero: string
  contratante_nome: string
  contratante_documento: string
  valor_total: number
  status: string
  created_at: string
  template_nome?: string
}

export default function ContratosListaPage() {
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadContratos()
  }, [])

  const loadContratos = async () => {
    try {
      const response = await api.get('/contratos')
      setContratos(response.data.items || [])
    } catch (err) {
      console.error('Erro ao carregar contratos:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este contrato?')) return
    
    try {
      await api.delete(`/contratos/${id}`)
      loadContratos()
    } catch (err: any) {
      alert('Erro ao excluir: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handlePrint = async (id: string) => {
    try {
      const response = await api.get(`/contratos/${id}/pdf`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `contrato-${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err: any) {
      console.error('Erro ao gerar PDF:', err)
      alert('Função PDF em desenvolvimento.')
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'rascunho': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'finalizado': return 'text-green-600 bg-green-50 border-green-200'
      case 'enviado': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'cancelado': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'rascunho': return 'Rascunho'
      case 'finalizado': return 'Finalizado'
      case 'enviado': return 'Enviado'
      case 'cancelado': return 'Cancelado'
      default: return status
    }
  }

  const filteredContratos = contratos.filter(c => 
    c.contratante_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.numero.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.contratante_documento.includes(searchTerm)
  )

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Link href="/contratos">
            <Button variant="outline" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Contratos Existentes</h1>
            <p className="text-gray-500 mt-1">
              Gerencie os contratos já cadastrados no sistema
            </p>
          </div>
        </div>
        <Link href="/contratos">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Novo Contrato
          </Button>
        </Link>
      </div>

      {/* Search */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Buscar por nome, número ou CPF..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Lista */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Contratos ({filteredContratos.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">
              Carregando contratos...
            </div>
          ) : filteredContratos.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                {searchTerm 
                  ? 'Nenhum contrato encontrado para esta busca.' 
                  : 'Nenhum contrato cadastrado ainda.'}
              </p>
              {!searchTerm && (
                <Link href="/contratos">
                  <Button className="mt-4">
                    <Plus className="w-4 h-4 mr-2" />
                    Criar Primeiro Contrato
                  </Button>
                </Link>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredContratos.map((contrato) => (
                <div
                  key={contrato.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-100 rounded-xl">
                      <FileText className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-900">
                          {contrato.numero}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full border ${getStatusColor(contrato.status)}`}>
                          {getStatusLabel(contrato.status)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <User className="w-4 h-4" />
                        {contrato.contratante_nome}
                      </div>
                      <div className="text-sm text-gray-400">
                        CPF: {contrato.contratante_documento}
                      </div>
                      {contrato.template_nome && (
                        <div className="text-xs text-blue-600 mt-1">
                          {contrato.template_nome}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className="font-semibold text-gray-900 text-lg">
                        {formatCurrency(contrato.valor_total)}
                      </div>
                      <div className="text-sm text-gray-400">
                        {formatDate(contrato.created_at)}
                      </div>
                    </div>
                    
                    {/* Ações */}
                    <div className="flex items-center gap-1">
                      <Link href={`/contratos/${contrato.id}`}>
                        <Button variant="ghost" size="icon" title="Ver detalhes">
                          <Eye className="w-4 h-4 text-gray-600" />
                        </Button>
                      </Link>
                      
                      <Link href={`/contratos/${contrato.id}/editar`}>
                        <Button variant="ghost" size="icon" title="Editar">
                          <Pencil className="w-4 h-4 text-blue-600" />
                        </Button>
                      </Link>
                      
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        title="Gerar PDF"
                        onClick={() => handlePrint(contrato.id)}
                      >
                        <Printer className="w-4 h-4 text-green-600" />
                      </Button>
                      
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        title="Excluir"
                        onClick={() => handleDelete(contrato.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
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

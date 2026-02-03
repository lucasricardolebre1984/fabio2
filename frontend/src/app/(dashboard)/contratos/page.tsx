'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Plus, FileText, User, Pencil, Trash2, Printer, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'

interface Contrato {
  id: string
  numero: string
  contratante_nome: string
  contratante_documento: string
  valor_total: number
  status: string
  created_at: string
}

export default function ContratosPage() {
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [loading, setLoading] = useState(true)

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
      
      // Criar URL do blob e baixar
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `contrato-${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err: any) {
      console.error('Erro ao gerar PDF:', err)
      alert('Função PDF em desenvolvimento. Verifique o console.')
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
      case 'rascunho': return 'text-yellow-600 bg-yellow-50'
      case 'finalizado': return 'text-green-600 bg-green-50'
      case 'enviado': return 'text-blue-600 bg-blue-50'
      case 'cancelado': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
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

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Contratos</h1>
        <Link href="/contratos/novo">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Novo Contrato
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Contratos</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">
              Carregando contratos...
            </div>
          ) : contratos.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Nenhum contrato encontrado. Clique em "Novo Contrato" para criar.
            </div>
          ) : (
            <div className="space-y-4">
              {contratos.map((contrato) => (
                <div
                  key={contrato.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">
                        {contrato.numero}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <User className="w-4 h-4" />
                        {contrato.contratante_nome}
                      </div>
                      <div className="text-sm text-gray-500">
                        CPF: {contrato.contratante_documento}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className="font-medium text-gray-900">
                        {formatCurrency(contrato.valor_total)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatDate(contrato.created_at)}
                      </div>
                      <span className={`inline-block px-2 py-1 text-xs rounded mt-1 ${getStatusColor(contrato.status)}`}>
                        {getStatusLabel(contrato.status)}
                      </span>
                    </div>
                    
                    {/* Botões de Ação */}
                    <div className="flex items-center gap-2">
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

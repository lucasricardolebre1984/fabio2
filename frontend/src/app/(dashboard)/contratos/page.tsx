'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  FileText, 
  ChevronRight, 
  Building2, 
  Landmark,
  Scale,
  FileCheck,
  ArrowRight,
  Plus
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { api } from '@/lib/api'

interface Template {
  id: string
  nome: string
  categoria: string
  descricao: string
  icone: string
  ativo: boolean
}

export default function ContratosMenuPage() {
  const router = useRouter()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      // Por enquanto, templates mockados atÃ© o backend ter endpoint
      // Depois: const response = await api.get('/contratos/templates')
      const templatesMock: Template[] = [
        {
          id: 'bacen',
          nome: 'Contrato Bacen',
          categoria: 'Bacen',
          descricao: 'RemoÃ§Ã£o de apontamentos de prejuÃ­zo no Sistema de InformaÃ§Ãµes de CrÃ©dito (SCR) do Banco Central',
          icone: 'landmark',
          ativo: true
        },
        {
          id: 'cadin',
          nome: 'Contrato CADIN PF/PJ',
          categoria: 'CADIN',
          descricao: 'RegularizaÃ§Ã£o administrativa de pendÃªncias no CADIN.',
          icone: 'file',
          ativo: true
        },
        {
          id: 'serasa',
          nome: 'Contrato Serasa',
          categoria: 'Serasa',
          descricao: 'Limpeza de nome e regularizaÃ§Ã£o de dÃ­vidas no Serasa',
          icone: 'building',
          ativo: false // Em breve
        },
        {
          id: 'protesto',
          nome: 'Contrato Protesto',
          categoria: 'Protesto',
          descricao: 'Cancelamento de protestos de tÃ­tulos',
          icone: 'scale',
          ativo: false // Em breve
        }
      ]
      setTemplates(templatesMock)
    } catch (err) {
      console.error('Erro ao carregar templates:', err)
    } finally {
      setLoading(false)
    }
  }

  const getIcone = (icone: string) => {
    switch (icone) {
      case 'landmark': return <Landmark className="w-12 h-12" />
      case 'building': return <Building2 className="w-12 h-12" />
      case 'scale': return <Scale className="w-12 h-12" />
      case 'file': return <FileText className="w-12 h-12" />
      default: return <FileText className="w-12 h-12" />
    }
  }

  const handleSelecionarTemplate = (templateId: string, ativo: boolean) => {
    if (!ativo) {
      alert('Este contrato estarÃ¡ disponÃ­vel em breve!')
      return
    }
    router.push(`/contratos/novo?template=${templateId}`)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Contratos</h1>
          <p className="text-gray-500 mt-1">
            Selecione o tipo de contrato ou visualize os existentes
          </p>
        </div>
        <Link href="/contratos/lista">
          <Button variant="outline">
            <FileCheck className="w-4 h-4 mr-2" />
            Ver Contratos Existentes
          </Button>
        </Link>
      </div>

      {/* SeÃ§Ã£o: Criar Novo Contrato */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Criar Novo Contrato
        </h2>
        
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            Carregando templates...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <Card
                key={template.id}
                className={`group cursor-pointer transition-all duration-200 hover:shadow-lg ${
                  template.ativo 
                    ? 'hover:border-blue-400 hover:bg-blue-50/30' 
                    : 'opacity-60 grayscale'
                }`}
                onClick={() => handleSelecionarTemplate(template.id, template.ativo)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className={`p-3 rounded-xl ${
                      template.ativo 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'bg-gray-100 text-gray-400'
                    }`}>
                      {getIcone(template.icone)}
                    </div>
                    {!template.ativo && (
                      <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
                        Em breve
                      </span>
                    )}
                  </div>
                  
                  <div className="mt-4">
                    <span className="text-sm text-blue-600 font-medium">
                      {template.categoria}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900 mt-1 group-hover:text-blue-700 transition-colors">
                      {template.nome}
                    </h3>
                    <p className="text-sm text-gray-500 mt-2 line-clamp-2">
                      {template.descricao}
                    </p>
                  </div>

                  <div className="mt-4 flex items-center text-sm font-medium">
                    <span className={template.ativo ? 'text-blue-600' : 'text-gray-400'}>
                      {template.ativo ? 'Preencher contrato' : 'IndisponÃ­vel'}
                    </span>
                    <ChevronRight className={`w-4 h-4 ml-1 transition-transform group-hover:translate-x-1 ${
                      template.ativo ? 'text-blue-600' : 'text-gray-400'
                    }`} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* SeÃ§Ã£o: AÃ§Ãµes RÃ¡pidas */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          AÃ§Ãµes RÃ¡pidas
        </h2>
        <div className="flex flex-wrap gap-4">
          <Link href="/contratos/lista">
            <Button variant="outline" className="bg-white">
              <FileCheck className="w-4 h-4 mr-2" />
              Lista de Contratos
            </Button>
          </Link>
          <Link href="/clientes">
            <Button variant="outline" className="bg-white">
              <Building2 className="w-4 h-4 mr-2" />
              Clientes Cadastrados
            </Button>
          </Link>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-900">
              Como funciona?
            </h3>
            <p className="text-sm text-blue-700 mt-1">
              1. Selecione o tipo de contrato acima<br/>
              2. Preencha os dados do cliente e valores<br/>
              3. O contrato Ã© gerado automaticamente com cÃ¡lculo de extensos<br/>
              4. Salve e gere o PDF para assinatura
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

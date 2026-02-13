'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Building2, ChevronRight, FileCheck, FileText, Landmark, Plus, Scale } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface Template {
  id: string
  nome: string
  categoria: string
  descricao: string
  icone: string
  ativo: boolean
}

const CONTRACT_TEMPLATES: Template[] = [
  {
    id: 'bacen',
    nome: 'Contrato Bacen',
    categoria: 'Bacen',
    descricao: 'Remoção de apontamentos de prejuízo no Sistema de Informações de Crédito (SCR) do Banco Central.',
    icone: 'landmark',
    ativo: true,
  },
  {
    id: 'cadin',
    nome: 'Contrato CADIN PF/PJ',
    categoria: 'CADIN',
    descricao: 'Regularização administrativa de pendências no CADIN.',
    icone: 'file',
    ativo: true,
  },
  {
    id: 'cnh',
    nome: 'Contrato CNH e Multas',
    categoria: 'CNH',
    descricao: 'Defesa administrativa/judicial para CNH cassada ou suspensa e recursos de multas.',
    icone: 'scale',
    ativo: true,
  },
  {
    id: 'aumento_score',
    nome: 'Contrato Aumento de Score',
    categoria: 'Score',
    descricao: 'Assessoria especializada para elevar score de crédito com plano personalizado e acompanhamento.',
    icone: 'building',
    ativo: true,
  },
  {
    id: 'diagnostico360',
    nome: 'Contrato Diagnóstico 360',
    categoria: 'Diagnóstico',
    descricao: 'Análise completa do perfil de crédito com relatório técnico e plano de ação.',
    icone: 'file',
    ativo: true,
  },
  {
    id: 'limpa_nome_standard',
    nome: 'Contrato Limpa Nome Standard',
    categoria: 'Limpa Nome',
    descricao: 'Regularização de pendências com prazo padrão, garantia e acompanhamento.',
    icone: 'file',
    ativo: true,
  },
  {
    id: 'limpa_nome_express',
    nome: 'Contrato Limpa Nome Express',
    categoria: 'Limpa Nome',
    descricao: 'Fluxo expresso para remoção de apontamentos com prioridade de execução.',
    icone: 'file',
    ativo: true,
  },
  {
    id: 'rating_convencional',
    nome: 'Contrato Rating Convencional',
    categoria: 'Rating',
    descricao: 'Execução de plano de rating com meta condicional e acompanhamento completo.',
    icone: 'landmark',
    ativo: true,
  },
  {
    id: 'rating_express_pj',
    nome: 'Contrato Rating Express PJ',
    categoria: 'Rating PJ',
    descricao: 'Modalidade expressa para melhoria de rating comercial de pessoa jurídica.',
    icone: 'landmark',
    ativo: true,
  },
  {
    id: 'rating_full_pj',
    nome: 'Contrato Rating Full PJ',
    categoria: 'Rating PJ',
    descricao: 'Execução full do plano de rating com apoio contábil (DRE) e fiscal (CND).',
    icone: 'landmark',
    ativo: true,
  },
  {
    id: 'ccf',
    nome: 'Contrato Regularização CCF',
    categoria: 'CCF',
    descricao: 'Assessoria para regularização de cheques sem fundos e baixa do cadastro CCF.',
    icone: 'scale',
    ativo: true,
  },
  {
    id: 'certificado_digital',
    nome: 'Contrato Certificado Digital',
    categoria: 'Certificado',
    descricao: 'Emissão de certificado digital com suporte completo de validação.',
    icone: 'file',
    ativo: true,
  },
  {
    id: 'remocao_proposta',
    nome: 'Contrato Remoção de Proposta',
    categoria: 'Serasa',
    descricao: 'Remoção de propostas de negociação no sistema Serasa.',
    icone: 'building',
    ativo: true,
  },
  {
    id: 'revisional',
    nome: 'Contrato Ação Revisional',
    categoria: 'Jurídico',
    descricao: 'Ação revisional com pedido de suspensão de busca e apreensão.',
    icone: 'scale',
    ativo: true,
  },
  {
    id: 'jusbrasil',
    nome: 'Contrato Jusbrasil/Escavador',
    categoria: 'Desindexação',
    descricao: 'Remoção, anonimização e desindexação de dados pessoais em agregadores jurídicos.',
    icone: 'scale',
    ativo: true,
  },
]

export default function ContratosMenuPage() {
  const router = useRouter()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      setTemplates(CONTRACT_TEMPLATES)
    } catch (err) {
      console.error('Erro ao carregar templates:', err)
    } finally {
      setLoading(false)
    }
  }

  const getIcone = (icone: string) => {
    switch (icone) {
      case 'landmark':
        return <Landmark className="h-12 w-12" />
      case 'building':
        return <Building2 className="h-12 w-12" />
      case 'scale':
        return <Scale className="h-12 w-12" />
      case 'file':
      default:
        return <FileText className="h-12 w-12" />
    }
  }

  const handleSelecionarTemplate = (templateId: string, ativo: boolean) => {
    if (!ativo) {
      alert('Este contrato estará disponível em breve!')
      return
    }
    router.push(`/contratos/novo?template=${templateId}`)
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Contratos</h1>
          <p className="mt-1 text-gray-500">Selecione o tipo de contrato ou visualize os existentes</p>
        </div>
        <Link href="/contratos/lista">
          <Button variant="outline">
            <FileCheck className="mr-2 h-4 w-4" />
            Ver Contratos Existentes
          </Button>
        </Link>
      </div>

      <div>
        <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold text-gray-800">
          <Plus className="h-5 w-5" />
          Criar Novo Contrato
        </h2>

        {loading ? (
          <div className="py-8 text-center text-gray-500">Carregando templates...</div>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => (
              <Card
                key={template.id}
                className={`group cursor-pointer transition-all duration-200 hover:shadow-lg ${
                  template.ativo ? 'hover:border-blue-400 hover:bg-blue-50/30' : 'opacity-60 grayscale'
                }`}
                onClick={() => handleSelecionarTemplate(template.id, template.ativo)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div
                      className={`rounded-xl p-3 ${
                        template.ativo ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
                      }`}
                    >
                      {getIcone(template.icone)}
                    </div>
                    {!template.ativo && (
                      <span className="rounded-full bg-gray-200 px-2 py-1 text-xs text-gray-600">Em breve</span>
                    )}
                  </div>

                  <div className="mt-4">
                    <span className="text-sm font-medium text-blue-600">{template.categoria}</span>
                    <h3 className="mt-1 text-lg font-semibold text-gray-900 transition-colors group-hover:text-blue-700">
                      {template.nome}
                    </h3>
                    <p className="mt-2 line-clamp-2 text-sm text-gray-500">{template.descricao}</p>
                  </div>

                  <div className="mt-4 flex items-center text-sm font-medium">
                    <span className={template.ativo ? 'text-blue-600' : 'text-gray-400'}>
                      {template.ativo ? 'Preencher contrato' : 'Indisponível'}
                    </span>
                    <ChevronRight
                      className={`ml-1 h-4 w-4 transition-transform group-hover:translate-x-1 ${
                        template.ativo ? 'text-blue-600' : 'text-gray-400'
                      }`}
                    />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-xl bg-gray-50 p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-800">Ações Rápidas</h2>
        <div className="flex flex-wrap gap-4">
          <Link href="/contratos/lista">
            <Button variant="outline" className="bg-white">
              <FileCheck className="mr-2 h-4 w-4" />
              Lista de Contratos
            </Button>
          </Link>
          <Link href="/clientes">
            <Button variant="outline" className="bg-white">
              <Building2 className="mr-2 h-4 w-4" />
              Clientes Cadastrados
            </Button>
          </Link>
        </div>
      </div>

      <div className="rounded-xl border border-blue-200 bg-blue-50 p-6">
        <div className="flex items-start gap-4">
          <div className="rounded-lg bg-blue-100 p-2">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-900">Como funciona?</h3>
            <p className="mt-1 text-sm text-blue-700">
              1. Selecione o tipo de contrato acima
              <br />
              2. Preencha os dados do cliente e valores
              <br />
              3. O contrato é gerado automaticamente com cálculo de extensos
              <br />
              4. Salve e gere o PDF para assinatura
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

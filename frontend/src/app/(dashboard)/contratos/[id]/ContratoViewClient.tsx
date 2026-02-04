'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, Printer, Download, Edit, Mail } from 'lucide-react'
import { contratosApi } from '@/lib/api'
import { formatCurrency, formatDate, formatCPF } from '@/lib/utils'
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
  valor_total_extenso: string
  valor_entrada_extenso: string
  qtd_parcelas_extenso: string
  valor_parcela_extenso: string
  prazo_1_extenso: string
  prazo_2_extenso: string
  dados_extras?: Record<string, any>
  created_at: string
  updated_at?: string
  cliente_nome?: string
}

export default function ContratoViewClient() {
  const params = useParams()
  const router = useRouter()
  const [contrato, setContrato] = useState<Contrato | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    carregarContrato()
  }, [])

  const carregarContrato = async () => {
    try {
      const id = params.id as string
      const data = await contratosApi.getById(id)
      setContrato(data)
    } catch (error) {
      toast.error('Erro ao carregar contrato')
    } finally {
      setLoading(false)
    }
  }

  const handlePrint = async () => {
    try {
      const { generateContractPDF } = await import('@/lib/pdf')
      generateContractPDF(contrato)
      toast.success('PDF aberto para visualização!')
    } catch (error) {
      toast.error('Erro ao gerar PDF')
    }
  }

  const handleDownload = async () => {
    try {
      const { generateContractPDF } = await import('@/lib/pdf')
      generateContractPDF(contrato)
      toast.success('PDF aberto para download!')
    } catch (error) {
      toast.error('Erro ao gerar PDF')
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      'rascunho': 'bg-yellow-100 text-yellow-800',
      'ativo': 'bg-green-100 text-green-800',
      'cancelado': 'bg-red-100 text-red-800',
      'concluido': 'bg-blue-100 text-blue-800'
    }
    return variants[status] || 'bg-gray-100 text-gray-800'
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

  const renderContratoPreview = () => {
    return (
      <div className="bg-white p-8 min-h-[1100px] shadow-sm [font-family:'Times_New_Roman',Times,serif_!important]">
        
        {/* Cabeçalho Institucional */}
        <div className="bg-[#1e3a5f] text-white py-4 px-6 mb-6 -mx-8 -mt-8">
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0">
              <svg width="60" height="60" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" stroke="white" strokeWidth="3" fill="none"/>
                <line x1="50" y1="15" x2="50" y2="85" stroke="white" strokeWidth="3"/>
                <line x1="25" y1="35" x2="75" y2="35" stroke="white" strokeWidth="2"/>
                <line x1="15" y1="35" x2="35" y2="35" stroke="white" strokeWidth="2"/>
                <line x1="65" y1="35" x2="85" y2="35" stroke="white" strokeWidth="2"/>
                <line x1="25" y1="35" x2="20" y2="50" stroke="white" strokeWidth="2"/>
                <line x1="75" y1="35" x2="80" y2="50" stroke="white" strokeWidth="2"/>
                <text x="42" y="58" fill="white" fontSize="24" fontWeight="bold" fontFamily="serif">F</text>
                <text x="54" y="58" fill="white" fontSize="24" fontWeight="bold" fontFamily="serif">C</text>
              </svg>
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold tracking-wide">
                F C Soluções Financeiras
              </h1>
            </div>
          </div>
        </div>

        {/* Título */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-bold uppercase tracking-wider text-gray-900 border-b-2 border-gray-800 pb-2 inline-block">
            Contrato de Prestação de Serviços
          </h2>
          <p className="text-gray-600 mt-2 font-semibold">Bacen - Remoção SCR</p>
          <div className="mt-4 flex justify-center gap-8 text-sm">
            <span><strong>Nº:</strong> {contrato.numero}</span>
            <span><strong>Data:</strong> {contrato.data_assinatura || formatDate(contrato.created_at)}</span>
          </div>
        </div>

        {/* Dados das Partes */}
        <div className="grid grid-cols-2 gap-6 mb-6 text-sm">
          <div className="border-2 border-gray-800 p-4">
            <h3 className="font-bold text-gray-900 uppercase mb-3 border-b border-gray-400 pb-1">Contratante</h3>
            <p><strong>Nome:</strong> {contrato.contratante_nome}</p>
            <p><strong>CPF/CNPJ:</strong> {formatCPF(contrato.contratante_documento)}</p>
            <p><strong>E-mail:</strong> {contrato.contratante_email}</p>
            {contrato.contratante_telefone && (
              <p><strong>Contato:</strong> {contrato.contratante_telefone}</p>
            )}
            <p><strong>Endereço:</strong> {contrato.contratante_endereco}</p>
          </div>

          <div className="border-2 border-gray-800 p-4">
            <h3 className="font-bold text-gray-900 uppercase mb-3 border-b border-gray-400 pb-1">Contratada</h3>
            <p><strong>Razão Social:</strong> FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</p>
            <p><strong>CNPJ:</strong> 57.815.628/0001-62</p>
            <p><strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com</p>
            <p><strong>Contato:</strong> (16) 99301-7396</p>
            <p><strong>Endereço:</strong> Rua Maria das Graças de Negreiros Bonilha, nº 30, sala 3, Jardim Nova Aliança Sul, Ribeirão Preto/SP, CEP 14022-100</p>
          </div>
        </div>

        {/* Texto introdutório */}
        <p className="text-sm text-justify mb-6 leading-relaxed">
          As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços, 
          que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.
        </p>

        {/* CLÁUSULAS */}
        <div className="space-y-4 text-sm text-justify leading-relaxed">
          
          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA PRIMEIRA - DO OBJETO</strong><br />
            O presente contrato tem como objeto a prestação de serviços de consultoria e intermediação administrativa 
            pela CONTRATADA em favor do(a) CONTRATANTE, visando a adoção de procedimentos administrativos para a 
            regularização de apontamentos de prejuízo registrados no Sistema de Informações de Crédito (SCR) do 
            Banco Central do Brasil, vinculados ao CPF/CNPJ do(a) CONTRATANTE.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA</strong><br />
            A CONTRATADA se compromete a:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Realizar uma análise detalhada da situação do(a) CONTRATANTE junto ao SCR.</li>
            <li>Elaborar e protocolar os requerimentos administrativos necessários junto às instituições financeiras pertinentes.</li>
            <li>Acompanhar o andamento dos procedimentos, empregando seus melhores esforços técnicos para a obtenção do resultado almejado.</li>
            <li>Manter o(a) CONTRATANTE informado sobre as etapas e o andamento do processo.</li>
            <li>Prestar o serviço dentro do mais alto padrão de ética e profissionalismo.</li>
          </ul>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES DO(A) CONTRATANTE</strong><br />
            <strong>3.1.</strong> O(A) CONTRATANTE se compromete a:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Fornecer à CONTRATADA todos os documentos e informações solicitados, de forma completa e verdadeira, para a correta execução dos serviços.</li>
            <li>Efetuar o pagamento dos honorários nas datas e valores acordados neste instrumento.</li>
            <li>Não tratar diretamente com as instituições financeiras sobre o objeto deste contrato sem o prévio conhecimento e anuência da CONTRATADA.</li>
          </ul>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO</strong><br />
            <strong>4.1.</strong> Pelos serviços prestados, o(a) CONTRATANTE pagará à CONTRATADA o valor total de{' '}
            <strong>{formatCurrency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), a ser pago da seguinte forma:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li><strong>Entrada:</strong> {formatCurrency(contrato.valor_entrada)} ({contrato.valor_entrada_extenso}), a ser paga no ato da assinatura deste contrato.</li>
            {contrato.qtd_parcelas > 0 && (
              <li>
                <strong>Parcelas:</strong> {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de{' '}
                {formatCurrency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso}), com vencimento em{' '}
                {contrato.prazo_1} ({contrato.prazo_1_extenso}) e {contrato.prazo_2} ({contrato.prazo_2_extenso}) dias.
              </li>
            )}
          </ul>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA QUINTA - DO PRAZO DE EXECUÇÃO</strong><br />
            O prazo estimado para a conclusão dos serviços é de 45 (quarenta e cinco) a 60 (sessenta) dias úteis, 
            contados a partir da data de assinatura deste instrumento e da confirmação do pagamento da entrada.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA SEXTA - DA GARANTIA DE RESULTADO</strong><br />
            O serviço objeto deste contrato é de resultado, vinculado à efetiva baixa dos apontamentos no SCR.
          </p>
          <p>
            Caso a CONTRATADA não comprove a conclusão do serviço no prazo máximo de 60 (sessenta) dias úteis, 
            o presente contrato será considerado automaticamente rescindido.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA SÉTIMA - DO INADIMPLEMENTO</strong><br />
            Em caso de atraso no pagamento, o valor devido será acrescido de multa de 10% e juros de 1% ao mês.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA OITAVA - DA ALOCAÇÃO DE RECURSOS</strong><br />
            Ao assinar este contrato, o(a) CONTRATANTE autoriza a alocação imediata e irreversível dos recursos.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA NONA - DA CONFIDENCIALIDADE</strong><br />
            As partes se comprometem a manter em sigilo todas as informações.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÁUSULA DÉCIMA - DO FORO</strong><br />
            Para dirimir quaisquer controvérsias, as partes elegem o foro da Comarca de São Paulo/SP.
          </p>

          <p className="mt-6">
            E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias.
          </p>

          <p className="mt-4 font-semibold">
            {contrato.local_assinatura || 'Ribeirão Preto/SP'}, {contrato.data_assinatura || formatDate(contrato.created_at)}.
          </p>
        </div>

        {/* Assinaturas */}
        <div className="mt-12 grid grid-cols-2 gap-8">
          <div className="text-center">
            <div className="border-t-2 border-black pt-2 mt-16">
              <p className="font-bold text-sm">{contrato.contratante_nome}</p>
              <p className="text-xs text-gray-600">CPF: {formatCPF(contrato.contratante_documento)}</p>
              <p className="text-xs text-gray-500 uppercase mt-1 font-semibold">CONTRATANTE</p>
            </div>
          </div>
          <div className="text-center">
            <div className="border-t-2 border-black pt-2 mt-16">
              <p className="font-bold text-sm">FC SERVIÇOS E SOLUÇÕES ADMINISTRATIVAS LTDA</p>
              <p className="text-xs text-gray-600">CNPJ: 57.815.628/0001-62</p>
              <p className="text-xs text-gray-500 uppercase mt-1 font-semibold">CONTRATADA</p>
            </div>
          </div>
        </div>

        {/* Rodapé */}
        <div className="mt-8 pt-3 border-t border-gray-300 text-center text-xs text-gray-500">
          <p>FC Soluções Financeiras - CNPJ: 57.815.628/0001-62</p>
          <p>Documento gerado em {formatDate(new Date().toISOString())}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => router.push('/contratos/lista')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Contrato {contrato.numero}
            </h1>
            <p className="text-sm text-gray-500">
              Criado em {formatDate(contrato.created_at)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getStatusBadge(contrato.status)}>
            {contrato.status.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* Ações */}
      <div className="flex items-center gap-2 mb-6">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => router.push(`/contratos/${contrato.id}/editar`)}
        >
          <Edit className="h-4 w-4 mr-2" />
          Editar
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={handlePrint}
        >
          <Printer className="h-4 w-4 mr-2" />
          Visualizar PDF
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={handleDownload}
        >
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => toast.info('Funcionalidade em desenvolvimento')}
        >
          <Mail className="h-4 w-4 mr-2" />
          Enviar
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="preview" className="flex-1">
        <TabsList>
          <TabsTrigger value="preview">Visualização</TabsTrigger>
          <TabsTrigger value="data">Dados</TabsTrigger>
        </TabsList>
        
        <TabsContent value="preview" className="mt-4">
          <Card>
            <CardContent className="p-0">
              {renderContratoPreview()}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="data" className="mt-4">
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">Dados do Contrato</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Número:</span>
                  <span className="font-medium">{contrato.numero}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Template:</span>
                  <span className="font-medium">{contrato.template_nome}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Status:</span>
                  <span className="font-medium capitalize">{contrato.status}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Contratante:</span>
                  <span className="font-medium">{contrato.contratante_nome}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">CPF:</span>
                  <span className="font-medium">{formatCPF(contrato.contratante_documento)}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Valor Total:</span>
                  <span className="font-medium">{formatCurrency(contrato.valor_total)}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Entrada:</span>
                  <span className="font-medium">{formatCurrency(contrato.valor_entrada)}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-500">Parcelas:</span>
                  <span className="font-medium">{contrato.qtd_parcelas}x</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

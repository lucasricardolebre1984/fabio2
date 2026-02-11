'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, Printer, Download, Edit, Mail, Share2 } from 'lucide-react'
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

function normalizeMojibakeText(value?: string | null): string {
  const text = String(value || '').trim()
  if (!text) return ''
  if (!/[\u00C3\u00C2]/.test(text)) return text

  try {
    const bytes = Uint8Array.from(text, (char) => char.charCodeAt(0))
    return new TextDecoder('utf-8').decode(bytes)
  } catch {
    return text
  }
}

export default function VisualizarContratoPage() {
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
      toast.success('PDF aberto para visualizaÃ§Ã£o!')
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
        <p>Contrato nÃ£o encontrado</p>
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

  const templateId = (contrato.template_id || '').toLowerCase()
  const isCadin = templateId === 'cadin'
  const isCnh = templateId === 'cnh'
  const localAssinatura = normalizeMojibakeText(contrato.local_assinatura) || 'Ribeir\u00E3o Preto/SP'
  const cnhNumero = String(contrato.dados_extras?.cnh_numero || '').trim()
  const contractSubtitle = isCadin
    ? 'CADIN - Regularizacao de pendencias federais'
    : isCnh
      ? 'CNH - Cassacao/Suspensao e Recurso de Multas'
      : 'Bacen - Remocao SCR'
  // Layout institucional conforme modelo
  const renderContratoPreview = () => {
    return (
      <div className="bg-white p-10 min-h-[1120px] shadow-sm [font-family:'Times_New_Roman',Times,serif_!important]">
        
        {/* CabeÃ§alho Institucional - Faixa Azul com Logo */}
        <div className="bg-[#1e3a5f] text-white py-5 px-8 mb-8 -mx-10 -mt-10">
          <div className="flex items-center gap-4">
            {/* Logo Institucional */}
            <div className="flex-shrink-0">
              <img
                src="/logo2.png"
                alt="FC SoluÃ§Ãµes Financeiras"
                className="h-[92px] w-auto object-contain"
              />
            </div>
            <div className="flex-1">
              <h1 className="text-[2rem] font-bold tracking-wide">
                F C SoluÃ§Ãµes Financeiras
              </h1>
            </div>
          </div>
        </div>

        {/* TÃ­tulo */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold uppercase tracking-wider text-gray-900 border-b-2 border-gray-800 pb-2 inline-block">
            Contrato de PrestaÃ§Ã£o de ServiÃ§os
          </h2>
          <p className="text-gray-600 mt-2 font-semibold">{contractSubtitle}</p>
          <div className="mt-5 flex justify-center gap-10 text-base">
            <span><strong>NÂº:</strong> {contrato.numero}</span>
            <span><strong>Data:</strong> {contrato.data_assinatura || formatDate(contrato.created_at)}</span>
          </div>
        </div>

        {/* Dados das Partes - Layout em duas colunas */}
        <div className="grid grid-cols-2 gap-6 mb-7 text-base">
          <div className="border-2 border-gray-800 p-4">
            <h3 className="font-bold text-gray-900 uppercase mb-3 border-b border-gray-400 pb-1">Contratante</h3>
            <p><strong>Nome:</strong> {contrato.contratante_nome}</p>
            <p><strong>CPF/CNPJ:</strong> {formatCPF(contrato.contratante_documento)}</p>
            {isCnh && cnhNumero && <p><strong>CNH:</strong> {cnhNumero}</p>}
            <p><strong>E-mail:</strong> {contrato.contratante_email}</p>
            {contrato.contratante_telefone && (
              <p><strong>Contato:</strong> {contrato.contratante_telefone}</p>
            )}
            <p><strong>EndereÃ§o:</strong> {contrato.contratante_endereco}</p>
          </div>

          <div className="border-2 border-gray-800 p-4">
            <h3 className="font-bold text-gray-900 uppercase mb-3 border-b border-gray-400 pb-1">Contratada</h3>
            <p><strong>RazÃ£o Social:</strong> FC SERVIÃ‡OS E SOLUÃ‡Ã•ES ADMINISTRATIVAS LTDA</p>
            <p><strong>CNPJ:</strong> 57.815.628/0001-62</p>
            <p><strong>E-mail:</strong> contato@fcsolucoesfinanceiras.com</p>
            <p><strong>Contato:</strong> (16) 99301-7396</p>
            <p><strong>EndereÃ§o:</strong> Rua Maria das GraÃ§as de Negreiros Bonilha, nÂº 30, sala 3, Jardim Nova AlianÃ§a Sul, RibeirÃ£o Preto/SP, CEP 14022-100</p>
          </div>
        </div>

        {/* Texto introdutÃ³rio */}
        <p className="text-base text-justify mb-7 leading-relaxed">
          As partes acima identificadas tÃªm, entre si, justo e acertado o presente Contrato de PrestaÃ§Ã£o de ServiÃ§os, 
          que se regerÃ¡ pelas clÃ¡usulas seguintes e pelas condiÃ§Ãµes descritas no presente.
        </p>

        {/* CLÃUSULAS */}
        <div className="space-y-4 text-base text-justify leading-relaxed">
          {isCadin ? (
            <>
              <p>
                <strong className="text-gray-900 uppercase">CLÃUSULA PRIMEIRA - DO OBJETO</strong><br />
                <strong>1.1.</strong> O presente instrumento tem por objeto a prestaÃ§Ã£o de serviÃ§os de assessoria administrativa para a
                regularizaÃ§Ã£o de pendÃªncias do(a) CONTRATANTE junto ao Cadastro Informativo de CrÃ©ditos nÃ£o Quitados do Setor PÃºblico
                Federal (CADIN), visando Ã  adoÃ§Ã£o dos procedimentos necessÃ¡rios para obtenÃ§Ã£o da CertidÃ£o Negativa de DÃ©bitos (CND)
                ou documento equivalente, referente Ã s dÃ­vidas federais constatadas atÃ© a data de assinatura deste contrato.
              </p>
              <p>
                <strong>Â§1Âº.</strong> O serviÃ§o inclui anÃ¡lise dos dÃ©bitos, negociaÃ§Ã£o junto aos Ã³rgÃ£os credores para obtenÃ§Ã£o de descontos e
                formalizaÃ§Ã£o de parcelamentos, conforme as condiÃ§Ãµes e programas de anistia disponibilizados pelo governo.
              </p>
              <p>
                <strong>Â§2Âº.</strong> Fica expressamente claro que a CONTRATADA nÃ£o se responsabiliza pela quitaÃ§Ã£o das dÃ­vidas do(a)
                CONTRATANTE, mas sim pela prestaÃ§Ã£o de serviÃ§os de assessoria para negociaÃ§Ã£o e regularizaÃ§Ã£o dos apontamentos no CADIN.
              </p>
              <p>
                <strong>Â§3Âº.</strong> DÃ©bitos que surgirem ou forem inscritos no CADIN apÃ³s a data de assinatura deste contrato nÃ£o estarÃ£o
                cobertos por este instrumento.
              </p>
              <p>
                <strong>1.2.</strong> Os serviÃ§os contratados nÃ£o representam garantia de aprovaÃ§Ã£o de crÃ©dito para o(a) CONTRATANTE,
                mas um meio para regularizaÃ§Ã£o da situaÃ§Ã£o fiscal perante os Ã³rgÃ£os federais.
              </p>
              <p>
                <strong className="text-gray-900 uppercase">CLÃUSULA SEGUNDA - DAS DESPESAS E HONORÃRIOS</strong><br />
                <strong>2.1.</strong> Como contraprestaÃ§Ã£o pelos serviÃ§os descritos na ClÃ¡usula 1Âª, o(a) CONTRATANTE pagarÃ¡ Ã  CONTRATADA
                o valor total de <strong>{formatCurrency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), sendo entrada de{' '}
                <strong>{formatCurrency(contrato.valor_entrada)}</strong> ({contrato.valor_entrada_extenso})
                {contrato.qtd_parcelas > 0 ? (
                  <> e o saldo em {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de {formatCurrency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso}).</>
                ) : (
                  <> com pagamento integral na assinatura.</>
                )}
              </p>
              <p>
                <strong>2.2.</strong> Em caso de atraso superior a 30 (trinta) dias no pagamento de qualquer parcela, o serviÃ§o serÃ¡
                suspenso. Persistindo a inadimplÃªncia, o(a) CONTRATANTE perderÃ¡ o direito Ã  continuidade do serviÃ§o e aos valores jÃ¡ pagos,
                e as demais parcelas em aberto poderÃ£o ser protestadas.
              </p>
              <p>
                <strong>2.3.</strong> No caso de solicitaÃ§Ã£o de cancelamento pelo(a) CONTRATANTE, serÃ¡ cobrada multa de 30% (trinta por cento)
                sobre o valor total das parcelas em aberto.
              </p>
              <p>
                <strong>2.4.</strong> A execuÃ§Ã£o dos serviÃ§os terÃ¡ inÃ­cio imediato apÃ³s a assinatura deste contrato e confirmaÃ§Ã£o do pagamento
                da primeira parcela ou do valor integral, conforme modalidade escolhida.
              </p>
              <p>
                <strong>2.5.</strong> Havendo parcelamento, o nÃ£o pagamento de qualquer parcela acarretarÃ¡ acrÃ©scimo de juros de 2% (dois por cento)
                ao mÃªs, multa de 10% (dez por cento) e correÃ§Ã£o monetÃ¡ria.
              </p>
              <p>
                <strong>2.6.</strong> O nÃ£o pagamento de uma parcela acarreta vencimento antecipado das vincendas, podendo a CONTRATADA
                promover cobranÃ§a e protesto dos tÃ­tulos em aberto perante o foro da comarca de RibeirÃ£o Preto/SP.
              </p>
              <p>
                <strong>2.7.</strong> A rescisÃ£o solicitada pelo(a) CONTRATANTE apÃ³s o inÃ­cio da prestaÃ§Ã£o dos serviÃ§os implica multa compensatÃ³ria
                de 30% (trinta por cento) do valor acordado, sem direito a ressarcimento dos valores jÃ¡ pagos.
              </p>
              <p>
                <strong className="text-gray-900 uppercase">CLÃUSULA TERCEIRA - DO PRAZO E GARANTIA</strong><br />
                <strong>3.1.</strong> A CONTRATADA realizarÃ¡ os procedimentos no prazo de atÃ© 45 (quarenta e cinco) dias Ãºteis, contados da
                confirmaÃ§Ã£o do pagamento e assinatura deste contrato, podendo ser prorrogado conforme complexidade dos dÃ©bitos ou prazos dos Ã³rgÃ£os.
              </p>
              <p>
                <strong>Â§1Âº - GARANTIA DE RESULTADO:</strong> caso o serviÃ§o nÃ£o seja executado no prazo estabelecido, a CONTRATADA garantirÃ¡
                devoluÃ§Ã£o integral do valor pago em atÃ© 30 (trinta) dias Ãºteis apÃ³s o tÃ©rmino do prazo.
              </p>
              <p>
                <strong>3.2.</strong> A CONTRATADA oferece garantia de acompanhamento por 1 (um) ano, contado da data de efetiva regularizaÃ§Ã£o dos apontamentos.
                Se os apontamentos das dÃ­vidas tratadas neste contrato retornarem ao CADIN nesse perÃ­odo, o processo serÃ¡ refeito sem custo adicional.
              </p>
              <p>
                <strong>Â§2Âº - ABRANGÃŠNCIA DA GARANTIA:</strong> a garantia aplica-se exclusivamente Ã s dÃ­vidas e restriÃ§Ãµes identificadas e tratadas
                no Ã¢mbito deste contrato. DÃ­vidas ou restriÃ§Ãµes posteriores nÃ£o estÃ£o cobertas.
              </p>
              <p>
                <strong className="text-gray-900 uppercase">CLÃUSULA QUARTA - DA PROTEÃ‡ÃƒO DE DADOS (LGPD)</strong><br />
                <strong>4.1.</strong> Em conformidade com a Lei nÂº 13.709/2018 (LGPD), a CONTRATADA tratarÃ¡ os dados pessoais do(a) CONTRATANTE
                com finalidade exclusiva de execuÃ§Ã£o contratual, nos termos do art. 7Âº, incisos II, V e X.
              </p>
              <p>
                <strong>Â§1Âº.</strong> A CONTRATADA adota medidas de seguranÃ§a para proteger os dados e os eliminarÃ¡ apÃ³s o tÃ©rmino do serviÃ§o,
                ressalvadas as obrigaÃ§Ãµes legais de guarda.
              </p>
              <p>
                <strong>Â§2Âº.</strong> O(A) CONTRATANTE pode exercer direitos de titular (acesso, correÃ§Ã£o, eliminaÃ§Ã£o etc.) pelo e-mail:
                contato@fcsolucoesfinanceiras.com.
              </p>
              <p>
                <strong className="text-gray-900 uppercase">CLÃUSULA QUINTA - DO FORO</strong><br />
                <strong>5.1.</strong> Para dirimir controvÃ©rsias oriundas deste contrato, as partes elegem o foro da comarca de RibeirÃ£o Preto/SP,
                ressalvada a faculdade do(a) CONTRATANTE de propor aÃ§Ã£o no foro de seu domicÃ­lio, conforme o CÃ³digo de Defesa do Consumidor.
              </p>
              <p className="mt-6">
                E, por estarem assim justas e contratadas, as partes assinam o presente instrumento em 2 (duas) vias de igual teor e forma,
                juntamente com 2 (duas) testemunhas.
              </p>
              <p className="mt-4 font-semibold">
                {localAssinatura}, {contrato.data_assinatura || formatDate(contrato.created_at)}.
              </p>
            </>
          ) : isCnh ? (
            <>
              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA PRIMEIRA - DO OBJETO</strong><br />
                <strong>1.1.</strong> O presente contrato tem por objeto a prestacao de servicos de assessoria tecnica especializada
                para defesa administrativa e judicial contra suspensao, cassacao da Carteira Nacional de Habilitacao (CNH)
                e multas de transito aplicadas ao(à) CONTRATANTE.
              </p>
              <p>
                <strong>1.2.</strong> O servico compreende analise tecnica das infracoes para identificacao de erros formais,
                nulidades processuais e vicios de legalidade, com objetivo de cancelamento das penalidades junto aos orgaos competentes.
              </p>
              <p>
                <strong>1.3.</strong> A atuacao inclui protocolo de recursos e defesas, acompanhamento processual e, quando necessario,
                ajuizamento de medida judicial cabivel.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA SEGUNDA - DAS OBRIGACOES DA CONTRATADA</strong><br />
                A CONTRATADA compromete-se a realizar analise tecnica, elaborar e protocolar as pecas cabiveis,
                acompanhar os processos e informar o(a) CONTRATANTE sobre o andamento e desfecho.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA TERCEIRA - DAS OBRIGACOES DO(A) CONTRATANTE</strong><br />
                O(A) CONTRATANTE se compromete a fornecer documentacao completa e veridica, efetuar pagamentos nas datas acordadas
                e atender convocacoes de diligencias ou audiencias quando aplicavel.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO</strong><br />
                Pelos servicos, o(a) CONTRATANTE pagara o valor total de <strong>{formatCurrency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}),
                com entrada de <strong>{formatCurrency(contrato.valor_entrada)}</strong> ({contrato.valor_entrada_extenso})
                {contrato.qtd_parcelas > 0 ? (
                  <> e saldo em {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de {formatCurrency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso}).</>
                ) : (
                  <> com pagamento integral na assinatura.</>
                )}
              </p>
              <p>
                <strong>Antecipacao:</strong> desconto de 1,5% ao mes, limitado a 15%, mediante solicitacao previa e pagamento por PIX.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA QUINTA - DO PRAZO DE EXECUCAO</strong><br />
                A CONTRATADA executara as medidas administrativas em ate 15 (quinze) dias uteis, contados da assinatura,
                confirmacao de pagamento e entrega da documentacao completa.
              </p>
              <p>
                O prazo de decisao dos orgaos de transito independe da CONTRATADA.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA SEXTA - DA GARANTIA DE ENTREGA</strong><br />
                Caso a CONTRATADA nao protocole os atos no prazo da clausula anterior por sua culpa, havera devolucao integral dos valores
                pagos em ate 10 (dez) dias uteis. Esta garantia nao implica promessa de resultado favoravel no merito.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA SETIMA - INADIMPLEMENTO</strong><br />
                Em atraso de pagamento: multa de 20%, juros de 1% ao mes pro rata die e correcao pelo IPCA/IBGE.
                Atraso superior a 30 dias suspende os servicos; persistindo por mais 15 dias, ha perda do direito ao servico.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA OITAVA - RESCISAO</strong><br />
                Rescisao pelo(a) CONTRATANTE apos inicio dos servicos implica multa de 20% do valor total, sem ressarcimento,
                salvo inadimplemento da CONTRATADA previsto na clausula de garantia.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA NONA - LGPD E CONFIDENCIALIDADE</strong><br />
                Os dados pessoais serao tratados exclusivamente para execucao do contrato, conforme Lei 13.709/2018 (LGPD),
                com sigilo das informacoes trocadas entre as partes.
              </p>

              <p>
                <strong className="text-gray-900 uppercase">CLAUSULA DECIMA - DO FORO</strong><br />
                Fica eleito o foro da Comarca de Ribeirao Preto/SP, ressalvado o foro do domicilio do(a) CONTRATANTE,
                conforme o CDC.
              </p>

              <p className="mt-6">
                E, por estarem justas e contratadas, as partes assinam o presente instrumento em 2 (duas) vias de igual teor e forma.
              </p>
              <p className="mt-4 font-semibold">
                {localAssinatura}, {contrato.data_assinatura || formatDate(contrato.created_at)}.
              </p>
            </>
          ) : (
            <>
          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA PRIMEIRA - DO OBJETO</strong><br />
            O presente contrato tem como objeto a prestaÃ§Ã£o de serviÃ§os de consultoria e intermediaÃ§Ã£o administrativa 
            pela CONTRATADA em favor do(a) CONTRATANTE, visando a adoÃ§Ã£o de procedimentos administrativos para a 
            regularizaÃ§Ã£o de apontamentos de prejuÃ­zo registrados no Sistema de InformaÃ§Ãµes de CrÃ©dito (SCR) do 
            Banco Central do Brasil, vinculados ao CPF/CNPJ do(a) CONTRATANTE.
          </p>
          <p>
            O serviÃ§o consiste na anÃ¡lise do caso, elaboraÃ§Ã£o de requerimentos e acompanhamento do processo 
            administrativo junto Ã s instituiÃ§Ãµes financeiras credoras, buscando a baixa dos referidos apontamentos, 
            nos termos da regulamentaÃ§Ã£o vigente.
          </p>
          <p>
            Fica claro entre as partes que este serviÃ§o nÃ£o se trata de quitaÃ§Ã£o ou pagamento de dÃ­vidas, 
            mas sim de um procedimento administrativo para a regularizaÃ§Ã£o dos registros no SCR.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA SEGUNDA - DAS OBRIGAÃ‡Ã•ES DA CONTRATADA</strong><br />
            A CONTRATADA se compromete a:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Realizar uma anÃ¡lise detalhada da situaÃ§Ã£o do(a) CONTRATANTE junto ao SCR.</li>
            <li>Elaborar e protocolar os requerimentos administrativos necessÃ¡rios junto Ã s instituiÃ§Ãµes financeiras pertinentes.</li>
            <li>Acompanhar o andamento dos procedimentos, empregando seus melhores esforÃ§os tÃ©cnicos para a obtenÃ§Ã£o do resultado almejado.</li>
            <li>Manter o(a) CONTRATANTE informado sobre as etapas e o andamento do processo.</li>
            <li>Prestar o serviÃ§o dentro do mais alto padrÃ£o de Ã©tica e profissionalismo.</li>
          </ul>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA TERCEIRA - DAS OBRIGAÃ‡Ã•ES DO(A) CONTRATANTE</strong><br />
            <strong>3.1.</strong> O(A) CONTRATANTE se compromete a:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Fornecer Ã  CONTRATADA todos os documentos e informaÃ§Ãµes solicitados, de forma completa e verdadeira, para a correta execuÃ§Ã£o dos serviÃ§os.</li>
            <li>Efetuar o pagamento dos honorÃ¡rios nas datas e valores acordados neste instrumento.</li>
            <li>NÃ£o tratar diretamente com as instituiÃ§Ãµes financeiras sobre o objeto deste contrato sem o prÃ©vio conhecimento e anuÃªncia da CONTRATADA.</li>
          </ul>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA QUARTA - DO VALOR E DA FORMA DE PAGAMENTO</strong><br />
            <strong>4.1.</strong> Pelos serviÃ§os prestados, o(a) CONTRATANTE pagarÃ¡ Ã  CONTRATADA o valor total de{' '}
            <strong>{formatCurrency(contrato.valor_total)}</strong> ({contrato.valor_total_extenso}), a ser pago da seguinte forma:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li><strong>Entrada:</strong> {formatCurrency(contrato.valor_entrada)} ({contrato.valor_entrada_extenso}), a ser paga no ato da assinatura deste contrato.</li>
            {contrato.qtd_parcelas > 0 && (
              <li>
                <strong>Parcelas:</strong> {contrato.qtd_parcelas} ({contrato.qtd_parcelas_extenso}) parcelas de{' '}
                {formatCurrency(contrato.valor_parcela)} ({contrato.valor_parcela_extenso}), com vencimento em{' '}
                {contrato.prazo_1} ({contrato.prazo_1_extenso}) e {contrato.prazo_2} ({contrato.prazo_2_extenso}) dias, 
                respectivamente, a contar da data de assinatura.
              </li>
            )}
          </ul>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA QUINTA - DO PRAZO DE EXECUÃ‡ÃƒO</strong><br />
            O prazo estimado para a conclusÃ£o dos serviÃ§os Ã© de 45 (quarenta e cinco) a 60 (sessenta) dias Ãºteis, 
            contados a partir da data de assinatura deste instrumento e da confirmaÃ§Ã£o do pagamento da entrada.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA SEXTA - DA GARANTIA DE RESULTADO E POLÃTICA DE REEMBOLSO</strong><br />
            O serviÃ§o objeto deste contrato Ã© de resultado, vinculado Ã  efetiva baixa e atualizaÃ§Ã£o dos apontamentos 
            de prejuÃ­zo no Sistema de InformaÃ§Ãµes de CrÃ©dito (SCR) do Banco Central, conforme o escopo definido na ClÃ¡usula Primeira.
          </p>
          <p>
            Caso a CONTRATADA nÃ£o comprove a conclusÃ£o do serviÃ§o no prazo mÃ¡ximo de 60 (sessenta) dias Ãºteis, 
            o presente contrato serÃ¡ considerado automaticamente rescindido por inadimplemento da CONTRATADA.
          </p>
          <p>
            Na hipÃ³tese de rescisÃ£o por descumprimento do prazo, a CONTRATADA deverÃ¡ realizar a devoluÃ§Ã£o integral 
            dos valores jÃ¡ pagos pelo(a) CONTRATANTE, no prazo de atÃ© 30 (trinta) dias Ãºteis apÃ³s o tÃ©rmino do prazo contratual.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA SÃ‰TIMA - DO INADIMPLEMENTO DO(A) CONTRATANTE</strong><br />
            Em caso de atraso no pagamento de qualquer parcela, o valor devido serÃ¡ acrescido de:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Multa de 10% (dez por cento) sobre o valor da parcela em atraso;</li>
            <li>Juros de mora de 1% (um por cento) ao mÃªs, calculados pro rata die;</li>
            <li>CorreÃ§Ã£o monetÃ¡ria pelo Ã­ndice IPCA/IBGE, ou outro que venha a substituÃ­-lo.</li>
          </ul>
          <p>
            O atraso superior a 30 (trinta) dias no pagamento de qualquer parcela poderÃ¡ ensejar a suspensÃ£o dos 
            serviÃ§os e, a critÃ©rio da CONTRATADA, a rescisÃ£o do presente contrato.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA OITAVA - DA ALOCAÃ‡ÃƒO DE RECURSOS E DA IRREVERSIBILIDADE DOS CUSTOS</strong><br />
            O(A) CONTRATANTE declara estar ciente de que o processo de contrataÃ§Ã£o foi dividido em duas fases distintas: 
            (I) a fase de anÃ¡lise e onboarding, de carÃ¡ter gratuito e sem compromisso; e (II) a fase de execuÃ§Ã£o do serviÃ§o.
          </p>
          <p>
            Ao assinar este contrato, o(a) CONTRATANTE autoriza e a CONTRATADA se compromete a alocar, de forma 
            imediata e irreversÃ­vel, os recursos humanos e materiais necessÃ¡rios para o protocolo e acompanhamento 
            do procedimento administrativo.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA NONA - DA CONFIDENCIALIDADE</strong><br />
            As partes se comprometem a manter em sigilo todas as informaÃ§Ãµes e documentos a que tiverem acesso em 
            decorrÃªncia deste contrato, nÃ£o podendo divulgÃ¡-los a terceiros sem a prÃ©via autorizaÃ§Ã£o da outra parte.
          </p>

          <p>
            <strong className="text-gray-900 uppercase">CLÃUSULA DÃ‰CIMA - DO FORO</strong><br />
            Para dirimir quaisquer controvÃ©rsias oriundas do CONTRATO, as partes elegem o foro da Comarca de SÃ£o Paulo/SP.
          </p>

          <p className="mt-6">
            E, por estarem assim justos e contratados, firmam o presente instrumento em 2 (duas) vias de igual teor e forma.
          </p>

          <p className="mt-4 font-semibold">
            {localAssinatura}, {contrato.data_assinatura || formatDate(contrato.created_at)}.
          </p>
            </>
          )}
        </div>

        {/* Assinaturas */}
        <div className="mt-12 grid grid-cols-2 gap-8">
          <div className="text-center">
            <div className="border-t-2 border-black pt-2 mt-16">
              <p className="font-bold text-base">{contrato.contratante_nome}</p>
              <p className="text-xs text-gray-600">CPF: {formatCPF(contrato.contratante_documento)}</p>
              <p className="text-xs text-gray-500 uppercase mt-1 font-semibold">CONTRATANTE</p>
            </div>
          </div>
          <div className="text-center">
            <div className="border-t-2 border-black pt-2 mt-16">
              <p className="font-bold text-base">FC SERVIÃ‡OS E SOLUÃ‡Ã•ES ADMINISTRATIVAS LTDA</p>
              <p className="text-xs text-gray-600">CNPJ: 57.815.628/0001-62</p>
              <p className="text-xs text-gray-500 uppercase mt-1 font-semibold">CONTRATADA</p>
            </div>
          </div>
        </div>

        {/* Testemunhas */}
        <div className="mt-8 text-base">
          <p className="font-bold mb-2">Testemunhas:</p>
          <div className="grid grid-cols-2 gap-8">
            <div>
              <p>1. _______________________________________</p>
              <p className="text-xs text-gray-600 mt-1">Nome:</p>
              <p className="text-xs text-gray-600">CPF:</p>
            </div>
            <div>
              <p>2. _______________________________________</p>
              <p className="text-xs text-gray-600 mt-1">Nome:</p>
              <p className="text-xs text-gray-600">CPF:</p>
            </div>
          </div>
        </div>

        {/* RodapÃ© */}
        <div className="mt-8 pt-3 border-t border-gray-300 text-center text-xs text-gray-500">
          <p>FC SoluÃ§Ãµes Financeiras - CNPJ: 57.815.628/0001-62</p>
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

      {/* AÃ§Ãµes */}
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
          <TabsTrigger value="preview">VisualizaÃ§Ã£o</TabsTrigger>
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
                  <span className="text-gray-500">NÃºmero:</span>
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



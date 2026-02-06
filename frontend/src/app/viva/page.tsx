'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, Trash2, Copy, Check, ImageIcon, Mic, X, FileUp, Layout, Palette, Image as ImageLucide, FileText, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { api } from '@/lib/api'

interface Mensagem {
  id: string
  tipo: 'usuario' | 'ia'
  conteudo: string
  timestamp: Date
  anexos?: { tipo: 'imagem' | 'audio' | 'arquivo'; url: string; nome?: string; meta?: any }[]
  modo?: string
  overlay?: {
    brand: 'REZETA' | 'FC'
    text?: string
    copy?: {
      headline?: string
      subheadline?: string
      bullets?: string[]
      quote?: string
      cta?: string
    }
  }
}

interface PromptItem {
  id: string
  titulo: string
  icone: React.ReactNode
  descricao: string
  cor: string
}

const PROMPTS: PromptItem[] = [
  {
    id: 'CRIADORLANDPAGE',
    titulo: 'Landing Pages',
    icone: <Layout className="w-5 h-5" />,
    descricao: 'Criar sites e landing pages',
    cor: 'bg-blue-500'
  },
  {
    id: 'LOGO',
    titulo: 'Logos & Brand',
    icone: <Palette className="w-5 h-5" />,
    descricao: 'Gerar logos e identidade visual',
    cor: 'bg-purple-500'
  },
  {
    id: 'FC',
    titulo: 'Imagens FC',
    icone: <ImageLucide className="w-5 h-5" />,
    descricao: 'Imagens para FC Soluções',
    cor: 'bg-indigo-500'
  },
  {
    id: 'REZETA',
    titulo: 'Imagens Rezeta',
    icone: <FileText className="w-5 h-5" />,
    descricao: 'Imagens para RezetaBrasil',
    cor: 'bg-green-500'
  },
  {
    id: 'CRIADORPROMPT',
    titulo: 'Criador Prompt',
    icone: <Sparkles className="w-5 h-5" />,
    descricao: 'Criar instruções de sistema',
    cor: 'bg-amber-500'
  }
]

const IMAGE_TERMS = [
  'imagem',
  'banner',
  'logo',
  'logotipo',
  'post',
  'flyer',
  'arte',
  'cartaz',
  'thumbnail',
  'capa'
]

const isImageRequest = (text: string) => {
  const lower = text.toLowerCase()
  return IMAGE_TERMS.some(term => lower.includes(term))
}

const extractOverlaySource = (text: string) => {
  const lower = text.toLowerCase()
  const markers = [
    'segue o texto a ser vinculado',
    'segue o texto',
    'texto a ser vinculado',
    'texto:'
  ]
  const found = markers.find(marker => lower.includes(marker))
  if (!found) return text

  const parts = text.split(new RegExp(found, 'i'))
  if (parts.length < 2) return text
  return parts.slice(1).join(' ').replace(':', '').trim()
}

const parseOverlayText = (overlay?: Mensagem['overlay']) => {
  if (!overlay) {
    return {
      headline: 'Mensagem principal',
      subheadline: '',
      bullets: [],
      quote: '',
      cta: ''
    }
  }

  if (overlay.copy?.headline || overlay.copy?.subheadline || overlay.copy?.bullets?.length) {
    return {
      headline: overlay.copy?.headline || 'Mensagem principal',
      subheadline: overlay.copy?.subheadline || '',
      bullets: (overlay.copy?.bullets || []).slice(0, 6),
      quote: overlay.copy?.quote || '',
      cta: overlay.copy?.cta || ''
    }
  }

  const sourceText = extractOverlaySource(overlay.text || '')
  const lines = sourceText
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)
    .filter(line => {
      const lower = line.toLowerCase()
      return !(
        lower.startsWith('gerar uma imagem') ||
        lower.startsWith('segue o texto') ||
        lower.startsWith('texto a ser vinculado') ||
        lower.startsWith('segue o texto a ser vinculado')
      )
    })

  const headline = lines.find(line => !/^(✅|❌|⚠️|•|-)/.test(line) && !line.startsWith('"') && !line.startsWith('“')) || lines[0] || 'Mensagem principal'
  const quote = lines.find(line => line.startsWith('"') || line.startsWith('“'))
  const bulletLines = lines.filter(line => /^(✅|❌|⚠️|•|-)/.test(line))
  const remaining = lines.filter(line => line !== headline && line !== quote && !bulletLines.includes(line))
  const subheadline = remaining[0] || ''

  return {
    headline,
    subheadline,
    bullets: bulletLines.slice(0, 6),
    quote,
    cta: ''
  }
}

const BRAND_THEMES = {
  REZETA: {
    label: 'RezetaBrasil',
    primary: '#1E3A5F',
    accent: '#3DAA7F',
    dark: '#2A8B68',
    light: '#FFFFFF'
  },
  FC: {
    label: 'FC Solucoes Financeiras',
    primary: '#071c4a',
    accent: '#00a3ff',
    dark: '#010a1c',
    light: '#f9feff'
  }
} as const

export default function VivaChatPage() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([
    {
      id: 'welcome',
      tipo: 'ia',
      conteudo: 'Olá! Sou a VIVA, assistente virtual da FC Soluções Financeiras. Como posso ajudar você hoje?\n\n💡 Selecione um modo especial no menu lateral ou envie uma mensagem diretamente.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [anexos, setAnexos] = useState<{ file: File; tipo: 'imagem' | 'audio' | 'arquivo'; preview?: string }[]>([])
  const [promptAtivo, setPromptAtivo] = useState<string | null>(null)
  const [promptConteudo, setPromptConteudo] = useState<string | null>(null)
  const [menuAberto, setMenuAberto] = useState(true)
  const [imagemAtiva, setImagemAtiva] = useState<{ url: string; nome?: string } | null>(null)
  const [arteAtiva, setArteAtiva] = useState<{ url: string; nome?: string; overlay: NonNullable<Mensagem['overlay']> } | null>(null)
  const [erroExport, setErroExport] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const audioInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [mensagens])

  const handleSend = async () => {
    if ((!input.trim() && anexos.length === 0) || loading) return

    const textoEntrada = input.trim()
    const modoAtual = promptAtivo
    const deveGerarOverlay = Boolean(
      textoEntrada &&
      (modoAtual === 'REZETA' || modoAtual === 'FC') &&
      isImageRequest(textoEntrada)
    )
    const overlayText = deveGerarOverlay ? extractOverlaySource(textoEntrada) : null

    const userMsg: Mensagem = {
      id: Date.now().toString(),
      tipo: 'usuario',
      conteudo: textoEntrada || (anexos.length > 0 ? 'Anexos enviados:' : ''),
      timestamp: new Date(),
      anexos: anexos.map(a => ({ 
        tipo: a.tipo, 
        url: a.preview || '', 
        nome: a.file.name 
      })),
      modo: modoAtual || undefined
    }

    setMensagens(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      let resposta = ''

      // Processa anexos primeiro
      for (const anexo of anexos) {
        if (anexo.tipo === 'imagem') {
          const formData = new FormData()
          formData.append('file', anexo.file)
          formData.append('prompt', input.trim() || 'Descreva esta imagem em detalhes')
          const response = await api.post('/viva/vision/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          resposta += `📷 **Análise da imagem "${anexo.file.name}":**\n${response.data.analise}\n\n`
        } else if (anexo.tipo === 'audio') {
          const formData = new FormData()
          formData.append('file', anexo.file)
          const response = await api.post('/viva/audio/transcribe', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          resposta += `🎤 **Transcrição do áudio "${anexo.file.name}":**\n${response.data.transcricao}\n\n`
        }
      }

      // Se tiver mensagem de texto, processa
      if (textoEntrada) {
        const contexto = mensagens.slice(-10)
        const response = await api.post('/viva/chat', {
          mensagem: textoEntrada,
          contexto,
          prompt_extra: promptConteudo || undefined
        })
        resposta += response.data.resposta

        const midia = Array.isArray(response.data.midia) ? response.data.midia : []
        if (midia.length > 0) {
          const anexosIA = midia
            .filter((item: any) => item && item.url)
            .map((item: any) => ({
              tipo: item.tipo === 'imagem' ? 'imagem' : 'arquivo',
              url: item.url,
              nome: item.nome,
              meta: item.meta
            }))

          const overlayMeta = midia.find((item: any) => item?.meta?.overlay)?.meta?.overlay
          const overlayFromBackend = overlayMeta && (overlayMeta.brand === 'FC' || overlayMeta.brand === 'REZETA')
            ? {
                brand: overlayMeta.brand as 'FC' | 'REZETA',
                copy: {
                  headline: overlayMeta.headline,
                  subheadline: overlayMeta.subheadline,
                  bullets: Array.isArray(overlayMeta.bullets) ? overlayMeta.bullets : [],
                  quote: overlayMeta.quote,
                  cta: overlayMeta.cta
                }
              }
            : undefined

          const overlayFallback = overlayText && (modoAtual === 'REZETA' || modoAtual === 'FC')
            ? { brand: modoAtual as 'REZETA' | 'FC', text: overlayText }
            : undefined

          if (anexosIA.length > 0) {
            const iaMsg: Mensagem = {
              id: (Date.now() + 1).toString(),
              tipo: 'ia',
              conteudo: resposta || 'Processado com sucesso!',
              timestamp: new Date(),
              anexos: anexosIA,
              overlay: overlayFromBackend || overlayFallback
            }
            setMensagens(prev => [...prev, iaMsg])
            return
          }
        }
      }

      const iaMsg: Mensagem = {
        id: (Date.now() + 1).toString(),
        tipo: 'ia',
        conteudo: resposta || 'Processado com sucesso!',
        timestamp: new Date(),
        overlay: overlayText && (modoAtual === 'REZETA' || modoAtual === 'FC')
          ? { brand: modoAtual as 'REZETA' | 'FC', text: overlayText }
          : undefined
      }

      setMensagens(prev => [...prev, iaMsg])
    } catch (error) {
      const errorMsg: Mensagem = {
        id: (Date.now() + 1).toString(),
        tipo: 'ia',
        conteudo: 'Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?',
        timestamp: new Date()
      }
      setMensagens(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
      setAnexos([])
    }
  }

  const selecionarPrompt = async (promptId: string) => {
    setPromptAtivo(promptId)
    
    // Carrega o prompt
    try {
      const response = await fetch(`/viva/PROMPTS/${promptId}.md`)
      const texto = await response.text()
      setPromptConteudo(texto)
      
      const novoContexto = `Modo **${PROMPTS.find(p => p.id === promptId)?.titulo}** ativado!\n\nComo posso ajudar?`
      
      const iaMsg: Mensagem = {
        id: Date.now().toString(),
        tipo: 'ia',
        conteudo: novoContexto,
        timestamp: new Date()
      }
      
      setMensagens(prev => [...prev, iaMsg])
    } catch (e) {
      setPromptConteudo(null)
      // Se não conseguir carregar, apenas mostra mensagem
      const iaMsg: Mensagem = {
        id: Date.now().toString(),
        tipo: 'ia',
        conteudo: `Modo **${PROMPTS.find(p => p.id === promptId)?.titulo}** ativado!`,
        timestamp: new Date()
      }
      setMensagens(prev => [...prev, iaMsg])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, tipo: 'imagem' | 'audio' | 'arquivo') => {
    const files = e.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      const reader = new FileReader()
      reader.onload = () => {
        setAnexos(prev => [...prev, { 
          file, 
          tipo, 
          preview: tipo === 'imagem' ? reader.result as string : undefined 
        }])
      }
      if (tipo === 'imagem') {
        reader.readAsDataURL(file)
      } else {
        setAnexos(prev => [...prev, { file, tipo }])
      }
    })
  }

  const removeAnexo = (index: number) => {
    setAnexos(prev => prev.filter((_, i) => i !== index))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMensagens([{
      id: 'welcome',
      tipo: 'ia',
      conteudo: 'Olá! Sou a VIVA, assistente virtual da FC Soluções Financeiras. Como posso ajudar você hoje?\n\n💡 Selecione um modo especial no menu lateral ou envie uma mensagem diretamente.',
      timestamp: new Date()
    }])
    setPromptAtivo(null)
    setPromptConteudo(null)
  }

  const copyMessage = (id: string, texto: string) => {
    navigator.clipboard.writeText(texto)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const hexToRgba = (hex: string, alpha: number) => {
    const normalized = hex.replace('#', '')
    const bigint = parseInt(normalized, 16)
    const r = (bigint >> 16) & 255
    const g = (bigint >> 8) & 255
    const b = bigint & 255
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }

  const wrapText = (
    ctx: CanvasRenderingContext2D,
    text: string,
    x: number,
    y: number,
    maxWidth: number,
    lineHeight: number,
    maxLines?: number
  ) => {
    const words = text.split(' ')
    let line = ''
    let lines = 0
    let currentY = y

    words.forEach(word => {
      const testLine = `${line}${word} `
      const metrics = ctx.measureText(testLine)
      if (metrics.width > maxWidth && line) {
        ctx.fillText(line.trim(), x, currentY)
        line = `${word} `
        currentY += lineHeight
        lines += 1
        if (maxLines && lines >= maxLines) {
          line = ''
        }
      } else {
        line = testLine
      }
    })

    if (line && (!maxLines || lines < maxLines)) {
      ctx.fillText(line.trim(), x, currentY)
      currentY += lineHeight
    }

    return currentY
  }

  const exportarArte = async () => {
    if (!arteAtiva) return
    setErroExport(null)

    const theme = BRAND_THEMES[arteAtiva.overlay.brand]
    const parsed = parseOverlayText(arteAtiva.overlay)

    const image = new window.Image()
    image.crossOrigin = 'anonymous'

    const loadImage = () =>
      new Promise<void>((resolve, reject) => {
        image.onload = () => resolve()
        image.onerror = () => reject(new Error('Falha ao carregar imagem'))
        image.src = arteAtiva.url
      })

    try {
      await loadImage()
      const canvas = document.createElement('canvas')
      const width = image.naturalWidth || 1024
      const height = image.naturalHeight || 1024
      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        setErroExport('Nao foi possivel inicializar o canvas.')
        return
      }

      ctx.drawImage(image, 0, 0, width, height)

      const topHeight = Math.round(height * 0.26)
      const bottomHeight = Math.round(height * 0.3)
      const margin = Math.round(width * 0.06)

      ctx.fillStyle = hexToRgba(theme.light, 0.86)
      ctx.fillRect(0, 0, width, topHeight)

      const gradient = ctx.createLinearGradient(0, height - bottomHeight, width, height)
      gradient.addColorStop(0, hexToRgba(theme.dark, 0.9))
      gradient.addColorStop(1, hexToRgba(theme.accent, 0.9))
      ctx.fillStyle = gradient
      ctx.fillRect(0, height - bottomHeight, width, bottomHeight)

      ctx.fillStyle = theme.primary
      ctx.font = `bold ${Math.round(width * 0.045)}px Inter, Arial, sans-serif`
      wrapText(ctx, parsed.headline, margin, Math.round(topHeight * 0.35), width - margin * 2, Math.round(width * 0.055), 2)

      if (parsed.subheadline) {
        ctx.font = `${Math.round(width * 0.03)}px Inter, Arial, sans-serif`
        wrapText(ctx, parsed.subheadline, margin, Math.round(topHeight * 0.72), width - margin * 2, Math.round(width * 0.04), 2)
      }

      ctx.fillStyle = '#ffffff'
      ctx.font = `${Math.round(width * 0.028)}px Inter, Arial, sans-serif`
      let currentY = height - bottomHeight + Math.round(bottomHeight * 0.25)
      parsed.bullets.forEach((bullet) => {
        currentY = wrapText(ctx, bullet, margin, currentY, width - margin * 2, Math.round(width * 0.038), 2)
      })

      if (parsed.quote) {
        ctx.font = `italic ${Math.round(width * 0.025)}px Inter, Arial, sans-serif`
        wrapText(ctx, parsed.quote, margin, height - Math.round(bottomHeight * 0.18), width - margin * 2, Math.round(width * 0.035), 2)
      }

      const dataUrl = canvas.toDataURL('image/png')
      const link = document.createElement('a')
      link.href = dataUrl
      link.download = `arte-${arteAtiva.overlay.brand.toLowerCase()}.png`
      link.click()
    } catch (error) {
      setErroExport('Nao foi possivel exportar a imagem. Se a URL nao permitir CORS, use "Abrir imagem" e salve manualmente.')
    }
  }

  return (
    <>
      <div className="flex h-[calc(100vh-4rem)]">
      {/* Menu Lateral de Prompts */}
      <div className={`bg-gray-50 border-r transition-all duration-300 ${menuAberto ? 'w-64' : 'w-0 overflow-hidden'}`}>
        <div className="p-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Modos Especiais
          </h3>
          <div className="space-y-2">
            {PROMPTS.map((prompt) => (
              <button
                key={prompt.id}
                onClick={() => selecionarPrompt(prompt.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                  promptAtivo === prompt.id
                    ? 'bg-white shadow-md ring-2 ring-blue-500'
                    : 'bg-white hover:shadow-md border border-gray-200'
                }`}
              >
                <div className={`w-10 h-10 rounded-lg ${prompt.cor} flex items-center justify-center text-white`}>
                  {prompt.icone}
                </div>
                <div className="text-left">
                  <p className="font-medium text-sm">{prompt.titulo}</p>
                  <p className="text-xs text-gray-500">{prompt.descricao}</p>
                </div>
                {promptAtivo === prompt.id && (
                  <ChevronRight className="w-4 h-4 text-blue-500 ml-auto" />
                )}
              </button>
            ))}
          </div>
        </div>
        
        <div className="p-4 border-t">
          <p className="text-xs text-gray-400">
            Selecione um modo para ativar prompts especializados
          </p>
        </div>
      </div>

      {/* Área Principal do Chat */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-white">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMenuAberto(!menuAberto)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className={`w-5 h-5 transition-transform ${menuAberto ? 'rotate-180' : ''}`} />
            </button>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-lg">VIVA</h1>
              <p className="text-sm text-gray-500 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Assistente Virtual IA
                {promptAtivo && (
                  <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
                    {PROMPTS.find(p => p.id === promptAtivo)?.titulo}
                  </span>
                )}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={clearChat} className="text-gray-500">
            <Trash2 className="w-4 h-4 mr-2" />
            Limpar
          </Button>
        </div>

        {/* Área de mensagens */}
        <ScrollArea className="flex-1 px-4" ref={scrollRef}>
          <div className="max-w-3xl mx-auto py-6 space-y-6">
            {mensagens.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.tipo === 'usuario' ? 'flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.tipo === 'usuario' 
                    ? 'bg-gray-200' 
                    : 'bg-gradient-to-br from-blue-500 to-purple-600'
                }`}>
                  {msg.tipo === 'usuario' ? (
                    <User className="w-4 h-4 text-gray-600" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>

                {/* Mensagem */}
                <div className={`group relative max-w-[80%] ${
                  msg.tipo === 'usuario' ? 'items-end' : 'items-start'
                }`}>
                  <div className={`px-4 py-3 rounded-2xl ${
                    msg.tipo === 'usuario'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-800 rounded-bl-none'
                  }`}>
                    <p className="whitespace-pre-wrap">{msg.conteudo}</p>
                    
                    {/* Anexos */}
                    {msg.anexos && msg.anexos.length > 0 && (
                      <div className="mt-2 space-y-2">
                        {msg.anexos.map((anexo, idx) => (
                          <div key={idx}>
                            {anexo.tipo === 'imagem' && anexo.url && (
                              <div className="space-y-2">
                                <img 
                                  src={anexo.url} 
                                  alt={anexo.nome || 'Imagem'} 
                                  className="max-w-sm sm:max-w-md rounded-lg cursor-zoom-in"
                                  onClick={() => setImagemAtiva({ url: anexo.url, nome: anexo.nome })}
                                />
                                {msg.overlay && (
                                  <button
                                    onClick={() => {
                                      setArteAtiva({ url: anexo.url, nome: anexo.nome, overlay: msg.overlay! })
                                      setErroExport(null)
                                    }}
                                    className="text-xs text-blue-600 hover:text-blue-800"
                                  >
                                    Ver arte final
                                  </button>
                                )}
                              </div>
                            )}
                            {anexo.tipo === 'audio' && (
                              <div className="flex items-center gap-2 text-sm bg-black/10 px-3 py-2 rounded">
                                <Mic className="w-4 h-4" />
                                {anexo.nome}
                              </div>
                            )}
                            {anexo.tipo === 'arquivo' && (
                              <div className="flex items-center gap-2 text-sm bg-black/10 px-3 py-2 rounded">
                                <FileUp className="w-4 h-4" />
                                {anexo.nome}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Ações */}
                  <div className="flex items-center gap-2 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs text-gray-400">
                      {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {msg.tipo === 'ia' && (
                      <button
                        onClick={() => copyMessage(msg.id, msg.conteudo)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        {copiedId === msg.id ? (
                          <Check className="w-3 h-3 text-green-500" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-none">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Anexos selecionados */}
        {anexos.length > 0 && (
          <div className="px-4 py-2 border-t bg-gray-50">
            <div className="flex gap-2 overflow-x-auto">
              {anexos.map((anexo, idx) => (
                <div key={idx} className="relative flex-shrink-0">
                  {anexo.tipo === 'imagem' && anexo.preview ? (
                    <img 
                      src={anexo.preview} 
                      alt="Preview" 
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                      {anexo.tipo === 'audio' ? <Mic className="w-6 h-6" /> : <FileUp className="w-6 h-6" />}
                    </div>
                  )}
                  <button
                    onClick={() => removeAnexo(idx)}
                    className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="p-4 border-t bg-white">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              {/* Botões de anexo */}
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-gray-500"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <ImageIcon className="w-5 h-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-gray-500"
                  onClick={() => audioInputRef.current?.click()}
                >
                  <Mic className="w-5 h-5" />
                </Button>
              </div>
              
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Digite sua mensagem para a VIVA..."
                className="flex-1 px-4 py-3 border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={1}
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
              <Button
                onClick={handleSend}
                disabled={(!input.trim() && anexos.length === 0) || loading}
                className="px-4 h-12"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
            
            {/* Inputs escondidos */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => handleFileSelect(e, 'imagem')}
            />
            <input
              ref={audioInputRef}
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={(e) => handleFileSelect(e, 'audio')}
            />
            
            <p className="text-center text-xs text-gray-400 mt-2">
              VIVA pode cometer erros. Verifique informações importantes.
            </p>
          </div>
        </div>
      </div>
    </div>

      {imagemAtiva && (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-6"
        onClick={() => setImagemAtiva(null)}
      >
        <div
          className="relative max-w-5xl w-full"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => setImagemAtiva(null)}
            className="absolute -top-10 right-0 text-white hover:text-gray-200"
            aria-label="Fechar imagem"
          >
            <X className="w-6 h-6" />
          </button>
          <img
            src={imagemAtiva.url}
            alt={imagemAtiva.nome || 'Imagem ampliada'}
            className="w-full h-auto rounded-lg"
          />
        </div>
      </div>
      )}

      {arteAtiva && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-6"
          onClick={() => setArteAtiva(null)}
        >
          <div
            className="relative w-full max-w-5xl rounded-lg bg-white p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Arte final</h2>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => window.open(arteAtiva.url, '_blank')}>
                  Abrir imagem
                </Button>
                <Button size="sm" onClick={exportarArte}>
                  Baixar PNG
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setArteAtiva(null)}>
                  Fechar
                </Button>
              </div>
            </div>

            {erroExport && (
              <p className="mb-3 text-sm text-red-600">{erroExport}</p>
            )}

            {(() => {
              const theme = BRAND_THEMES[arteAtiva.overlay.brand]
              const parsed = parseOverlayText(arteAtiva.overlay)

              return (
                <div className="relative w-full aspect-square overflow-hidden rounded-lg border">
                  <img
                    src={arteAtiva.url}
                    alt={arteAtiva.nome || 'Arte gerada'}
                    className="absolute inset-0 h-full w-full object-cover"
                  />
                  <div className="absolute inset-x-0 top-0 h-[26%] bg-white/85 px-6 py-4">
                    <p className="text-xs uppercase tracking-widest" style={{ color: theme.accent }}>
                      {theme.label}
                    </p>
                    <h3 className="mt-2 text-lg sm:text-2xl font-bold" style={{ color: theme.primary }}>
                      {parsed.headline}
                    </h3>
                    {parsed.subheadline && (
                      <p className="mt-1 text-sm sm:text-base" style={{ color: theme.primary }}>
                        {parsed.subheadline}
                      </p>
                    )}
                  </div>
                  <div
                    className="absolute inset-x-0 bottom-0 h-[30%] px-6 py-4 text-white"
                    style={{
                      background: `linear-gradient(90deg, ${theme.dark}e6, ${theme.accent}e6)`
                    }}
                  >
                    <ul className="space-y-1 text-xs sm:text-sm">
                      {parsed.bullets.map((bullet, idx) => (
                        <li key={idx}>{bullet}</li>
                      ))}
                    </ul>
                    {parsed.quote && (
                      <p className="mt-3 text-xs sm:text-sm italic">{parsed.quote}</p>
                    )}
                    {parsed.cta && (
                      <p className="mt-3 inline-block rounded-full bg-white/20 px-3 py-1 text-xs sm:text-sm font-semibold tracking-wide">
                        {parsed.cta}
                      </p>
                    )}
                  </div>
                </div>
              )
            })()}
          </div>
        </div>
      )}
    </>
  )
}

'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, Trash2, Copy, Check, ImageIcon, Mic, X, FileUp, Layout, Palette, Image, FileText, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { api } from '@/lib/api'

interface Mensagem {
  id: string
  tipo: 'usuario' | 'ia'
  conteudo: string
  timestamp: Date
  anexos?: { tipo: 'imagem' | 'audio' | 'arquivo'; url: string; nome?: string }[]
  modo?: string
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
    icone: <Image className="w-5 h-5" />,
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

    const userMsg: Mensagem = {
      id: Date.now().toString(),
      tipo: 'usuario',
      conteudo: input.trim() || (anexos.length > 0 ? 'Anexos enviados:' : ''),
      timestamp: new Date(),
      anexos: anexos.map(a => ({ 
        tipo: a.tipo, 
        url: a.preview || '', 
        nome: a.file.name 
      })),
      modo: promptAtivo || undefined
    }

    setMensagens(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      let resposta = ''

      // Processa anexos primeiro
      for (const anexo of anexos) {
        if (anexo.tipo === 'imagem') {
          const base64 = await fileToBase64(anexo.file)
          const response = await api.post('/viva/vision', {
            image_base64: base64.split(',')[1],
            prompt: input.trim() || 'Descreva esta imagem em detalhes'
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
      if (input.trim()) {
        const contexto = mensagens.slice(-10)
        const response = await api.post('/viva/chat', {
          mensagem: input.trim(),
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
              nome: item.nome
            }))

          if (anexosIA.length > 0) {
            const iaMsg: Mensagem = {
              id: (Date.now() + 1).toString(),
              tipo: 'ia',
              conteudo: resposta || 'Processado com sucesso!',
              timestamp: new Date(),
              anexos: anexosIA
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
        timestamp: new Date()
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

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
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
                              <img 
                                src={anexo.url} 
                                alt={anexo.nome || 'Imagem'} 
                                className="max-w-sm sm:max-w-md rounded-lg cursor-zoom-in"
                                onClick={() => setImagemAtiva({ url: anexo.url, nome: anexo.nome })}
                              />
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
    </>
  )
}

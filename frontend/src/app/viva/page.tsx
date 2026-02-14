'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import Image from 'next/image'
import { Send, Bot, User, Sparkles, Trash2, Copy, Check, ImageIcon, Mic, X, FileUp, ChevronRight, Volume2, VolumeX } from 'lucide-react'
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
    formato?: string
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

interface SnapshotMessage {
  id: string
  tipo: 'usuario' | 'ia'
  conteudo: string
  modo?: string | null
  anexos?: { tipo: 'imagem' | 'audio' | 'arquivo'; url: string; nome?: string; meta?: any }[]
  meta?: Record<string, any>
  created_at: string
}

interface ChatSnapshot {
  session_id: string | null
  modo?: string | null
  messages: SnapshotMessage[]
}

interface ChatSessionSummary {
  id: string
  modo?: string | null
  message_count: number
  created_at: string
  updated_at: string
  last_message_at: string
}

interface ChatSessionListResponse {
  items: ChatSessionSummary[]
  total: number
  page: number
  page_size: number
}

interface ContinuousCaptureState {
  stream: MediaStream
  recorder: MediaRecorder
  chunks: BlobPart[]
  mimeType: string
  audioContext: AudioContext | null
  sourceNode: MediaStreamAudioSourceNode | null
  analyser: AnalyserNode | null
  dataArray: Uint8Array | null
  rafId: number | null
  timeoutId: number | null
  hasSpeech: boolean
  lastSpeechTs: number
  startedAt: number
  stopping: boolean
}

type ComposerAnexo = { file: File; tipo: 'imagem' | 'audio' | 'arquivo'; preview?: string }
type SendOptions = {
  textoOverride?: string
  anexosOverride?: ComposerAnexo[]
}

const inferBrandMode = (text: string): 'FC' | 'REZETA' | null => {
  const normalized = String(text || '').toLowerCase()
  if (!normalized) return null
  if (normalized.includes('rezeta')) return 'REZETA'
  // Detecta "fc" como sigla (evita pegar trechos aleatorios)
  if (/(^|\s|[^a-z0-9])fc(\s|[^a-z0-9]|$)/i.test(normalized)) return 'FC'
  if (normalized.includes('fc solucoes') || normalized.includes('fc solucoes financeiras')) return 'FC'
  return null
}

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
  const clamp = (value: string, max: number) => {
    const text = (value || '').trim()
    if (text.length <= max) return text
    return `${text.slice(0, max - 3).trim()}...`
  }

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
      bullets: (overlay.copy?.bullets || []).slice(0, 4),
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

  const headline = lines.find(line => !/^(âœ…|âŒ|âš ï¸|â€¢|-)/.test(line) && !line.startsWith('"') && !line.startsWith('â€œ')) || lines[0] || 'Mensagem principal'
  const quote = lines.find(line => line.startsWith('"') || line.startsWith('â€œ'))
  const bulletLines = lines.filter(line => /^(âœ…|âŒ|âš ï¸|â€¢|-)/.test(line))
  const remaining = lines.filter(line => line !== headline && line !== quote && !bulletLines.includes(line))
  const subheadline = remaining[0] || ''

  return {
    headline: clamp(headline, 140),
    subheadline: clamp(subheadline, 200),
    bullets: bulletLines.slice(0, 4).map(line => clamp(line, 140)),
    quote: clamp(quote || '', 180),
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

const VIVA_AVATAR_SOURCES = ['/viva-avatar-official.jpg', '/viva-avatar-official.png', '/viva-avatar.png', '/viva-avatar-3d.png', '/viva.png']

const createWelcomeMessage = (): Mensagem => ({
  id: 'welcome',
  tipo: 'ia',
  conteudo: 'Oi, Fabio. Viva aqui. O que voce precisa agora?',
  timestamp: new Date()
})

const extractOverlayFromAnexos = (anexos?: Mensagem['anexos']): Mensagem['overlay'] | undefined => {
  const first = Array.isArray(anexos) && anexos.length > 0 ? anexos[0] : undefined
  const overlayMeta = first?.meta?.overlay
  if (!overlayMeta || (overlayMeta.brand !== 'FC' && overlayMeta.brand !== 'REZETA')) {
    return undefined
  }

  return {
    brand: overlayMeta.brand as 'FC' | 'REZETA',
    formato: overlayMeta.formato,
    copy: {
      headline: overlayMeta.headline,
      subheadline: overlayMeta.subheadline,
      bullets: Array.isArray(overlayMeta.bullets) ? overlayMeta.bullets : [],
      quote: overlayMeta.quote,
      cta: overlayMeta.cta
    }
  }
}

const mapSnapshotMessages = (messages: SnapshotMessage[] = []): Mensagem[] => {
  return messages.map((item) => {
    const anexos: Mensagem['anexos'] = Array.isArray(item.anexos)
      ? item.anexos
          .filter((anexo) => anexo && typeof anexo.url === 'string' && anexo.url.trim().length > 0)
          .map((anexo) => {
            const tipo: 'imagem' | 'audio' | 'arquivo' =
              anexo.tipo === 'imagem' || anexo.tipo === 'audio' ? anexo.tipo : 'arquivo'
            return {
              tipo,
            url: anexo.url,
            nome: anexo.nome,
            meta: anexo.meta
            }
          })
      : undefined

    const overlay = extractOverlayFromAnexos(anexos) || (
      item.meta?.overlay && (item.meta.overlay.brand === 'FC' || item.meta.overlay.brand === 'REZETA')
        ? {
            brand: item.meta.overlay.brand as 'FC' | 'REZETA',
            formato: item.meta.overlay.formato,
            copy: {
              headline: item.meta.overlay.headline,
              subheadline: item.meta.overlay.subheadline,
              bullets: Array.isArray(item.meta.overlay.bullets) ? item.meta.overlay.bullets : [],
              quote: item.meta.overlay.quote,
              cta: item.meta.overlay.cta
            }
          }
        : undefined
    )

    return {
      id: String(item.id),
      tipo: item.tipo,
      conteudo: item.conteudo || '',
      timestamp: item.created_at ? new Date(item.created_at) : new Date(),
      modo: item.modo || undefined,
      anexos,
      overlay
    }
  })
}

export default function VivaChatPage() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([createWelcomeMessage()])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [gravandoAudio, setGravandoAudio] = useState(false)
  const [erroAudio, setErroAudio] = useState<string | null>(null)
  const [pendingAudioAutoSend, setPendingAudioAutoSend] = useState<ComposerAnexo | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSessionSummary[]>([])
  const [loadingSessions, setLoadingSessions] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [anexos, setAnexos] = useState<ComposerAnexo[]>([])
  const [menuAberto, setMenuAberto] = useState(true)
  const [modoConversacaoAtivo, setModoConversacaoAtivo] = useState(false)
  const [vozVivaAtiva, setVozVivaAtiva] = useState(true)
  const [ttsProviderConfigured, setTtsProviderConfigured] = useState(false)
  const [ttsMissingEnv, setTtsMissingEnv] = useState<string[]>([])
  const [escutaContinuaAtiva, setEscutaContinuaAtiva] = useState(false)
  const [transcricaoParcial, setTranscricaoParcial] = useState('')
  const [avatarFallback, setAvatarFallback] = useState(false)
  const [avatarSourceIndex, setAvatarSourceIndex] = useState(0)
  const [imagemAtiva, setImagemAtiva] = useState<{ url: string; nome?: string } | null>(null)
  const [arteAtiva, setArteAtiva] = useState<{ url: string; nome?: string; overlay: NonNullable<Mensagem['overlay']> } | null>(null)
  const [erroExport, setErroExport] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textAreaRef = useRef<HTMLTextAreaElement>(null)
  const holoStageRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioChunksRef = useRef<BlobPart[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const audioInputRef = useRef<HTMLInputElement>(null)
  const playbackAudioRef = useRef<HTMLAudioElement | null>(null)
  const lastSpokenMessageIdRef = useRef<string | null>(null)
  const speechRecognitionRef = useRef<any>(null)
  const continuousCaptureRef = useRef<ContinuousCaptureState | null>(null)
  const continuousStartInFlightRef = useRef(false)
  const conversationShouldListenRef = useRef(false)
  const assistantSpeakingRef = useRef(false)
  const loadingRef = useRef(false)
  const modoConversacaoRef = useRef(false)
  const sendFromVoiceRef = useRef<(text: string) => void>(() => {})
  const startContinuousConversationRef = useRef<() => void>(() => {})

  const INPUT_MIN_HEIGHT = 88
  const INPUT_MAX_HEIGHT = 220

  const formatSessionLabel = (session: ChatSessionSummary) => {
    const dt = new Date(session.last_message_at || session.updated_at || session.created_at)
    const dateLabel = Number.isNaN(dt.getTime())
      ? 'sem data'
      : dt.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
    return `${dateLabel} | ${session.message_count} msg`
  }

  const scrollToBottom = useCallback((smooth = false) => {
    const behavior: ScrollBehavior = smooth ? 'smooth' : 'auto'
    const viewport = scrollAreaRef.current?.querySelector('[data-radix-scroll-area-viewport]') as HTMLDivElement | null
    if (viewport) {
      viewport.scrollTo({ top: viewport.scrollHeight, behavior })
    } else if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior })
    }
    messagesEndRef.current?.scrollIntoView({ block: 'end', behavior })
  }, [])

  const loadSessions = useCallback(async (selectedSessionId?: string | null) => {
    setLoadingSessions(true)
    try {
      const response = await api.get<ChatSessionListResponse>('/viva/chat/sessions', {
        params: { page: 1, page_size: 30 }
      })
      const items = Array.isArray(response.data?.items) ? response.data.items : []
      setChatSessions(items)

      if (items.length > 0 && !selectedSessionId) {
        setSessionId((prev) => prev || items[0].id)
      }
    } catch {
      setChatSessions([])
    } finally {
      setLoadingSessions(false)
    }
  }, [])

  const loadSessionSnapshot = useCallback(async (targetSessionId: string) => {
    try {
      const response = await api.get<ChatSnapshot>('/viva/chat/snapshot', {
        params: { session_id: targetSessionId, limit: 180 }
      })
      const snapshot = response.data
      const restoredMessages = mapSnapshotMessages(snapshot?.messages || [])

      setSessionId(snapshot?.session_id || targetSessionId)
      setMensagens(restoredMessages.length > 0 ? restoredMessages : [createWelcomeMessage()])
      requestAnimationFrame(() => scrollToBottom())
    } catch {
      // Mantem sessao atual em caso de erro de leitura.
    }
  }, [scrollToBottom])

  const releaseContinuousCapture = useCallback((state: ContinuousCaptureState | null) => {
    if (!state) return
    state.stopping = true
    if (state.rafId !== null) {
      window.cancelAnimationFrame(state.rafId)
      state.rafId = null
    }
    if (state.timeoutId !== null) {
      window.clearTimeout(state.timeoutId)
      state.timeoutId = null
    }
    if (state.sourceNode) {
      try {
        state.sourceNode.disconnect()
      } catch {
        // no-op
      }
    }
    if (state.analyser) {
      try {
        state.analyser.disconnect()
      } catch {
        // no-op
      }
    }
    if (state.audioContext && state.audioContext.state !== 'closed') {
      state.audioContext.close().catch(() => undefined)
    }
    state.stream.getTracks().forEach(track => track.stop())
  }, [])

  const transcribeAudioBlob = useCallback(async (audioBlob: Blob): Promise<string> => {
    if (!audioBlob.size) return ''
    const ext = audioBlob.type.includes('mp4') ? 'm4a' : 'webm'
    const stamp = new Date().toISOString().replace(/[:.]/g, '-')
    const audioFile = new File([audioBlob], `conversa-${stamp}.${ext}`, { type: audioBlob.type || 'audio/webm' })
    const formData = new FormData()
    formData.append('file', audioFile)
    const response = await api.post('/viva/audio/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return String(response.data?.transcricao || '').trim()
  }, [])

  const startBrowserContinuousConversation = useCallback(() => {
    const SpeechCtor = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechCtor) {
      setErroAudio('Seu navegador nao suporta voz continua. Use Chrome ou Edge atualizado.')
      return
    }

    if (!speechRecognitionRef.current) {
      const recognition = new SpeechCtor()
      recognition.lang = 'pt-BR'
      recognition.continuous = true
      recognition.interimResults = true
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        setEscutaContinuaAtiva(true)
      }

      recognition.onresult = (event: any) => {
        let interimText = ''
        let finalText = ''

        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const result = event.results[i]
          const transcript = String(result?.[0]?.transcript || '').trim()
          if (!transcript) continue

          if (result.isFinal) {
            finalText += `${transcript} `
          } else {
            interimText += `${transcript} `
          }
        }

        setTranscricaoParcial(interimText.trim())
        const textoFinal = finalText.trim()
        if (!textoFinal) return

        setTranscricaoParcial('')
        conversationShouldListenRef.current = false
        try {
          recognition.stop()
        } catch {
          // no-op
        }

        if (!loadingRef.current) {
          sendFromVoiceRef.current(textoFinal)
        }
      }

      recognition.onerror = (event: any) => {
        const code = String(event?.error || '')
        if (code === 'no-speech' || code === 'aborted') return
        if (code === 'not-allowed' || code === 'service-not-allowed') {
          setErroAudio('Permissao de microfone negada. Ative o microfone no navegador para usar conversa continua.')
          conversationShouldListenRef.current = false
          return
        }
        setErroAudio('Falha de reconhecimento no navegador. Tentando reconectar.')
      }

      recognition.onend = () => {
        setEscutaContinuaAtiva(false)
        setTranscricaoParcial('')
        if (!conversationShouldListenRef.current) return
        if (!modoConversacaoRef.current || loadingRef.current || assistantSpeakingRef.current) return

        window.setTimeout(() => {
          if (!conversationShouldListenRef.current) return
          if (!modoConversacaoRef.current || loadingRef.current || assistantSpeakingRef.current) return
          try {
            recognition.start()
          } catch {
            // no-op
          }
        }, 260)
      }

      speechRecognitionRef.current = recognition
    }

    setErroAudio('Usando fallback de reconhecimento do navegador.')
    try {
      speechRecognitionRef.current.start()
    } catch (error) {
      const msg = String(error || '')
      if (!/already started/i.test(msg)) {
        setErroAudio('Nao foi possivel iniciar a escuta continua agora.')
      }
    }
  }, [])

  const startServerContinuousConversation = useCallback(async (): Promise<boolean> => {
    if (typeof window === 'undefined') return false
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') return false
    if (continuousCaptureRef.current || continuousStartInFlightRef.current) return true

    continuousStartInFlightRef.current = true
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      })

      const preferredMime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : ''
      const recorder = preferredMime ? new MediaRecorder(stream, { mimeType: preferredMime }) : new MediaRecorder(stream)

      const state: ContinuousCaptureState = {
        stream,
        recorder,
        chunks: [],
        mimeType: recorder.mimeType || 'audio/webm',
        audioContext: null,
        sourceNode: null,
        analyser: null,
        dataArray: null,
        rafId: null,
        timeoutId: null,
        hasSpeech: false,
        lastSpeechTs: Date.now(),
        startedAt: Date.now(),
        stopping: false,
      }
      continuousCaptureRef.current = state
      setEscutaContinuaAtiva(true)
      setTranscricaoParcial('Escutando...')
      setErroAudio(null)

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          state.chunks.push(event.data)
        }
      }

      recorder.onerror = () => {
        setErroAudio('Falha ao capturar audio continuo. Retornando ao modo de fallback.')
      }

      recorder.onstop = () => {
        const audioBlob = new Blob(state.chunks, { type: state.mimeType })
        const hadSpeech = state.hasSpeech
        const shouldContinue = conversationShouldListenRef.current && modoConversacaoRef.current
        releaseContinuousCapture(state)
        if (continuousCaptureRef.current === state) {
          continuousCaptureRef.current = null
        }
        continuousStartInFlightRef.current = false
        setEscutaContinuaAtiva(false)
        setTranscricaoParcial('')

        if (!shouldContinue || assistantSpeakingRef.current || loadingRef.current) {
          return
        }

        const resume = () => {
          window.setTimeout(() => {
            if (!conversationShouldListenRef.current) return
            if (!modoConversacaoRef.current || loadingRef.current || assistantSpeakingRef.current) return
            startContinuousConversationRef.current()
          }, 260)
        }

        if (!hadSpeech || !audioBlob.size) {
          resume()
          return
        }

        void (async () => {
          try {
            const texto = await transcribeAudioBlob(audioBlob)
            if (texto) {
              conversationShouldListenRef.current = false
              sendFromVoiceRef.current(texto)
              return
            }
            resume()
          } catch {
            resume()
          }
        })()
      }

      const AudioContextCtor = (window as any).AudioContext || (window as any).webkitAudioContext
      if (AudioContextCtor) {
        const audioContext: AudioContext = new AudioContextCtor()
        const sourceNode = audioContext.createMediaStreamSource(stream)
        const analyser = audioContext.createAnalyser()
        analyser.fftSize = 1024
        sourceNode.connect(analyser)
        const dataArray = new Uint8Array(analyser.fftSize)

        state.audioContext = audioContext
        state.sourceNode = sourceNode
        state.analyser = analyser
        state.dataArray = dataArray

        const detectSpeech = () => {
          if (state.stopping) return
          analyser.getByteTimeDomainData(dataArray)
          let sum = 0
          for (let i = 0; i < dataArray.length; i += 1) {
            const normalized = (dataArray[i] - 128) / 128
            sum += normalized * normalized
          }
          const rms = Math.sqrt(sum / dataArray.length)
          const now = Date.now()
          if (rms > 0.018) {
            state.hasSpeech = true
            state.lastSpeechTs = now
          }

          const elapsed = now - state.startedAt
          const silenceMs = now - state.lastSpeechTs
          if ((state.hasSpeech && silenceMs > 1150 && elapsed > 1000) || elapsed > 12000) {
            state.stopping = true
            if (recorder.state !== 'inactive') {
              try {
                recorder.stop()
              } catch {
                // no-op
              }
            }
            return
          }
          state.rafId = window.requestAnimationFrame(detectSpeech)
        }
        state.rafId = window.requestAnimationFrame(detectSpeech)
      } else {
        state.timeoutId = window.setTimeout(() => {
          state.stopping = true
          if (recorder.state !== 'inactive') {
            try {
              recorder.stop()
            } catch {
              // no-op
            }
          }
        }, 7000)
      }

      recorder.start(250)
      return true
    } catch {
      const state = continuousCaptureRef.current
      if (state) {
        releaseContinuousCapture(state)
      }
      continuousCaptureRef.current = null
      continuousStartInFlightRef.current = false
      return false
    }
  }, [releaseContinuousCapture, transcribeAudioBlob])

  const stopContinuousConversation = useCallback((clearIntent = true) => {
    if (clearIntent) {
      conversationShouldListenRef.current = false
    }

    continuousStartInFlightRef.current = false
    const captureState = continuousCaptureRef.current
    if (captureState) {
      captureState.stopping = true
      if (captureState.recorder.state !== 'inactive') {
        try {
          captureState.recorder.stop()
        } catch {
          // no-op
        }
      }
      releaseContinuousCapture(captureState)
      continuousCaptureRef.current = null
    }

    const recognition = speechRecognitionRef.current
    if (recognition) {
      try {
        recognition.stop()
      } catch {
        // Ignora erro de stop em estados transientes.
      }
    }

    setEscutaContinuaAtiva(false)
    setTranscricaoParcial('')
  }, [releaseContinuousCapture])

  const startContinuousConversation = useCallback(() => {
    if (typeof window === 'undefined') return
    if (!modoConversacaoRef.current || loadingRef.current || assistantSpeakingRef.current) return

    conversationShouldListenRef.current = true
    if (continuousCaptureRef.current || continuousStartInFlightRef.current) return

    void (async () => {
      const startedServer = await startServerContinuousConversation()
      if (!startedServer) {
        startBrowserContinuousConversation()
      }
    })()
  }, [startBrowserContinuousConversation, startServerContinuousConversation])

  useEffect(() => {
    startContinuousConversationRef.current = () => {
      startContinuousConversation()
    }
  }, [startContinuousConversation])

  const stopAssistantPlayback = useCallback(() => {
    const currentAudio = playbackAudioRef.current
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.src = ''
      playbackAudioRef.current = null
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }, [])

  useEffect(() => {
    let active = true

    const restoreSnapshot = async () => {
      let restoredSessionId: string | null = null
      try {
        const response = await api.get<ChatSnapshot>('/viva/chat/snapshot', {
          params: { limit: 120 }
        })
        if (!active) return

        const snapshot = response.data
        const restoredMessages = mapSnapshotMessages(snapshot?.messages || [])
        restoredSessionId = snapshot?.session_id || null

        if (snapshot?.session_id) {
          setSessionId(snapshot.session_id)
        }

        if (restoredMessages.length > 0) {
          setMensagens(restoredMessages)
        } else {
          setMensagens([createWelcomeMessage()])
        }
      } catch {
        if (active) {
          setMensagens([createWelcomeMessage()])
        }
      }

      if (active) {
        await loadSessions(restoredSessionId)
      }
    }

    restoreSnapshot()
    return () => {
      active = false
    }
  }, [loadSessions])

  useEffect(() => {
    let mounted = true
    const loadTtsStatus = async () => {
      try {
        const response = await api.get('/viva/status')
        const configured = Boolean(response?.data?.tts?.configured)
        const missing = Array.isArray(response?.data?.tts?.missing_env) ? response.data.tts.missing_env : []
        if (mounted) {
          setTtsProviderConfigured(configured)
          setTtsMissingEnv(missing)
        }
      } catch {
        if (mounted) {
          setTtsProviderConfigured(false)
          setTtsMissingEnv([])
        }
      }
    }
    void loadTtsStatus()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    requestAnimationFrame(() => scrollToBottom())
  }, [mensagens, loading, scrollToBottom])

  useEffect(() => {
    const textarea = textAreaRef.current
    if (!textarea) return
    textarea.style.height = 'auto'
    const nextHeight = Math.min(Math.max(textarea.scrollHeight, INPUT_MIN_HEIGHT), INPUT_MAX_HEIGHT)
    textarea.style.height = `${nextHeight}px`
  }, [input])

  useEffect(() => {
    loadingRef.current = loading
  }, [loading])

  useEffect(() => {
    modoConversacaoRef.current = modoConversacaoAtivo
  }, [modoConversacaoAtivo])

  useEffect(() => {
    if (!modoConversacaoAtivo) {
      stopContinuousConversation()
      return
    }

    conversationShouldListenRef.current = true
    startContinuousConversation()
  }, [modoConversacaoAtivo, startContinuousConversation, stopContinuousConversation])

  useEffect(() => {
    if (!modoConversacaoAtivo) return
    if (loading || assistantSpeakingRef.current) return
    if (!conversationShouldListenRef.current) {
      conversationShouldListenRef.current = true
    }
    startContinuousConversation()
  }, [loading, modoConversacaoAtivo, startContinuousConversation])

  useEffect(() => {
    return () => {
      stopContinuousConversation()
      speechRecognitionRef.current = null
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      mediaStreamRef.current?.getTracks().forEach(track => track.stop())
      stopAssistantPlayback()
    }
  }, [stopAssistantPlayback, stopContinuousConversation])

  useEffect(() => {
    if (!modoConversacaoAtivo || !vozVivaAtiva) return

    const ultimaMensagemIA = [...mensagens].reverse().find(msg => msg.tipo === 'ia')
    if (!ultimaMensagemIA) return
    if (lastSpokenMessageIdRef.current === ultimaMensagemIA.id) return

    const texto = String(ultimaMensagemIA.conteudo || '').replace(/\*\*/g, '').trim()
    if (!texto) return

    let cancelled = false

    const finishSpeech = () => {
      assistantSpeakingRef.current = false
      if (modoConversacaoRef.current) {
        conversationShouldListenRef.current = true
        startContinuousConversation()
      }
    }

    const beginSpeech = () => {
      assistantSpeakingRef.current = true
      if (modoConversacaoRef.current) {
        conversationShouldListenRef.current = true
        stopContinuousConversation(false)
      }
    }

    const speakWithBrowserFallback = async () => {
      if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
        return
      }

      await new Promise<void>((resolve) => {
        const utterance = new SpeechSynthesisUtterance(texto)
        utterance.lang = 'pt-BR'
        utterance.rate = 1
        utterance.pitch = 1.03

        const voices = window.speechSynthesis.getVoices()
        const preferredVoice =
          voices.find(voice => /pt-BR/i.test(voice.lang) && /(female|maria|luciana|francisca|helena)/i.test(voice.name)) ||
          voices.find(voice => /pt-BR/i.test(voice.lang))
        if (preferredVoice) {
          utterance.voice = preferredVoice
        }

        utterance.onend = () => resolve()
        utterance.onerror = () => resolve()
        window.speechSynthesis.cancel()
        window.speechSynthesis.speak(utterance)
      })
    }

    const speakWithMinimax = async (): Promise<boolean> => {
      try {
        const response = await api.post('/viva/audio/speak', { text: texto }, { responseType: 'blob' })
        const mediaType = String(response.headers?.['content-type'] || 'audio/mpeg')
        const blob = new Blob([response.data], { type: mediaType })
        if (!blob.size) return false

        const url = URL.createObjectURL(blob)
        const audio = new Audio(url)
        playbackAudioRef.current = audio

        await new Promise<void>((resolve) => {
          audio.onended = () => {
            URL.revokeObjectURL(url)
            resolve()
          }
          audio.onerror = () => {
            URL.revokeObjectURL(url)
            resolve()
          }
          void audio.play().catch(() => {
            URL.revokeObjectURL(url)
            resolve()
          })
        })

        playbackAudioRef.current = null
        return true
      } catch {
        return false
      }
    }

    const run = async () => {
      beginSpeech()
      stopAssistantPlayback()
      let spoke = await speakWithMinimax()
      if (!spoke) {
        await speakWithBrowserFallback()
        if (ttsProviderConfigured) {
          setErroAudio('MiniMax indisponivel no momento. Usei a voz do navegador como fallback.')
        }
      }
      if (cancelled) return
      finishSpeech()
      lastSpokenMessageIdRef.current = ultimaMensagemIA.id
    }

    void run()

    return () => {
      cancelled = true
      stopAssistantPlayback()
    }
  }, [mensagens, modoConversacaoAtivo, vozVivaAtiva, startContinuousConversation, stopContinuousConversation, stopAssistantPlayback, ttsProviderConfigured])

  const handleSendStream = useCallback(async (
    mensagemComReferencia: string,
    contexto: any[],
    sessionIdAtual: string | null
  ) => {
    try {
      const response = await fetch('/api/v1/viva/chat/stream', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mensagem: mensagemComReferencia,
          contexto,
          session_id: sessionIdAtual || undefined
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      if (!response.body) {
        throw new Error('Response body not available')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      // Criar mensagem do assistente que será atualizada
      const assistantMsgId = (Date.now() + 1).toString()
      setMensagens(prev => [...prev, {
        id: assistantMsgId,
        tipo: 'ia',
        conteudo: '',
        timestamp: new Date(),
        streaming: true
      }])

      let fullResponse = ''
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue

          try {
            const data = JSON.parse(line.slice(6))

            if (data.error) {
              throw new Error(data.error)
            }

            if (data.content) {
              fullResponse += data.content
              setMensagens(prev => prev.map(msg =>
                msg.id === assistantMsgId
                  ? { ...msg, conteudo: fullResponse }
                  : msg
              ))
            }

            if (data.done) {
              setMensagens(prev => prev.map(msg =>
                msg.id === assistantMsgId
                  ? { ...msg, streaming: false }
                  : msg
              ))
              if (data.session_id) {
                setSessionId(data.session_id)
                void loadSessions(data.session_id)
              }
              return true
            }
          } catch (e) {
            console.error('Error parsing SSE:', e)
          }
        }
      }

      return true
    } catch (error) {
      console.error('Streaming error:', error)
      return false
    }
  }, [loadSessions, setMensagens, setSessionId])

  const handleSend = useCallback(async (options?: SendOptions) => {
    const anexosAtuais = options?.anexosOverride ?? anexos
    const textoEntrada = (options?.textoOverride ?? input).trim()
    if ((!textoEntrada && anexosAtuais.length === 0) || loading) return
    const referenciasVisuais: string[] = []
    const transcricoesAudio: string[] = []
    const anexosUsuarioPreview: Mensagem['anexos'] = []

    setLoading(true)
    if (!options?.textoOverride) setInput('')
    if (!options?.anexosOverride) setAnexos([])

    try {
      for (const anexo of anexosAtuais) {
        if (anexo.tipo === 'imagem') {
          const formData = new FormData()
          formData.append('file', anexo.file)
          formData.append('prompt', textoEntrada || 'Descreva esta imagem em detalhes')
          const response = await api.post('/viva/vision/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          const analise = String(response.data?.analise || '').trim()
          if (analise) {
            referenciasVisuais.push(`Referencia "${anexo.file.name}": ${analise.slice(0, 1200)}`)
          }
          anexosUsuarioPreview.push({
            tipo: 'imagem',
            url: anexo.preview || '',
            nome: anexo.file.name
          })
        } else if (anexo.tipo === 'audio') {
          const transcricao = await transcribeAudioBlob(anexo.file)
          if (transcricao) {
            transcricoesAudio.push(transcricao)
          }
        } else {
          anexosUsuarioPreview.push({
            tipo: 'arquivo',
            url: anexo.preview || '',
            nome: anexo.file.name
          })
        }
      }

      const textoAudio = transcricoesAudio.join('\n').trim()
      const mensagemBase = textoEntrada || textoAudio
      const brandMode = inferBrandMode(mensagemBase)
      const mensagemComReferencia =
        referenciasVisuais.length > 0
          ? `${mensagemBase}\n\nReferencia visual enviada pelo usuario (usar como base):\n${referenciasVisuais.join('\n\n')}`
          : mensagemBase

      if (!mensagemBase) {
        const iaMsg: Mensagem = {
          id: (Date.now() + 1).toString(),
          tipo: 'ia',
          conteudo: 'Nao consegui transcrever o audio com qualidade. Tente gravar novamente em ambiente mais silencioso.',
          timestamp: new Date()
        }
        setMensagens(prev => [...prev, iaMsg])
        return
      }

      const deveGerarOverlay = Boolean(
        mensagemBase &&
        (brandMode === 'REZETA' || brandMode === 'FC') &&
        isImageRequest(mensagemBase)
      )
      const overlayText = deveGerarOverlay ? extractOverlaySource(mensagemBase) : null

      const userMsg: Mensagem = {
        id: Date.now().toString(),
        tipo: 'usuario',
        conteudo: mensagemBase,
        timestamp: new Date(),
        anexos: anexosUsuarioPreview.length > 0 ? anexosUsuarioPreview : undefined
      }
      setMensagens(prev => [...prev, userMsg])

      const contexto = mensagens.slice(-10)

      // Tentar streaming primeiro (apenas para chat textual simples)
      const usarStreaming = !deveGerarOverlay && !referenciasVisuais.length
      let streamingSuccess = false

      if (usarStreaming) {
        streamingSuccess = await handleSendStream(
          mensagemComReferencia,
          contexto,
          sessionId
        )
      }

      // Fallback para modo não-streaming se streaming falhar ou não for usado
      if (!streamingSuccess) {
        const response = await api.post('/viva/chat', {
          mensagem: mensagemComReferencia,
          contexto,
          session_id: sessionId || undefined
        })
        if (response.data?.session_id) {
          setSessionId(response.data.session_id)
          void loadSessions(response.data.session_id)
        }

        const resposta = String(response.data?.resposta || '').trim() || 'Processado com sucesso!'
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

        const overlayMeta = midia[0]?.meta?.overlay
        const overlayFromBackend = overlayMeta && (overlayMeta.brand === 'FC' || overlayMeta.brand === 'REZETA')
          ? {
              brand: overlayMeta.brand as 'FC' | 'REZETA',
              formato: overlayMeta.formato,
              copy: {
                headline: overlayMeta.headline,
                subheadline: overlayMeta.subheadline,
                bullets: Array.isArray(overlayMeta.bullets) ? overlayMeta.bullets : [],
                quote: overlayMeta.quote,
                cta: overlayMeta.cta
              }
            }
          : undefined

        const overlayFallback = overlayText && (brandMode === 'REZETA' || brandMode === 'FC')
          ? { brand: brandMode as 'REZETA' | 'FC', text: overlayText }
          : undefined

        const iaMsg: Mensagem = {
          id: (Date.now() + 1).toString(),
          tipo: 'ia',
          conteudo: resposta,
          timestamp: new Date(),
          anexos: anexosIA.length > 0 ? anexosIA : undefined,
          overlay: overlayFromBackend || overlayFallback
        }
        setMensagens(prev => [...prev, iaMsg])
        return
      }

        const iaMsg: Mensagem = {
          id: (Date.now() + 1).toString(),
          tipo: 'ia',
          conteudo: resposta,
          timestamp: new Date(),
          overlay: overlayText && (brandMode === 'REZETA' || brandMode === 'FC')
            ? { brand: brandMode as 'REZETA' | 'FC', text: overlayText }
            : undefined
        }
        setMensagens(prev => [...prev, iaMsg])
      }
    } catch {
      const errorMsg: Mensagem = {
        id: (Date.now() + 1).toString(),
        tipo: 'ia',
        conteudo: 'Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?',
        timestamp: new Date()
      }
      setMensagens(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }, [anexos, input, loadSessions, loading, mensagens, sessionId, transcribeAudioBlob, handleSendStream])

  useEffect(() => {
    sendFromVoiceRef.current = (texto: string) => {
      const mensagem = String(texto || '').trim()
      if (!mensagem) return
      void handleSend({ textoOverride: mensagem, anexosOverride: [] })
    }
  }, [handleSend])

  useEffect(() => {
    if (loading || !pendingAudioAutoSend) return
    const queuedAudio = pendingAudioAutoSend
    setPendingAudioAutoSend(null)
    void handleSend({
      anexosOverride: [queuedAudio],
      textoOverride: ''
    })
  }, [loading, pendingAudioAutoSend, handleSend])

  const stopAudioRecording = () => {
    const recorder = mediaRecorderRef.current
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop()
    }
    setGravandoAudio(false)
  }

  const startAudioRecording = async () => {
    if (typeof window === 'undefined') return

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      audioInputRef.current?.click()
      return
    }

    try {
      setErroAudio(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream
      audioChunksRef.current = []

      const preferredMime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : ''

      const recorder = preferredMime ? new MediaRecorder(stream, { mimeType: preferredMime }) : new MediaRecorder(stream)
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      recorder.onerror = () => {
        setErroAudio('Falha ao gravar audio. Tente novamente.')
        setGravandoAudio(false)
      }

      recorder.onstop = () => {
        setGravandoAudio(false)
        stream.getTracks().forEach(track => track.stop())
        mediaStreamRef.current = null

        const mimeType = recorder.mimeType || 'audio/webm'
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType })
        audioChunksRef.current = []
        if (!audioBlob.size) return

        const ext = mimeType.includes('mp4') ? 'm4a' : 'webm'
        const stamp = new Date().toISOString().replace(/[:.]/g, '-')
        const audioFile = new File([audioBlob], `gravacao-${stamp}.${ext}`, { type: mimeType })

        // Fluxo institucional: grava, transcreve e envia direto para a VIVA.
        if (loading) {
          setPendingAudioAutoSend({ file: audioFile, tipo: 'audio' })
          return
        }
        void handleSend({
          anexosOverride: [{ file: audioFile, tipo: 'audio' }],
          textoOverride: ''
        })
      }

      recorder.start()
      setGravandoAudio(true)
    } catch {
      setErroAudio('Nao consegui acessar o microfone. Se preferir, selecione um audio manualmente.')
      audioInputRef.current?.click()
    }
  }

  const handleAudioButtonClick = async () => {
    if (gravandoAudio) {
      stopAudioRecording()
      return
    }
    await startAudioRecording()
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, tipo: 'imagem' | 'audio' | 'arquivo') => {
    const files = e.target.files
    if (!files) return
    if (tipo === 'audio') {
      setErroAudio(null)
      const selectedAudio = Array.from(files)[0]
      if (selectedAudio) {
        const queuedAudio: ComposerAnexo = { file: selectedAudio, tipo: 'audio' }
        if (loading) {
          setPendingAudioAutoSend(queuedAudio)
        } else {
          void handleSend({
            anexosOverride: [queuedAudio],
            textoOverride: ''
          })
        }
      }
      e.target.value = ''
      return
    }

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
    e.target.value = ''
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

  const clearChat = async () => {
    try {
      const response = await api.post<ChatSnapshot>('/viva/chat/session/new', {})
      if (response.data?.session_id) {
        setSessionId(response.data.session_id)
        await loadSessions(response.data.session_id)
      } else {
        setSessionId(null)
        await loadSessions(null)
      }
    } catch {
      setSessionId(null)
      await loadSessions(null)
    }

    setMensagens([createWelcomeMessage()])
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
    maxLines?: number,
    maxY?: number
  ) => {
    const words = String(text || '').trim().split(/\s+/).filter(Boolean)
    if (words.length === 0) return y

    const lines: string[] = []
    let line = ''
    let truncated = false

    for (let i = 0; i < words.length; i += 1) {
      const word = words[i]
      const testLine = `${line}${word} `
      const metrics = ctx.measureText(testLine)

      if (metrics.width > maxWidth && line) {
        lines.push(line.trim())
        line = `${word} `
        if (maxLines && lines.length >= maxLines) {
          truncated = true
          break
        }
      } else {
        line = testLine
      }
    }

    if (!truncated && line.trim()) {
      lines.push(line.trim())
    }

    let currentY = y
    const allowedLines: string[] = []
    for (const candidate of lines) {
      if (maxY && currentY > maxY) {
        truncated = true
        break
      }
      allowedLines.push(candidate)
      currentY += lineHeight
    }

    if (allowedLines.length > 0) {
      const lastIndex = allowedLines.length - 1
      if (truncated) {
        let ellipsisLine = allowedLines[lastIndex]
        while (ctx.measureText(`${ellipsisLine}...`).width > maxWidth && ellipsisLine.length > 3) {
          ellipsisLine = ellipsisLine.slice(0, -1).trimEnd()
        }
        allowedLines[lastIndex] = `${ellipsisLine}...`
      }

      let drawY = y
      for (const ln of allowedLines) {
        if (maxY && drawY > maxY) break
        ctx.fillText(ln, x, drawY)
        drawY += lineHeight
      }
      return drawY
    }

    return y
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

      // Menos "overlay" para nao cobrir tanto a foto (melhor em 100% zoom).
      const topHeight = Math.round(height * 0.30)
      const bottomHeight = Math.round(height * 0.38)
      const margin = Math.round(width * 0.06)
      const topMaxY = topHeight - Math.round(width * 0.03)
      const bottomStartY = height - bottomHeight + Math.round(bottomHeight * 0.18)
      const bottomMaxY = height - Math.round(bottomHeight * 0.12)

      ctx.fillStyle = hexToRgba(theme.light, 0.86)
      ctx.fillRect(0, 0, width, topHeight)

      const gradient = ctx.createLinearGradient(0, height - bottomHeight, width, height)
      gradient.addColorStop(0, hexToRgba(theme.dark, 0.9))
      gradient.addColorStop(1, hexToRgba(theme.accent, 0.9))
      ctx.fillStyle = gradient
      ctx.fillRect(0, height - bottomHeight, width, bottomHeight)

      ctx.fillStyle = theme.primary
      ctx.font = `bold ${Math.round(width * 0.042)}px Inter, Arial, sans-serif`
      wrapText(
        ctx,
        parsed.headline,
        margin,
        Math.round(topHeight * 0.3),
        width - margin * 2,
        Math.round(width * 0.05),
        3,
        topMaxY
      )

      if (parsed.subheadline) {
        ctx.font = `${Math.round(width * 0.028)}px Inter, Arial, sans-serif`
        wrapText(
          ctx,
          parsed.subheadline,
          margin,
          Math.round(topHeight * 0.66),
          width - margin * 2,
          Math.round(width * 0.038),
          3,
          topMaxY
        )
      }

      ctx.fillStyle = '#ffffff'
      ctx.font = `${Math.round(width * 0.028)}px Inter, Arial, sans-serif`
      let currentY = bottomStartY
      parsed.bullets.forEach((bullet) => {
        if (currentY > bottomMaxY) return
        currentY = wrapText(
          ctx,
          bullet,
          margin,
          currentY,
          width - margin * 2,
          Math.round(width * 0.036),
          3,
          bottomMaxY
        )
      })

      if (parsed.quote && currentY <= bottomMaxY) {
        ctx.font = `italic ${Math.round(width * 0.024)}px Inter, Arial, sans-serif`
        currentY = wrapText(
          ctx,
          parsed.quote,
          margin,
          currentY + Math.round(width * 0.01),
          width - margin * 2,
          Math.round(width * 0.032),
          2,
          bottomMaxY
        )
      }

      if (parsed.cta && currentY <= bottomMaxY) {
        ctx.font = `bold ${Math.round(width * 0.026)}px Inter, Arial, sans-serif`
        wrapText(
          ctx,
          parsed.cta,
          margin,
          currentY + Math.round(width * 0.016),
          width - margin * 2,
          Math.round(width * 0.034),
          2,
          bottomMaxY
        )
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

  const assistenteFalando = loading || gravandoAudio

  const resolveArteAspectClass = (formato: string) => {
    const normalized = String(formato || '').replace(/\s+/g, '').toLowerCase()
    if (normalized === '4:5') return 'aspect-[4/5]'
    if (normalized === '1:1') return 'aspect-square'
    if (normalized === '16:9') return 'aspect-video'
    if (normalized === '9:16') return 'aspect-[9/16]'
    return 'aspect-[4/5]'
  }

  const toggleModoConversacao = () => {
    const novoEstado = !modoConversacaoAtivo
    setModoConversacaoAtivo(novoEstado)
    setErroAudio(null)
    setTranscricaoParcial('')

    if (!novoEstado) {
      textAreaRef.current?.focus()
      scrollToBottom(true)
    }

    if (!novoEstado) {
      stopAssistantPlayback()
      stopContinuousConversation()
    } else {
      conversationShouldListenRef.current = true
      startContinuousConversation()
    }

    const ultimaMensagemIA = [...mensagens].reverse().find(msg => msg.tipo === 'ia')
    lastSpokenMessageIdRef.current = ultimaMensagemIA?.id || null
  }

  const handleHoloPointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    const stage = holoStageRef.current
    if (!stage) return
    const rect = stage.getBoundingClientRect()
    const x = (event.clientX - rect.left) / rect.width
    const y = (event.clientY - rect.top) / rect.height
    const rotateY = ((x - 0.5) * 16).toFixed(2)
    const rotateX = ((0.5 - y) * 12).toFixed(2)
    stage.style.setProperty('--holo-tilt-y', `${rotateY}deg`)
    stage.style.setProperty('--holo-tilt-x', `${rotateX}deg`)
  }

  const resetHoloTilt = () => {
    const stage = holoStageRef.current
    if (!stage) return
    stage.style.setProperty('--holo-tilt-y', '0deg')
    stage.style.setProperty('--holo-tilt-x', '0deg')
  }

  return (
    <>
      <div className="flex h-[calc(100vh-4rem)]">
      {/* Menu Lateral */}
      <div className={`bg-gray-50 border-r transition-all duration-300 ${menuAberto ? 'w-64' : 'w-0 overflow-hidden'}`}>
        <div className="p-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Conversa
          </h3>
          <div className="space-y-2">
            <button
              onClick={toggleModoConversacao}
              className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                modoConversacaoAtivo
                  ? 'bg-white shadow-md ring-2 ring-cyan-500'
                  : 'bg-white hover:shadow-md border border-gray-200'
              }`}
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white ${
                modoConversacaoAtivo ? 'bg-cyan-600' : 'bg-cyan-500'
              }`}>
                {modoConversacaoAtivo ? <Volume2 className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>
              <div className="text-left">
                <p className="font-medium text-sm">Conversa VIVA</p>
                <p className="text-xs text-gray-500">Modo fluido com voz da VIVA</p>
              </div>
              {modoConversacaoAtivo && (
                <ChevronRight className="w-4 h-4 text-cyan-600 ml-auto" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Ãrea Principal do Chat */}
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
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={sessionId || ''}
              onChange={(e) => {
                const target = e.target.value
                if (!target) return
                void loadSessionSnapshot(target)
              }}
              className="h-9 min-w-[230px] rounded-md border bg-white px-3 text-sm text-gray-700"
              disabled={loadingSessions || chatSessions.length === 0}
              title="Recuperar sessao anterior"
            >
              {chatSessions.length === 0 ? (
                <option value="">{loadingSessions ? 'Carregando sessoes...' : 'Sem historico'}</option>
              ) : (
                chatSessions.map((session) => (
                  <option key={session.id} value={session.id}>
                    {formatSessionLabel(session)}
                  </option>
                ))
              )}
            </select>
            <Button variant="ghost" size="sm" onClick={() => { void loadSessions(sessionId) }} className="text-gray-500">
              Atualizar
            </Button>
            <Button variant="ghost" size="sm" onClick={clearChat} className="text-gray-500">
              <Trash2 className="w-4 h-4 mr-2" />
              Limpar
            </Button>
          </div>
        </div>

        {modoConversacaoAtivo ? (
          <div className="flex-1 flex items-center justify-center p-6 bg-[radial-gradient(circle_at_top,rgba(125,211,252,0.2),rgba(248,250,252,0.96)_52%)]">
            <div className="flex flex-col items-center">
              <div
                ref={holoStageRef}
                className={`holo-stage ${assistenteFalando ? 'is-active' : ''}`}
                role="img"
                aria-label="Avatar oficial da VIVA"
                onPointerMove={handleHoloPointerMove}
                onPointerLeave={resetHoloTilt}
              >
                <div className="holo-grid" />
                <span className="holo-ring holo-ring-1" />
                <span className="holo-ring holo-ring-2" />
                <span className="holo-ring holo-ring-3" />
                <div className="holo-neural">
                  <span className="holo-node holo-node-1" />
                  <span className="holo-node holo-node-2" />
                  <span className="holo-node holo-node-3" />
                  <span className="holo-node holo-node-4" />
                </div>
                <div className="holo-avatar">
                  {!avatarFallback ? (
                    <Image
                      src={VIVA_AVATAR_SOURCES[avatarSourceIndex]}
                      alt="VIVA"
                      fill
                      className="rounded-[20px] object-contain object-center"
                      onError={() => {
                        if (avatarSourceIndex < VIVA_AVATAR_SOURCES.length - 1) {
                          setAvatarSourceIndex((prev) => prev + 1)
                          return
                        }
                        setAvatarFallback(true)
                      }}
                      unoptimized
                    />
                  ) : (
                    <Bot className="holo-brain-icon" />
                  )}
                </div>
                <span className="holo-shadow" />
              </div>

              <div className="mt-3 text-center">
                <p className="text-xs uppercase tracking-[0.24em] text-cyan-700">
                  {loading ? 'Processando' : escutaContinuaAtiva ? 'Escutando' : 'Aguardando'}
                </p>
                {transcricaoParcial && (
                  <p className="mt-2 max-w-xl text-sm text-slate-600">{transcricaoParcial}</p>
                )}
                {erroAudio && (
                  <p className="mt-2 max-w-xl text-sm text-amber-700">{erroAudio}</p>
                )}
                {!ttsProviderConfigured && ttsMissingEnv.length > 0 && (
                  <p className="mt-2 max-w-xl text-sm text-slate-600">
                    MiniMax TTS nao configurado: defina {ttsMissingEnv.join(', ')} em `backend/.env` e reinicie o container do backend.
                  </p>
                )}
                <div className="mt-3 flex items-center justify-center gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant={vozVivaAtiva ? 'default' : 'outline'}
                    onClick={() => {
                      const novoEstado = !vozVivaAtiva
                      setVozVivaAtiva(novoEstado)
                      if (!novoEstado) stopAssistantPlayback()
                    }}
                  >
                    {vozVivaAtiva ? <Volume2 className="mr-2 h-4 w-4" /> : <VolumeX className="mr-2 h-4 w-4" />}
                    {vozVivaAtiva ? 'Voz ativa' : 'Voz pausada'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ) : (
        <>
        {/* Ãrea de mensagens */}
        <ScrollArea className="flex-1 px-4" ref={scrollAreaRef}>
          <div className="max-w-4xl mx-auto py-6 space-y-6">

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
                                <Image 
                                  src={anexo.url} 
                                  alt={anexo.nome || 'Imagem'} 
                                  width={420}
                                  height={400}
                                  className="max-w-[320px] sm:max-w-[420px] max-h-[60vh] object-contain rounded-lg cursor-zoom-in bg-white"
                                  onLoad={() => scrollToBottom()}
                                  onClick={() => setImagemAtiva({ url: anexo.url, nome: anexo.nome })}
                                  unoptimized
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
                                {anexo.meta?.campanha_id && (
                                  <button
                                    onClick={() => {
                                      window.location.href = `/campanhas?id=${anexo.meta.campanha_id}`
                                    }}
                                    className="ml-3 text-xs text-emerald-600 hover:text-emerald-800"
                                  >
                                    Ver em campanhas
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
                  
                  {/* AÃ§Ãµes */}
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
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Anexos selecionados */}
        {anexos.length > 0 && (
          <div className="px-4 py-2 border-t bg-gray-50">
            <div className="flex gap-2 overflow-x-auto">
              {anexos.map((anexo, idx) => (
                <div key={idx} className="relative flex-shrink-0">
                  {anexo.tipo === 'imagem' && anexo.preview ? (
                    <Image 
                      src={anexo.preview} 
                      alt="Preview" 
                      width={64}
                      height={64}
                      className="w-16 h-16 object-cover rounded-lg"
                      unoptimized
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
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2 items-end">
              {/* BotÃµes de anexo */}
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
                  className={gravandoAudio ? 'text-red-600 bg-red-50 hover:bg-red-100' : 'text-gray-500'}
                  onClick={handleAudioButtonClick}
                  title={gravandoAudio ? 'Parar gravacao' : 'Gravar audio'}
                >
                  <Mic className="w-5 h-5" />
                </Button>
              </div>
              
              <textarea
                ref={textAreaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Digite sua mensagem para a VIVA..."
                className="flex-1 px-4 py-3 border rounded-xl resize-none text-base leading-6 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                style={{ minHeight: `${INPUT_MIN_HEIGHT}px`, maxHeight: `${INPUT_MAX_HEIGHT}px` }}
              />
              <Button
                onClick={() => { void handleSend() }}
                disabled={(!input.trim() && anexos.length === 0) || loading}
                className="px-4 h-12"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>

            {gravandoAudio && (
              <p className="mt-2 text-xs text-red-600 text-center">
                Gravando audio... clique no microfone para finalizar.
              </p>
            )}
            {erroAudio && (
              <p className="mt-2 text-xs text-amber-600 text-center">
                {erroAudio}
              </p>
            )}
            {pendingAudioAutoSend && (
              <p className="mt-2 text-xs text-blue-600 text-center">
                Audio na fila: envio automatico assim que a VIVA concluir a resposta atual.
              </p>
            )}
            
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
              VIVA pode cometer erros. Verifique informaÃ§Ãµes importantes.
            </p>
          </div>
        </div>
        </>
        )}
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
          <Image
            src={imagemAtiva.url}
            alt={imagemAtiva.nome || 'Imagem ampliada'}
            width={1200}
            height={1200}
            className="w-full h-auto rounded-lg"
            unoptimized
          />
        </div>
      </div>
      )}

      {arteAtiva && (
        <div
          className="fixed inset-0 z-50 overflow-y-auto bg-black/70 p-4 sm:p-6"
          onClick={() => setArteAtiva(null)}
        >
          <div className="min-h-full flex items-start justify-center">
            <div
              className="relative my-4 w-full max-w-4xl rounded-lg bg-white p-4 sm:p-6 shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-4 flex items-center justify-between gap-2">
                <h2 className="text-lg font-semibold">Arte final</h2>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={() => { setImagemAtiva({ url: arteAtiva.url, nome: arteAtiva.nome }); setArteAtiva(null) }}>
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
                  <div
                    className={`relative mx-auto w-full max-w-[680px] ${resolveArteAspectClass(arteAtiva.overlay.formato || '')} overflow-hidden rounded-lg border bg-gray-100`}
                  >
                    <Image
                      src={arteAtiva.url}
                      alt={arteAtiva.nome || 'Arte gerada'}
                      fill
                      className="object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                      unoptimized
                    />
                    <div className="absolute inset-x-0 top-0 h-[30%] overflow-y-auto bg-white/90 px-5 py-4">
                      <p className="text-xs uppercase tracking-widest" style={{ color: theme.accent }}>
                        {theme.label}
                      </p>
                      <h3 className="mt-2 break-words text-base sm:text-xl font-bold leading-tight" style={{ color: theme.primary }}>
                        {parsed.headline}
                      </h3>
                      {parsed.subheadline && (
                        <p className="mt-1 break-words text-xs sm:text-sm leading-snug" style={{ color: theme.primary }}>
                          {parsed.subheadline}
                        </p>
                      )}
                    </div>
                    <div
                      className="absolute inset-x-0 bottom-0 h-[38%] overflow-y-auto px-5 py-4 text-white"
                      style={{
                        background: `linear-gradient(90deg, ${theme.dark}e6, ${theme.accent}e6)`
                      }}
                    >
                      <ul className="space-y-1 text-[11px] sm:text-sm leading-snug break-words">
                        {parsed.bullets.map((bullet, idx) => (
                          <li key={idx}>{bullet}</li>
                        ))}
                      </ul>
                      {parsed.quote && (
                        <p className="mt-3 break-words text-[11px] sm:text-sm italic leading-snug">{parsed.quote}</p>
                      )}
                      {parsed.cta && (
                        <p className="mt-3 inline-block max-w-full break-words rounded-full bg-white/20 px-3 py-1 text-[11px] sm:text-sm font-semibold tracking-wide">
                          {parsed.cta}
                        </p>
                      )}
                    </div>
                  </div>
                )
              })()}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

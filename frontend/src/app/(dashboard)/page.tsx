'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Send, Bot, FileText, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function ChatHomePage() {
  const router = useRouter()
  const [inputValue, setInputValue] = useState('')

  const handleSend = () => {
    if (inputValue.trim()) {
      router.push(`/chat?message=${encodeURIComponent(inputValue)}`)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickActions = [
    { icon: FileText, label: 'Criar contrato', action: () => router.push('/contratos') },
    { icon: MessageSquare, label: 'Ver conversas', action: () => router.push('/whatsapp/conversas') },
    { icon: Bot, label: 'Perguntar à VIVA', action: () => router.push('/whatsapp/conversas') },
  ]

  return (
    <div className="flex flex-col h-full min-h-[calc(100vh-2rem)]">
      {/* Header com botão Novo Chat */}
      <div className="flex items-center justify-between mb-8">
        <Button
          variant="outline"
          className="flex items-center gap-2 rounded-full px-4 py-2 border-gray-200 hover:bg-gray-50"
          onClick={() => router.push('/whatsapp/conversas')}
        >
          <Plus className="w-4 h-4" />
          <span className="text-sm">Novo Chat</span>
          <kbd className="ml-2 text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-500">Ctrl K</kbd>
        </Button>
      </div>

      {/* Conteúdo Central */}
      <div className="flex-1 flex flex-col items-center justify-center -mt-20">
        {/* Logo/Título */}
        <div className="mb-12">
          <h1 className="text-6xl font-bold tracking-tight text-gray-900">
            VIVA
          </h1>
          <p className="text-center text-gray-500 mt-2 text-lg">
            Assistente Inteligente FC Soluções
          </p>
        </div>

        {/* Input Central */}
        <div className="w-full max-w-3xl px-4">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-100/50 to-purple-100/50 rounded-3xl blur-xl group-hover:blur-2xl transition-all opacity-50" />
            
            <div className="relative flex items-center bg-white border border-gray-200 rounded-3xl shadow-lg hover:shadow-xl transition-shadow p-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Digite sua mensagem para a VIVA..."
                className="flex-1 px-6 py-4 text-lg bg-transparent border-none outline-none placeholder:text-gray-400"
              />
              
              <Button
                size="icon"
                className="w-12 h-12 rounded-full bg-gray-900 hover:bg-gray-800 text-white mr-2"
                onClick={handleSend}
                disabled={!inputValue.trim()}
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {/* Botões de Ação Rápida */}
          <div className="flex items-center justify-center gap-2 mt-4">
            <span className="text-sm text-gray-500 mr-2">Ações rápidas:</span>
            {quickActions.map((action, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="rounded-full text-gray-600 border-gray-200 hover:bg-gray-50"
                onClick={action.action}
              >
                <action.icon className="w-4 h-4 mr-2" />
                {action.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-sm text-gray-400 mt-auto pb-4">
        FC Soluções Financeiras • Assistente Virtual VIVA
      </div>
    </div>
  )
}

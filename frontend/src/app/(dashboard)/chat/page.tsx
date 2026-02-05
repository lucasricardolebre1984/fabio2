'use client'

import { Suspense } from 'react'
import { useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { useRouter } from 'next/navigation'

function ChatRedirect() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const message = searchParams.get('message')

  useEffect(() => {
    // Redirecionar para conversas com a mensagem na query string
    if (message) {
      router.push(`/whatsapp/conversas?newMessage=${encodeURIComponent(message)}`)
    } else {
      router.push('/whatsapp/conversas')
    }
  }, [message, router])

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
        <p className="mt-4 text-gray-600">Iniciando conversa...</p>
      </div>
    </div>
  )
}

export default function ChatRedirectPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    }>
      <ChatRedirect />
    </Suspense>
  )
}

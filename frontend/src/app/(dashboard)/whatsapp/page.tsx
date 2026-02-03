'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageCircle } from 'lucide-react'

export default function WhatsAppPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">WhatsApp</h1>

      <Card>
        <CardHeader>
          <CardTitle>Status da Conexão</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-600 mb-4">WhatsApp desconectado</p>
              <Button>Conectar WhatsApp</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

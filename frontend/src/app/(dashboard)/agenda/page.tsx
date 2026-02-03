'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function AgendaPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Agenda</h1>

      <Card>
        <CardHeader>
          <CardTitle>Compromissos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Nenhum compromisso agendado.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

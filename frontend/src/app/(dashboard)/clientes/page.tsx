'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function ClientesPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Clientes</h1>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Clientes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Nenhum cliente encontrado. Os clientes são cadastrados automaticamente ao criar um contrato.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

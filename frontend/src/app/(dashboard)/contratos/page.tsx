'use client'

import Link from 'next/link'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function ContratosPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Contratos</h1>
        <Link href="/contratos/novo">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Novo Contrato
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Contratos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Nenhum contrato encontrado. Clique em "Novo Contrato" para criar.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

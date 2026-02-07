'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Loader2, RefreshCw, UserPlus } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { clientesApi } from '@/lib/api'

interface Cliente {
  id: string
  nome: string
  tipo_pessoa: 'fisica' | 'juridica'
  documento: string
  email: string
  telefone?: string | null
  cidade?: string | null
  estado?: string | null
  total_contratos: number
  created_at: string
}

const emptyForm = {
  nome: '',
  tipo_pessoa: 'fisica',
  documento: '',
  email: '',
  telefone: '',
  endereco: '',
  cidade: '',
  estado: '',
  cep: '',
  observacoes: '',
}

export default function ClientesPage() {
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return clientes
    return clientes.filter((cliente) => {
      return (
        cliente.nome.toLowerCase().includes(term) ||
        cliente.documento.toLowerCase().includes(term) ||
        (cliente.email || '').toLowerCase().includes(term)
      )
    })
  }, [clientes, search])

  const loadClientes = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await clientesApi.getAll()
      setClientes(Array.isArray(response?.items) ? response.items : [])
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao carregar clientes.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadClientes()
  }, [])

  const onCreate = async (event: FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    setNotice('')

    try {
      await clientesApi.create({
        ...form,
        tipo_pessoa: form.tipo_pessoa,
      })
      setForm(emptyForm)
      setShowForm(false)
      setNotice('Cliente cadastrado com sucesso.')
      await loadClientes()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao cadastrar cliente.')
    } finally {
      setSaving(false)
    }
  }

  const onSync = async () => {
    setSyncing(true)
    setError('')
    setNotice('')
    try {
      const result = await clientesApi.syncFromContracts()
      setNotice(
        `Sincronizacao concluida. Criados: ${result?.clientes_criados ?? 0}, vinculados: ${result?.contratos_vinculados ?? 0}.`
      )
      await loadClientes()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao sincronizar contratos.')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-gray-900">Clientes</h1>
        <div className="flex items-center gap-2">
          <Button type="button" variant="outline" onClick={onSync} disabled={syncing}>
            {syncing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
            Sincronizar contratos
          </Button>
          <Button type="button" onClick={() => setShowForm((value) => !value)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Cadastro manual
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6 text-sm text-red-700">{error}</CardContent>
        </Card>
      )}

      {notice && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6 text-sm text-green-700">{notice}</CardContent>
        </Card>
      )}

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Novo cliente</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="grid gap-4 md:grid-cols-2" onSubmit={onCreate}>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="nome">Nome</Label>
                <Input
                  id="nome"
                  required
                  value={form.nome}
                  onChange={(event) => setForm((prev) => ({ ...prev, nome: event.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo_pessoa">Tipo</Label>
                <select
                  id="tipo_pessoa"
                  className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={form.tipo_pessoa}
                  onChange={(event) => setForm((prev) => ({ ...prev, tipo_pessoa: event.target.value as 'fisica' | 'juridica' }))}
                >
                  <option value="fisica">Pessoa fisica</option>
                  <option value="juridica">Pessoa juridica</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="documento">CPF/CNPJ</Label>
                <Input
                  id="documento"
                  required
                  value={form.documento}
                  onChange={(event) => setForm((prev) => ({ ...prev, documento: event.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={form.email}
                  onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="telefone">Telefone</Label>
                <Input
                  id="telefone"
                  value={form.telefone}
                  onChange={(event) => setForm((prev) => ({ ...prev, telefone: event.target.value }))}
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="endereco">Endereco</Label>
                <Input
                  id="endereco"
                  value={form.endereco}
                  onChange={(event) => setForm((prev) => ({ ...prev, endereco: event.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cidade">Cidade</Label>
                <Input
                  id="cidade"
                  value={form.cidade}
                  onChange={(event) => setForm((prev) => ({ ...prev, cidade: event.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="estado">UF</Label>
                <Input
                  id="estado"
                  maxLength={2}
                  value={form.estado}
                  onChange={(event) => setForm((prev) => ({ ...prev, estado: event.target.value.toUpperCase() }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cep">CEP</Label>
                <Input
                  id="cep"
                  value={form.cep}
                  onChange={(event) => setForm((prev) => ({ ...prev, cep: event.target.value }))}
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="observacoes">Observacoes</Label>
                <textarea
                  id="observacoes"
                  className="min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={form.observacoes}
                  onChange={(event) => setForm((prev) => ({ ...prev, observacoes: event.target.value }))}
                />
              </div>

              <div className="md:col-span-2 flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={saving}>
                  {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Salvar cliente
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="space-y-3">
          <CardTitle>Lista de clientes</CardTitle>
          <Input
            placeholder="Buscar por nome, documento ou email"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Carregando clientes...
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-8 text-center text-gray-500">
              Nenhum cliente encontrado.
            </div>
          ) : (
            <div className="space-y-3">
              {filtered.map((cliente) => (
                <div key={cliente.id} className="rounded-lg border p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-gray-900">{cliente.nome}</p>
                      <p className="text-sm text-gray-600">{cliente.documento}</p>
                      <p className="text-sm text-gray-600">{cliente.email}</p>
                      <p className="text-sm text-gray-600">
                        {[cliente.cidade, cliente.estado].filter(Boolean).join(' - ') || 'Cidade nao informada'}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline">
                        {cliente.tipo_pessoa === 'fisica' ? 'PF' : 'PJ'}
                      </Badge>
                      <p className="mt-2 text-xs text-gray-500">
                        Contratos: {cliente.total_contratos ?? 0}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

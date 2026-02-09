'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Loader2, Pencil, RefreshCw, Save, ShieldAlert, Trash2, UserPlus, X } from 'lucide-react'

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
  endereco?: string | null
  cidade?: string | null
  estado?: string | null
  cep?: string | null
  observacoes?: string | null
  total_contratos: number
  created_at: string
}

interface ClienteForm {
  nome: string
  tipo_pessoa: 'fisica' | 'juridica'
  documento: string
  email: string
  telefone: string
  endereco: string
  cidade: string
  estado: string
  cep: string
  observacoes: string
}

const emptyForm: ClienteForm = {
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
  const [deduping, setDeduping] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editSaving, setEditSaving] = useState(false)
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<ClienteForm>(emptyForm)
  const [editForm, setEditForm] = useState<Partial<ClienteForm>>({})

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

  const resetMessages = () => {
    setError('')
    setNotice('')
  }

  const onCreate = async (event: FormEvent) => {
    event.preventDefault()
    setSaving(true)
    resetMessages()

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
      if (err?.response?.status === 409) {
        setError('Ja existe cliente com este CPF/CNPJ.')
      } else {
        setError(err?.response?.data?.detail || 'Falha ao cadastrar cliente.')
      }
    } finally {
      setSaving(false)
    }
  }

  const onSync = async () => {
    setSyncing(true)
    resetMessages()
    try {
      const result = await clientesApi.syncFromContracts()
      setNotice(
        `Sincronizacao concluida. Criados: ${result?.clientes_criados ?? 0}, vinculados: ${result?.contratos_vinculados ?? 0}, clientes recalculados: ${result?.clientes_recalculados ?? 0}.`
      )
      await loadClientes()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao sincronizar contratos.')
    } finally {
      setSyncing(false)
    }
  }

  const onDeduplicate = async () => {
    setDeduping(true)
    resetMessages()
    try {
      const result = await clientesApi.deduplicateDocuments()
      setNotice(
        `Saneamento concluido. Grupos: ${result?.grupos_duplicados ?? 0}, removidos: ${result?.clientes_removidos ?? 0}, contratos relinkados: ${result?.contratos_relinkados ?? 0}.`
      )
      await loadClientes()
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Saneamento permitido apenas para administrador.')
      } else {
        setError(err?.response?.data?.detail || 'Falha ao deduplicar clientes.')
      }
    } finally {
      setDeduping(false)
    }
  }

  const startEdit = (cliente: Cliente) => {
    resetMessages()
    setEditingId(cliente.id)
    setEditForm({
      nome: cliente.nome,
      email: cliente.email || '',
      telefone: cliente.telefone || '',
      endereco: cliente.endereco || '',
      cidade: cliente.cidade || '',
      estado: cliente.estado || '',
      cep: cliente.cep || '',
      observacoes: cliente.observacoes || '',
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditForm({})
  }

  const submitEdit = async (event: FormEvent) => {
    event.preventDefault()
    if (!editingId) return
    setEditSaving(true)
    resetMessages()

    try {
      await clientesApi.update(editingId, editForm)
      setNotice('Cliente atualizado com sucesso.')
      cancelEdit()
      await loadClientes()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Falha ao atualizar cliente.')
    } finally {
      setEditSaving(false)
    }
  }

  const onDelete = async (cliente: Cliente) => {
    const confirmed = window.confirm(
      `Excluir cliente ${cliente.nome} (${cliente.documento})?\n\nSe houver contratos vinculados, a exclusao pode falhar.`
    )
    if (!confirmed) return

    resetMessages()
    try {
      await clientesApi.delete(cliente.id)
      setNotice('Cliente excluido com sucesso.')
      if (editingId === cliente.id) {
        cancelEdit()
      }
      await loadClientes()
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Exclusao permitida apenas para administrador.')
      } else {
        setError(err?.response?.data?.detail || 'Falha ao excluir cliente.')
      }
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
          <Button type="button" variant="outline" onClick={onDeduplicate} disabled={deduping}>
            {deduping ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ShieldAlert className="mr-2 h-4 w-4" />}
            Corrigir duplicados CPF/CNPJ
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

                  <div className="mt-3 flex items-center justify-end gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => startEdit(cliente)}
                    >
                      <Pencil className="mr-2 h-4 w-4" />
                      Editar
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => onDelete(cliente)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Excluir
                    </Button>
                  </div>

                  {editingId === cliente.id && (
                    <form onSubmit={submitEdit} className="mt-4 grid gap-3 rounded-md border bg-gray-50 p-3 md:grid-cols-2">
                      <div className="space-y-1 md:col-span-2">
                        <Label htmlFor={`edit-nome-${cliente.id}`}>Nome</Label>
                        <Input
                          id={`edit-nome-${cliente.id}`}
                          required
                          value={editForm.nome || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, nome: event.target.value }))}
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`edit-email-${cliente.id}`}>Email</Label>
                        <Input
                          id={`edit-email-${cliente.id}`}
                          type="email"
                          required
                          value={editForm.email || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, email: event.target.value }))}
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`edit-telefone-${cliente.id}`}>Telefone</Label>
                        <Input
                          id={`edit-telefone-${cliente.id}`}
                          value={editForm.telefone || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, telefone: event.target.value }))}
                        />
                      </div>

                      <div className="space-y-1 md:col-span-2">
                        <Label htmlFor={`edit-endereco-${cliente.id}`}>Endereco</Label>
                        <Input
                          id={`edit-endereco-${cliente.id}`}
                          value={editForm.endereco || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, endereco: event.target.value }))}
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`edit-cidade-${cliente.id}`}>Cidade</Label>
                        <Input
                          id={`edit-cidade-${cliente.id}`}
                          value={editForm.cidade || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, cidade: event.target.value }))}
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`edit-estado-${cliente.id}`}>UF</Label>
                        <Input
                          id={`edit-estado-${cliente.id}`}
                          maxLength={2}
                          value={editForm.estado || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, estado: event.target.value.toUpperCase() }))}
                        />
                      </div>

                      <div className="space-y-1">
                        <Label htmlFor={`edit-cep-${cliente.id}`}>CEP</Label>
                        <Input
                          id={`edit-cep-${cliente.id}`}
                          value={editForm.cep || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, cep: event.target.value }))}
                        />
                      </div>

                      <div className="space-y-1 md:col-span-2">
                        <Label htmlFor={`edit-observacoes-${cliente.id}`}>Observacoes</Label>
                        <textarea
                          id={`edit-observacoes-${cliente.id}`}
                          className="min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          value={editForm.observacoes || ''}
                          onChange={(event) => setEditForm((prev) => ({ ...prev, observacoes: event.target.value }))}
                        />
                      </div>

                      <div className="md:col-span-2 flex justify-end gap-2">
                        <Button type="button" variant="outline" onClick={cancelEdit}>
                          <X className="mr-2 h-4 w-4" />
                          Cancelar
                        </Button>
                        <Button type="submit" disabled={editSaving}>
                          {editSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                          Salvar alteracoes
                        </Button>
                      </div>
                    </form>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

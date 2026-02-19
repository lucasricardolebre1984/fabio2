'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      })

      const { access_token, refresh_token } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      router.push('/contratos')
    } catch (err: any) {
      const status = err?.response?.status
      const detail = err?.response?.data?.detail

      if (status === 401) {
        setError('Email ou senha incorretos')
      } else if (status === 403) {
        setError(detail || 'Usuario inativo')
      } else if (status) {
        setError(detail || `Falha no login (HTTP ${status})`)
      } else {
        setError('Falha de conexao com o backend. Verifique a API em http://localhost:8000')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded focus:bg-black focus:px-3 focus:py-2 focus:text-white"
      >
        Pular para o conteúdo principal
      </a>
      <main id="main-content" className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="w-full max-w-md p-4">
          <Card>
            <CardHeader className="text-center">
              <div className="mb-4">
                <h1 className="text-3xl font-bold text-primary-800">FC Soluções</h1>
                <p className="text-primary-700">Financeiras</p>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Acesse sua conta</h2>
              <p className="text-sm text-gray-600">
                Entre com suas credenciais para continuar
              </p>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Senha</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                {error && (
                  <div role="alert" aria-live="assertive" className="rounded bg-red-50 p-3 text-sm text-red-700">
                    {error}
                  </div>
                )}
                <Button
                  type="submit"
                  className="w-full bg-primary-800 text-white hover:bg-primary-900"
                  disabled={loading}
                >
                  {loading ? 'Entrando...' : 'Entrar'}
                </Button>
              </form>
            </CardContent>
          </Card>
          <p className="mt-4 text-center text-sm text-gray-700">
            © 2026 FC Soluções Financeiras. Todos os direitos reservados.
          </p>
        </div>
      </main>
    </>
  )
}

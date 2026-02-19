'use client'

import { useEffect } from 'react'

type ErrorProps = {
  error: Error & { digest?: string }
  reset: () => void
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error('App route error:', error)
  }, [error])

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <section className="w-full max-w-md rounded-lg border bg-white p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-slate-900">Erro inesperado</h1>
        <p className="mt-2 text-sm text-slate-600">
          Ocorreu uma falha ao carregar esta tela.
        </p>
        <button
          type="button"
          onClick={() => reset()}
          className="mt-4 inline-flex items-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Tentar novamente
        </button>
      </section>
    </main>
  )
}

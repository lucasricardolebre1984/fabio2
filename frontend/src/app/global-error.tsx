'use client'

type GlobalErrorProps = {
  error: Error & { digest?: string }
  reset: () => void
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  console.error('Global app error:', error)

  return (
    <html lang="pt-BR">
      <body>
        <main className="flex min-h-screen items-center justify-center p-6">
          <section className="w-full max-w-md rounded-lg border bg-white p-6 shadow-sm">
            <h1 className="text-lg font-semibold text-slate-900">Falha crítica</h1>
            <p className="mt-2 text-sm text-slate-600">
              O aplicativo encontrou um erro inesperado.
            </p>
            <button
              type="button"
              onClick={() => reset()}
              className="mt-4 inline-flex items-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
            >
              Recarregar
            </button>
          </section>
        </main>
      </body>
    </html>
  )
}

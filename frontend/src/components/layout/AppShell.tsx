'use client'

import { useMemo, useState, type ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'

import { APP_BRAND, DASHBOARD_NAV_ITEMS } from '@/components/layout/navigation'
import { Sidebar } from '@/components/layout/Sidebar'

type AppShellProps = {
  children: ReactNode
}

function resolvePageTitle(pathname: string): string {
  const hit = DASHBOARD_NAV_ITEMS.find((item) => pathname.startsWith(item.href))
  return hit?.label ?? 'Dashboard'
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)
  const pageTitle = useMemo(() => resolvePageTitle(pathname), [pathname])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="hidden md:fixed md:inset-y-0 md:block">
        <Sidebar />
      </div>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-slate-900/55 md:hidden" onClick={() => setMobileOpen(false)}>
          <div className="h-full w-64" onClick={(event) => event.stopPropagation()}>
            <Sidebar onNavigate={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      <div className="md:pl-64">
        <header className="sticky top-0 z-30 border-b bg-white/90 backdrop-blur">
          <div className="flex h-16 items-center justify-between px-4 md:px-8">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="inline-flex h-10 w-10 items-center justify-center rounded-md border text-slate-700 md:hidden"
                aria-label={mobileOpen ? 'Fechar menu' : 'Abrir menu'}
                onClick={() => setMobileOpen((open) => !open)}
              >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
              <div>
                <p className="text-sm text-slate-500">{APP_BRAND.name}</p>
                <h1 className="text-lg font-semibold text-slate-900">{pageTitle}</h1>
              </div>
            </div>
          </div>
        </header>

        <main className="p-4 md:p-8">{children}</main>
      </div>
    </div>
  )
}

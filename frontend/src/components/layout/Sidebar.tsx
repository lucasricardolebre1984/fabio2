'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FileText, Users, Calendar, MessageCircle, LogOut, ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

const menuItems = [
  { href: '/contratos', label: 'Contratos', icon: FileText },
  { href: '/clientes', label: 'Clientes', icon: Users },
  { href: '/agenda', label: 'Agenda', icon: Calendar },
  { href: '/whatsapp', label: 'WhatsApp', icon: MessageCircle },
  { href: '/imagens', label: 'Imagens', icon: ImageIcon },
]

export function Sidebar() {
  const pathname = usePathname()

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/'
  }

  return (
    <aside className="w-64 bg-primary-900 text-white min-h-screen flex flex-col">
      <div className="p-6 border-b border-primary-800">
        <h1 className="text-xl font-bold">FC Soluções</h1>
        <p className="text-primary-400 text-sm">Financeiras</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname.startsWith(item.href)

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-200 hover:bg-primary-800 hover:text-white'
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-primary-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-primary-200 hover:bg-primary-800 hover:text-white transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  )
}

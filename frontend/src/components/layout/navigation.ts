import {
  Bot,
  Calendar,
  FileText,
  Megaphone,
  MessageCircle,
  Users,
  type LucideIcon,
} from 'lucide-react'

export type NavItem = {
  href: string
  label: string
  icon: LucideIcon
}

export const APP_BRAND = {
  name: 'FC Solucoes',
  tagline: 'Financeiras',
}

export const DASHBOARD_NAV_ITEMS: NavItem[] = [
  { href: '/viva', label: 'Chat IA VIVA', icon: Bot },
  { href: '/campanhas', label: 'Campanhas', icon: Megaphone },
  { href: '/contratos', label: 'Contratos', icon: FileText },
  { href: '/clientes', label: 'Clientes', icon: Users },
  { href: '/agenda', label: 'Agenda', icon: Calendar },
  { href: '/whatsapp', label: 'WhatsApp', icon: MessageCircle },
]

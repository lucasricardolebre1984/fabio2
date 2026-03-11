export const APP_NAME = 'FC Soluções Financeiras'
export const APP_VERSION = '1.0.0'

const defaultApiUrl = process.env.NODE_ENV === 'production' ? '/api/v1' : 'http://127.0.0.1:8000/api/v1'
export const API_URL = process.env.NEXT_PUBLIC_API_URL || defaultApiUrl

export const MENU_ITEMS = [
  {
    label: 'Contratos',
    href: '/contratos',
    icon: 'FileText',
  },
  {
    label: 'Clientes',
    href: '/clientes',
    icon: 'Users',
  },
  {
    label: 'Agenda',
    href: '/agenda',
    icon: 'Calendar',
  },
  {
    label: 'WhatsApp',
    href: '/whatsapp',
    icon: 'MessageCircle',
  },
]

export const CONTRATO_STATUS = {
  rascunho: { label: 'Rascunho', color: 'bg-yellow-100 text-yellow-800' },
  finalizado: { label: 'Finalizado', color: 'bg-green-100 text-green-800' },
  enviado: { label: 'Enviado', color: 'bg-blue-100 text-blue-800' },
  cancelado: { label: 'Cancelado', color: 'bg-red-100 text-red-800' },
}

// Server Component - export static params for static generation
export function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: '3' },
    { id: 'sample' },
  ]
}

// Disable static generation for dynamic routes not in the list
export const dynamicParams = true

import ContratoViewClient from './ContratoViewClient'

export default function VisualizarContratoPage() {
  return <ContratoViewClient />
}

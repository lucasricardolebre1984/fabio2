export function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }, { id: '3' }, { id: 'sample' }]
}

export const dynamicParams = true

import EditarContratoClient from './EditarContratoClient'

export default function EditarContratoPage() {
  return <EditarContratoClient />
}

import axios from 'axios'
import { API_URL } from './constants'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Contratos API
export const contratosApi = {
  getTemplate: async (templateId: string) => {
    const response = await api.get(`/contratos/templates/${templateId}`)
    return response.data
  },

  getAll: async () => {
    const response = await api.get('/contratos')
    return response.data
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/contratos/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/contratos', data)
    return response.data
  },
  
  update: async (id: string, data: any) => {
    const response = await api.put(`/contratos/${id}`, data)
    return response.data
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/contratos/${id}`)
    return response.data
  },
  
  generatePDF: async (id: string) => {
    const response = await api.get(`/contratos/${id}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  }
}

// Clientes API
export const clientesApi = {
  getAll: async () => {
    const response = await api.get('/clientes')
    return response.data
  },

  getByDocumento: async (documento: string) => {
    const response = await api.get(`/clientes/documento/${documento}`)
    return response.data
  },
  
  getById: async (id: string) => {
    const response = await api.get(`/clientes/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/clientes', data)
    return response.data
  },
  
  update: async (id: string, data: any) => {
    const response = await api.put(`/clientes/${id}`, data)
    return response.data
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/clientes/${id}`)
    return response.data
  },
  
  getContratos: async (id: string) => {
    const response = await api.get(`/clientes/${id}/contratos`)
    return response.data
  },

  syncFromContracts: async () => {
    const response = await api.post('/clientes/sincronizar-contratos')
    return response.data
  },

  deduplicateDocuments: async () => {
    const response = await api.post('/clientes/deduplicar-documentos')
    return response.data
  }
}

// Agenda API
export const agendaApi = {
  getAll: async () => {
    const response = await api.get('/agenda')
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post('/agenda', data)
    return response.data
  },

  conclude: async (id: string) => {
    const response = await api.patch(`/agenda/${id}/concluir`)
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(`/agenda/${id}`)
    return response.data
  }
}

// Google Calendar API
export const googleCalendarApi = {
  getStatus: async () => {
    const response = await api.get('/google-calendar/status')
    return response.data
  },

  getConnectUrl: async () => {
    const response = await api.get('/google-calendar/connect-url')
    return response.data
  },

  disconnect: async () => {
    const response = await api.post('/google-calendar/disconnect')
    return response.data
  },

  syncAgendaEvent: async (eventoId: string) => {
    const response = await api.post(`/google-calendar/sync/agenda/${eventoId}`)
    return response.data
  },
}

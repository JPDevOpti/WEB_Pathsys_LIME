import apiClient from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { UserRole } from '../types/userProfile.types'

export interface BackendPatologo {
  patologoName: string
  InicialesPatologo?: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  firma?: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export interface BackendResidente {
  residenteName: string
  InicialesResidente?: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

export interface BackendAuxiliar {
  auxiliarName: string
  auxiliarCode: string
  AuxiliarEmail: string
  observaciones?: string
  isActive: boolean
  fecha_creacion?: string
  fecha_actualizacion?: string
}

const pickFirstFromUnknown = (resp: any) => {
  if (Array.isArray(resp)) return resp[0]
  if (!resp || typeof resp !== 'object') return undefined
  const candidates = ['patologos', 'residentes', 'auxiliares', 'results', 'items', 'data', 'resultados']
  for (const key of candidates) {
    if (Array.isArray(resp[key]) && resp[key].length > 0) return resp[key][0]
  }
  return undefined
}

export const profileApiService = {
  async getByRoleAndEmail(role: UserRole, email: string) {
    switch (role) {
      case 'patologo': {
        const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/search`, {
          params: { q: email, limit: 1 }
        })
        return pickFirstFromUnknown(data) as BackendPatologo | undefined
      }
      case 'residente': {
        const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.RESIDENTS}/search`, {
          params: { ResidenteEmail: email, limit: 1 }
        })
        return pickFirstFromUnknown(data) as BackendResidente | undefined
      }
      case 'auxiliar': {
        const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.AUXILIARIES}/search`, {
          params: { AuxiliarEmail: email }
        })
        return pickFirstFromUnknown(data) as BackendAuxiliar | undefined
      }
      case 'admin':
      default:
        return undefined
    }
  },

  async updateByRole(role: UserRole, code: string, payload: any) {
    switch (role) {
      case 'patologo':
        return apiClient.put(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${code}`, payload)
      case 'residente':
        return apiClient.put(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${code}`, payload)
      case 'auxiliar':
        return apiClient.put(`${API_CONFIG.ENDPOINTS.AUXILIARIES}/${code}`, payload)
      default:
        return null
    }
  },

  async updateFirma(patologoCode: string, firmaUrl: string) {
    return apiClient.put(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${patologoCode}/firma`, {
      firma: firmaUrl
    })
  }
}



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
        // Backend de patólogos no expone filtro directo por email; usamos q=email y luego filtramos localmente
        const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/search`, {
          params: { q: email, limit: 5 }
        })
        let raw = pickFirstFromUnknown(data)
        // Intentar encontrar coincidencia exacta de email si la estructura retornada contiene lista
        if (Array.isArray((data as any)?.patologos)) {
          const exact = (data as any).patologos.find((p: any) => (p.patologo_email || p.PatologoEmail) === email)
          if (exact) raw = exact
        }
        if (!raw) return undefined
        // Normalizamos sólo si vienen campos en snake_case
        const mapped = {
          patologoName: raw.patologo_name || raw.patologoName,
          InicialesPatologo: raw.iniciales_patologo || raw.InicialesPatologo || raw.iniciales,
            patologoCode: raw.patologo_code || raw.patologoCode,
          PatologoEmail: raw.patologo_email || raw.PatologoEmail,
          registro_medico: raw.registro_medico,
          firma: raw.firma,
          observaciones: raw.observaciones,
          isActive: typeof raw.is_active === 'boolean' ? raw.is_active : raw.isActive,
          fecha_creacion: raw.fecha_creacion,
          fecha_actualizacion: raw.fecha_actualizacion
        } as BackendPatologo
        return mapped
      }
      case 'residente': {
        // BACKEND espera 'residente_email' (snake_case). Antes se enviaba 'ResidenteEmail' y no filtraba correctamente.
        const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.RESIDENTS}/search`, {
          params: { residente_email: email, limit: 1 }
        })
        const raw = pickFirstFromUnknown(data)
        if (!raw) return undefined
        const mapped = {
          residenteName: raw.residente_name || raw.residenteName,
          InicialesResidente: raw.iniciales_residente || raw.InicialesResidente || raw.iniciales,
          residenteCode: raw.residente_code || raw.residenteCode,
          ResidenteEmail: raw.residente_email || raw.ResidenteEmail,
          registro_medico: raw.registro_medico,
          observaciones: raw.observaciones,
          isActive: typeof raw.is_active === 'boolean' ? raw.is_active : raw.isActive,
          fecha_creacion: raw.fecha_creacion,
          fecha_actualizacion: raw.fecha_actualizacion
        } as BackendResidente
        return mapped
      }
      case 'auxiliar': {
        // Backend espera auxiliar_email (snake_case)
        const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.AUXILIARIES}/search`, {
          params: { auxiliar_email: email, limit: 5 }
        })
        const raw = pickFirstFromUnknown(data)
        if (!raw) return undefined
        const mapped = {
          auxiliarName: raw.auxiliar_name || raw.auxiliarName,
          auxiliarCode: raw.auxiliar_code || raw.auxiliarCode,
          AuxiliarEmail: raw.auxiliar_email || raw.AuxiliarEmail,
          observaciones: raw.observaciones,
          isActive: typeof raw.is_active === 'boolean' ? raw.is_active : raw.isActive,
          fecha_creacion: raw.fecha_creacion,
          fecha_actualizacion: raw.fecha_actualizacion
        } as BackendAuxiliar
        return mapped
      }
      case 'admin':
      default:
        return undefined
    }
  },

  async getPathologistByCode(code: string): Promise<BackendPatologo | undefined> {
    try {
      const data = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${code}`)
      return (data?.data ?? data) as BackendPatologo
    } catch {
      return undefined
    }
  },

  async updateByRole(role: UserRole, code: string, payload: any) {
    switch (role) {
      case 'patologo':
        // Mapear a snake_case si viene en camel/Pascal
        const patoPayload = {
          patologo_name: payload.patologoName || payload.patologo_name,
          iniciales_patologo: payload.InicialesPatologo || payload.iniciales_patologo || payload.iniciales,
          patologo_email: payload.PatologoEmail || payload.patologo_email,
          registro_medico: payload.registro_medico,
          observaciones: payload.observaciones
        }
        return apiClient.put(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${code}`, patoPayload)
      case 'residente':
        // Asegurar que exista code; si viene vacío no se debe intentar PUT raíz
        if (!code) throw new Error('No se pudo determinar el código del residente para actualizar')
        const resPayload = {
          residente_name: payload.residenteName || payload.residente_name,
          iniciales_residente: payload.InicialesResidente || payload.iniciales_residente || payload.iniciales,
          residente_email: payload.ResidenteEmail || payload.residente_email,
          registro_medico: payload.registro_medico,
          observaciones: payload.observaciones,
          // Permitir opcionalmente cambio de estado o password si se incluyen
          ...(payload.is_active !== undefined ? { is_active: payload.is_active } : {}),
          ...(payload.isActive !== undefined ? { is_active: payload.isActive } : {}),
          ...(payload.password ? { password: payload.password } : {})
        }
        return apiClient.put(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${code}`, resPayload)
      case 'auxiliar':
        const auxPayload = {
          auxiliar_name: payload.auxiliarName || payload.auxiliar_name,
          auxiliar_email: payload.AuxiliarEmail || payload.auxiliar_email,
          observaciones: payload.observaciones
        }
        return apiClient.put(`${API_CONFIG.ENDPOINTS.AUXILIARIES}/${code}`, auxPayload)
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



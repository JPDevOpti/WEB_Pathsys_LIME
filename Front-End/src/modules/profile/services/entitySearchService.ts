import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

class EntitySearchService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  async searchEntities(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const response = await apiClient.get(`${this.endpoint}/`, {
      params: { 
        query: query.trim(), 
        activo: includeInactive ? undefined : true, 
        limit: 50 
      }
    })
    if (response.entidades && Array.isArray(response.entidades)) {
      return response.entidades.map((entidad: any) => ({
        id: entidad.id || entidad._id,
        nombre: entidad.EntidadName,
        codigo: entidad.EntidadCode,
        tipo: 'entidad',
        activo: entidad.isActive,
        observaciones: entidad.observaciones,
        fecha_creacion: entidad.fecha_creacion,
        fecha_actualizacion: entidad.fecha_actualizacion,
        // Campos específicos para entidades (mapeo completo)
        EntidadName: entidad.EntidadName,
        EntidadCode: entidad.EntidadCode,
        isActive: entidad.isActive
      }))
    }
    return []
  }

  async searchResidents(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const response = await apiClient.get('/residentes/search', {
      params: { 
        residenteName: query.trim(),
        isActive: includeInactive ? undefined : true,
        limit: 50 
      }
    })
    // console.log('🔍 Respuesta búsqueda residentes:', response)
    if (response && response.residentes && Array.isArray(response.residentes)) {
      return response.residentes.map((residente: any) => ({
        id: residente.id || residente._id,
        nombre: residente.residenteName,
        codigo: residente.residenteCode,
        tipo: 'residente',
        activo: residente.isActive,
        email: residente.ResidenteEmail,
        documento: residente.residenteCode,
        fecha_creacion: residente.fecha_creacion,
        fecha_actualizacion: residente.fecha_actualizacion,
        // Campos específicos para residentes (mapeo completo)
        residenteName: residente.residenteName,
        residenteCode: residente.residenteCode,
        InicialesResidente: residente.InicialesResidente || '',
        ResidenteEmail: residente.ResidenteEmail,
        registro_medico: residente.registro_medico,
        observaciones: residente.observaciones || '',
        isActive: residente.isActive
      }))
    }
    return []
  }

  async searchPathologists(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const response = await apiClient.get('/patologos/search', {
      params: { 
        q: query.trim(), 
        isActive: includeInactive ? undefined : true,
        limit: 50 
      }
    })
    if (Array.isArray(response)) {
      return response.map((p: any) => ({
        id: p.id || p._id,
        nombre: p.patologoName,
        tipo: 'patologo',
        codigo: p.patologoCode,
        email: p.PatologoEmail,
        activo: p.isActive,
        // Campos específicos
        patologoName: p.patologoName,
        InicialesPatologo: p.InicialesPatologo || '',
        patologoCode: p.patologoCode,
        PatologoEmail: p.PatologoEmail,
        registro_medico: p.registro_medico,
        firma: p.firma || '',
        observaciones: p.observaciones || '',
        isActive: p.isActive,
        fecha_creacion: p.fecha_creacion,
        fecha_actualizacion: p.fecha_actualizacion
      }))
    }
    return []
  }

  async searchAuxiliaries(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const q = query.trim()
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const codeRegex = /^[A-Za-z0-9_-]{2,20}$/

    // Evitar enviar múltiples filtros a la vez (backend los combina con AND)
    const params: Record<string, any> = {}
    if (emailRegex.test(q)) {
      params.AuxiliarEmail = q
    } else if (codeRegex.test(q)) {
      params.auxiliarCode = q
    } else {
      params.auxiliarName = q
    }

    // Solo agregar filtro de estado activo si no se incluyen inactivos
    if (!includeInactive) {
      params.isActive = true
    }

    const response = await apiClient.get('/auxiliares/search', { params })
    if (response && response.auxiliares && Array.isArray(response.auxiliares)) {
      return response.auxiliares.map((aux: any) => ({
        id: aux.id || aux._id,
        nombre: aux.auxiliarName,
        codigo: aux.auxiliarCode,
        tipo: 'auxiliar',
        activo: aux.isActive,
        email: aux.AuxiliarEmail,
        fecha_creacion: aux.fecha_creacion,
        fecha_actualizacion: aux.fecha_actualizacion,
        // Campos específicos para auxiliar (mapeo completo)
        auxiliarName: aux.auxiliarName,
        auxiliarCode: aux.auxiliarCode,
        AuxiliarEmail: aux.AuxiliarEmail,
        observaciones: aux.observaciones || '',
        isActive: aux.isActive
      }))
    }
    return []
  }
}

export const entitySearchService = new EntitySearchService()
export default entitySearchService



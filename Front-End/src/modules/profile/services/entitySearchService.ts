import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

class EntitySearchService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  async searchEntities(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const response = await apiClient.get(`${this.endpoint}/`, {
      params: { 
        query: query.trim(), 
        activo: includeInactive ? undefined : true, // Usar 'activo' según el schema EntidadSearch
        limit: 50 
      }
    })
    if (response.entidades && Array.isArray(response.entidades)) {
      return response.entidades.map((entidad: any) => {
        // Mapeo correcto según documentación del backend
        const EntidadName = entidad.entidad_name || entidad.EntidadName || entidad.nombre || entidad.name || ''
        const EntidadCode = entidad.entidad_code || entidad.EntidadCode || entidad.codigo || entidad.code || ''
        const activo = entidad.is_active !== undefined ? entidad.is_active : (entidad.isActive !== undefined ? entidad.isActive : entidad.activo)
        return {
          id: entidad.id || entidad._id || EntidadCode,
          nombre: EntidadName,
          codigo: EntidadCode,
          tipo: 'entidad',
          activo,
          observaciones: entidad.observaciones || entidad.observations || '',
          fecha_creacion: entidad.fecha_creacion,
          fecha_actualizacion: entidad.fecha_actualizacion,
          // Campos específicos manteniendo nombres esperados por formularios
          EntidadName,
          EntidadCode,
          isActive: activo
        }
      })
    }
    return []
  }

  async searchResidents(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const response = await apiClient.get('/residentes/search', {
      params: { 
        residente_name: query.trim(), // Cambiar de 'q' a 'residente_name' según el backend
        is_active: includeInactive ? undefined : true, // Usar 'is_active' con underscore
        limit: 50 
      }
    })
    // console.log('🔍 Respuesta búsqueda residentes:', response)
    if (response && response.residentes && Array.isArray(response.residentes)) {
      return response.residentes.map((residente: any) => {
        // Mapeo correcto según documentación del backend
        const residenteName = residente.residente_name || residente.residenteName || residente.nombre || residente.name || ''
        const residenteCode = residente.residente_code || residente.residenteCode || residente.codigo || residente.code || residente.documento || ''
        const email = residente.residente_email || residente.ResidenteEmail || residente.email || ''
        const activo = residente.is_active !== undefined ? residente.is_active : (residente.isActive !== undefined ? residente.isActive : residente.activo)
        const iniciales = residente.iniciales_residente || residente.InicialesResidente || residente.initials || ''
        return {
          id: residente.id || residente._id || residenteCode,
          nombre: residenteName,
          codigo: residenteCode,
          tipo: 'residente',
          activo,
          email,
          documento: residenteCode,
          fecha_creacion: residente.fecha_creacion,
          fecha_actualizacion: residente.fecha_actualizacion,
          // Campos específicos manteniendo nombres esperados por formularios
          residenteName,
          residenteCode,
          InicialesResidente: iniciales,
          ResidenteEmail: email,
          registro_medico: residente.registro_medico || residente.medicalLicense || '',
          observaciones: residente.observaciones || residente.observations || '',
          isActive: activo
        }
      })
    }
    return []
  }

  async searchPathologists(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const response = await apiClient.get('/patologos/search', {
      params: { 
        q: query.trim(), 
        is_active: includeInactive ? undefined : true, // Corregir a 'is_active' con underscore
        limit: 50 
      }
    })
    if (Array.isArray(response)) {
      return response.map((p: any) => {
        // Mapeo correcto según documentación del backend
        const patologoName = p.patologo_name || p.patologoName || p.nombre || p.name || ''
        const patologoCode = p.patologo_code || p.patologoCode || p.codigo || p.code || ''
        const email = p.patologo_email || p.PatologoEmail || p.email || ''
        const activo = p.is_active !== undefined ? p.is_active : (p.isActive !== undefined ? p.isActive : p.activo)
        const iniciales = p.iniciales_patologo || p.InicialesPatologo || p.initials || ''
        return {
          id: p.id || p._id || patologoCode,
          nombre: patologoName,
          tipo: 'patologo',
          codigo: patologoCode,
          email,
          activo,
          // Campos específicos manteniendo nombres esperados por formularios
          patologoName,
          InicialesPatologo: iniciales,
          patologoCode,
          PatologoEmail: email,
          registro_medico: p.registro_medico || p.medicalLicense || '',
          firma: p.firma || p.signature || '',
          observaciones: p.observaciones || p.observations || '',
          isActive: activo,
          fecha_creacion: p.fecha_creacion,
          fecha_actualizacion: p.fecha_actualizacion
        }
      })
    }
    return []
  }

  async searchAuxiliaries(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    
    // Usar 'auxiliar_name' según el backend
    const params: Record<string, any> = {
      auxiliar_name: query.trim()
    }

    // Solo agregar filtro de estado activo si no se incluyen inactivos
    if (!includeInactive) {
      params.is_active = true // Corregir a 'is_active' con underscore
    }

    const response = await apiClient.get('/auxiliares/search', { params })
    if (response && response.auxiliares && Array.isArray(response.auxiliares)) {
      return response.auxiliares.map((aux: any) => {
        // Mapeo correcto según documentación del backend
        const auxiliarName = aux.auxiliar_name || aux.auxiliarName || aux.name || aux.nombre || ''
        const auxiliarCode = aux.auxiliar_code || aux.auxiliarCode || aux.code || aux.codigo || ''
        const email = aux.auxiliar_email || aux.AuxiliarEmail || aux.email || ''
        const activo = aux.is_active !== undefined ? aux.is_active : (aux.isActive !== undefined ? aux.isActive : aux.activo)
        return {
          id: aux.id || aux._id || auxiliarCode,
          nombre: auxiliarName,
          codigo: auxiliarCode,
          tipo: 'auxiliar',
          activo,
          email,
          fecha_creacion: aux.fecha_creacion,
          fecha_actualizacion: aux.fecha_actualizacion,
          // Campos específicos manteniendo nombres esperados por formularios
          auxiliarName,
          auxiliarCode,
          AuxiliarEmail: email,
          observaciones: aux.observaciones || aux.observations || '',
          isActive: activo
        }
      })
    }
    return []
  }
}

export const entitySearchService = new EntitySearchService()
export default entitySearchService



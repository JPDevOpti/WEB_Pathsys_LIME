import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

class EntitySearchService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  async searchEntities(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    
    let endpoint: string
    
    if (includeInactive) {
      endpoint = `${this.endpoint}/all-including-inactive`
    } else {
      endpoint = `${this.endpoint}/active`
    }
    
    // Construir parámetros de búsqueda
    const params: any = { 
      query: query.trim(),
      limit: 50 
    }
    
    console.log('🔍 Parámetros de búsqueda entidades:', params, 'Endpoint:', endpoint)
    
    const response = await apiClient.get(endpoint, { params })
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
    
    let endpoint: string
    
    if (includeInactive) {
      endpoint = '/residentes/all-including-inactive'
    } else {
      endpoint = '/residentes/active'
    }
    
    // Construir parámetros de búsqueda
    const params: any = { 
      query: query.trim(),
      limit: 50 
    }
    
    console.log('🔍 Parámetros de búsqueda residentes:', params, 'Endpoint:', endpoint)
    
    const response = await apiClient.get(endpoint, { params })
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
    
    let endpoint: string
    
    if (includeInactive) {
      endpoint = '/patologos/search/all-including-inactive'
    } else {
      endpoint = '/patologos/search/active'
    }
    
    // Construir parámetros de búsqueda
    const params: any = { 
      q: query.trim(),
      limit: 50 
    }
    
    console.log('🔍 Parámetros de búsqueda patólogos:', params, 'Endpoint:', endpoint)
    
    const response = await apiClient.get(endpoint, { params })
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
          isActive: activo
        }
      })
    }
    return []
  }

  async searchAuxiliaries(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    
    let endpoint: string
    
    if (includeInactive) {
      endpoint = '/auxiliares/all-including-inactive'
    } else {
      endpoint = '/auxiliares/active'
    }
    
    // Construir parámetros de búsqueda
    const params: any = { 
      query: query.trim(),
      limit: 50 
    }

    console.log('🔍 Parámetros de búsqueda auxiliares:', params, 'Endpoint:', endpoint)

    const response = await apiClient.get(endpoint, { params })
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

  async searchFacturacion(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    
    let endpoint: string
    
    if (includeInactive) {
      endpoint = '/facturacion/search/all-including-inactive'
    } else {
      endpoint = '/facturacion/search/active'
    }
    
    // Construir parámetros de búsqueda
    const params: any = { 
      query: query.trim(),
      limit: 50 
    }

    console.log('🔍 Parámetros de búsqueda facturación:', params, 'Endpoint:', endpoint)

    const response = await apiClient.get(endpoint, { params })
    console.log('🔍 Respuesta búsqueda facturación:', response)
    
    // El backend devuelve la respuesta directamente, no en response.data
    if (response && response.facturacion && Array.isArray(response.facturacion)) {
      return response.facturacion.map((fact: any) => {
        // Mapeo correcto según documentación del backend
        const facturacionName = fact.facturacion_name || fact.facturacionName || fact.name || fact.nombre || ''
        const facturacionCode = fact.facturacion_code || fact.facturacionCode || fact.code || fact.codigo || ''
        const email = fact.facturacion_email || fact.FacturacionEmail || fact.email || ''
        const activo = fact.is_active !== undefined ? fact.is_active : (fact.isActive !== undefined ? fact.isActive : fact.activo)
        return {
          id: fact.id || fact._id || facturacionCode,
          nombre: facturacionName,
          codigo: facturacionCode,
          tipo: 'facturacion',
          activo,
          email,
          fecha_creacion: fact.fecha_creacion,
          fecha_actualizacion: fact.fecha_actualizacion,
          // Campos específicos manteniendo nombres esperados por formularios
          facturacionName,
          facturacionCode,
          FacturacionEmail: email,
          observaciones: fact.observaciones || fact.observations || '',
          isActive: activo
        }
      })
    }
    return []
  }

  async searchTests(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    
    let endpoint: string
    
    if (includeInactive) {
      endpoint = '/pruebas/all-including-inactive'
    } else {
      endpoint = '/pruebas/active'
    }
    
    // Construir parámetros de búsqueda
    const params: any = { 
      query: query.trim(),
      limit: 50 
    }

    console.log('🔍 Parámetros de búsqueda pruebas:', params, 'Endpoint:', endpoint)

    const response = await apiClient.get(endpoint, { params })
    if (response && response.pruebas && Array.isArray(response.pruebas)) {
      return response.pruebas.map((prueba: any) => {
        const pruebasName = prueba.prueba_name || prueba.pruebasName || prueba.nombre || prueba.name || ''
        const pruebaCode = prueba.prueba_code || prueba.pruebaCode || prueba.codigo || prueba.code || ''
        const pruebasDescription = prueba.prueba_description || prueba.pruebasDescription || prueba.descripcion || prueba.description || ''
        const activo = prueba.is_active !== undefined ? prueba.is_active : (prueba.isActive !== undefined ? prueba.isActive : prueba.activo)
        return {
          id: prueba.id || prueba._id || pruebaCode,
          nombre: pruebasName,
          codigo: pruebaCode,
          tipo: 'prueba',
          activo,
          descripcion: pruebasDescription,
          tiempo: prueba.tiempo || 0,
          fecha_creacion: prueba.fecha_creacion,
          fecha_actualizacion: prueba.fecha_actualizacion,
          // Campos específicos manteniendo nombres esperados por formularios
          pruebasName,
          pruebaCode,
          pruebasDescription,
          isActive: activo
        }
      })
    }
    return []
  }
}

export const entitySearchService = new EntitySearchService()
export default entitySearchService



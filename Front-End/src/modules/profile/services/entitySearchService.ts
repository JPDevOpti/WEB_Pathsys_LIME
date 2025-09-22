import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

class EntitySearchService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  // Helper method to build search endpoints
  private buildEndpoint(endpoint: string, query: string, includeInactive: boolean): string {
    if (endpoint === this.endpoint) {
      // Entities use different endpoint structure
      const base = includeInactive ? `${endpoint}/inactive` : endpoint
      return `${base}?query=${encodeURIComponent(query.trim())}`
    } else {
      // Other entities use /search endpoint
      const base = `${endpoint}/search?q=${encodeURIComponent(query.trim())}`
      return includeInactive ? `${base}&include_inactive=true` : base
    }
  }

  // Data normalization for entities
  private normalizeEntity(entidad: any) {
    const entityName = entidad.name || entidad.entity_name || ''
    const entityCode = entidad.entity_code || entidad.code || ''
    const activo = entidad.is_active !== undefined ? entidad.is_active : true
    return {
      id: entidad.id || entidad._id || entityCode,
      nombre: entityName,
      codigo: entityCode,
      tipo: 'entidad',
      activo,
      observaciones: entidad.notes || entidad.observaciones || '',
      fecha_creacion: entidad.created_at,
      fecha_actualizacion: entidad.updated_at,
      entityName,
      entityCode,
      isActive: activo
    }
  }

  // Data normalization for residents
  private normalizeResident(residente: any) {
    const residenteName = residente.resident_name || residente.residente_name || residente.residenteName || residente.nombre || residente.name || ''
    const residenteCode = residente.resident_code || residente.residente_code || residente.residenteCode || residente.codigo || residente.code || residente.documento || ''
    const email = residente.resident_email || residente.residente_email || residente.ResidenteEmail || residente.email || ''
    const activo = residente.is_active !== undefined ? residente.is_active : (residente.isActive !== undefined ? residente.isActive : residente.activo)
    const iniciales = residente.initials || residente.iniciales_residente || residente.InicialesResidente || ''
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
      residenteName,
      residenteCode,
      InicialesResidente: iniciales,
      ResidenteEmail: email,
      registro_medico: residente.medical_license || residente.registro_medico || residente.medicalLicense || '',
      observaciones: residente.observations || residente.observaciones || '',
      isActive: activo
    }
  }

  // Data normalization for pathologists
  private normalizePathologist(p: any) {
    const patologoName = p.pathologist_name || p.patologo_name || p.patologoName || p.nombre || p.name || ''
    const patologoCode = p.pathologist_code || p.patologo_code || p.patologoCode || p.codigo || p.code || ''
    const email = p.pathologist_email || p.patologo_email || p.PatologoEmail || p.email || ''
    const activo = p.is_active !== undefined ? p.is_active : (p.isActive !== undefined ? p.isActive : p.activo)
    const iniciales = p.initials || p.iniciales_patologo || p.InicialesPatologo || ''
    return {
      id: p.id || p._id || patologoCode,
      nombre: patologoName,
      tipo: 'patologo',
      codigo: patologoCode,
      email,
      activo,
      patologoName,
      InicialesPatologo: iniciales,
      patologoCode,
      PatologoEmail: email,
      registro_medico: p.medical_license || p.registro_medico || p.medicalLicense || '',
      firma: p.signature || p.firma || '',
      observaciones: p.observations || p.observaciones || '',
      isActive: activo
    }
  }

  // Data normalization for auxiliaries
  private normalizeAuxiliary(aux: any) {
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
      auxiliarName,
      auxiliarCode,
      AuxiliarEmail: email,
      observaciones: aux.observations || aux.observaciones || '',
      isActive: activo
    }
  }

  // Data normalization for billing entities
  private normalizeBilling(fact: any) {
    const facturacionName = fact.billing_name || fact.facturacion_name || fact.facturacionName || fact.name || fact.nombre || ''
    const facturacionCode = fact.billing_code || fact.facturacion_code || fact.facturacionCode || fact.code || fact.codigo || ''
    const email = fact.billing_email || fact.facturacion_email || fact.FacturacionEmail || fact.email || ''
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
      facturacionName,
      facturacionCode,
      FacturacionEmail: email,
      observaciones: fact.observations || fact.observaciones || '',
      isActive: activo
    }
  }

  // Data normalization for tests
  private normalizeTest(prueba: any) {
    const pruebasName = prueba.name || prueba.prueba_name || prueba.pruebasName || prueba.nombre || ''
    const pruebaCode = prueba.test_code || prueba.prueba_code || prueba.pruebaCode || prueba.codigo || prueba.code || ''
    const pruebasDescription = prueba.description || prueba.prueba_description || prueba.pruebasDescription || prueba.descripcion || ''
    const activo = prueba.is_active !== undefined ? prueba.is_active : (prueba.isActive !== undefined ? prueba.isActive : prueba.activo)
    return {
      id: prueba.id || prueba._id || pruebaCode,
      nombre: pruebasName,
      codigo: pruebaCode,
      tipo: 'prueba',
      activo,
      descripcion: pruebasDescription,
      tiempo: prueba.time || prueba.tiempo || 0,
      fecha_creacion: prueba.fecha_creacion,
      fecha_actualizacion: prueba.fecha_actualizacion,
      pruebasName,
      pruebaCode,
      pruebasDescription,
      isActive: activo
    }
  }

  // Search methods
  async searchEntities(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const endpoint = this.buildEndpoint(this.endpoint, query, includeInactive)
    const response = await apiClient.get(endpoint)
    return Array.isArray(response) ? response.map(this.normalizeEntity) : []
  }

  async searchResidents(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const endpoint = this.buildEndpoint(API_CONFIG.ENDPOINTS.RESIDENTS, query, includeInactive)
    const response = await apiClient.get(endpoint)
    return Array.isArray(response) ? response.map(this.normalizeResident) : []
  }

  async searchPathologists(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const endpoint = this.buildEndpoint(API_CONFIG.ENDPOINTS.PATHOLOGISTS, query, includeInactive)
    const response = await apiClient.get(endpoint)
    return Array.isArray(response) ? response.map(this.normalizePathologist) : []
  }

  async searchAuxiliaries(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const endpoint = this.buildEndpoint(API_CONFIG.ENDPOINTS.AUXILIARIES, query, includeInactive)
    const response = await apiClient.get(endpoint)
    return Array.isArray(response) ? response.map(this.normalizeAuxiliary) : []
  }

  async searchFacturacion(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const endpoint = this.buildEndpoint(API_CONFIG.ENDPOINTS.FACTURACION, query, includeInactive)
    const response = await apiClient.get(endpoint)
    return Array.isArray(response) ? response.map(this.normalizeBilling) : []
  }

  async searchTests(query: string, includeInactive: boolean = false): Promise<any[]> {
    if (!query?.trim()) return []
    const endpoint = this.buildEndpoint(API_CONFIG.ENDPOINTS.TESTS, query, includeInactive)
    const response = await apiClient.get(endpoint)
    return Array.isArray(response) ? response.map(this.normalizeTest) : []
  }
}

export const entitySearchService = new EntitySearchService()
export default entitySearchService



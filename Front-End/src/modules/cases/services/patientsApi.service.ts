import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PatientData } from '../types'

/**
 * Interfaz para el request de crear paciente (según backend)
 */
interface CreatePatientRequest {
  nombre: string
  edad: number
  sexo: string
  entidad_info: {
    id: string
    nombre: string
  }
  tipo_atencion: string
  cedula: string
  observaciones?: string
}

/**
 * Interfaz para la respuesta del paciente creado (según backend)
 */
interface PatientResponse {
  id: string // El ID es igual a la cédula
  nombre: string
  edad: number
  sexo: string
  entidad_info: {
    id: string
    nombre: string
  }
  tipo_atencion: string
  cedula: string
  observaciones?: string
  fecha_creacion: string
  fecha_actualizacion: string
  id_casos: string[]
}

/**
 * Servicio específico para operaciones de pacientes
 * Maneja ÚNICAMENTE la colección de pacientes, NO casos
 */
export class PatientsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.PATIENTS

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Crea un paciente en la colección de pacientes
   * @param patientData - Datos del paciente a crear
   * @returns Paciente creado
   */
  async createPatient(patientData: PatientData): Promise<PatientResponse> {
    try {
  

      const patientRequest = this.buildPatientRequest(patientData)
      const response = await apiClient.post<PatientResponse>(this.endpoint, patientRequest)
      

      return response

    } catch (error: any) {

      throw new Error(error.message || 'Error al registrar el paciente')
    }
  }

  /**
   * Busca un paciente por cédula
   * @param cedula - Número de cédula del paciente
   * @returns Paciente encontrado o null
   */
  async getPatientByCedula(cedula: string): Promise<PatientResponse | null> {
    try {

      const response = await apiClient.get<PatientResponse>(`${this.endpoint}/cedula/${cedula}`)

      return response
    } catch (error: any) {
      if (error.response?.status === 404) {

        return null
      }

      throw new Error(error.message || `Error al buscar paciente con cédula ${cedula}`)
    }
  }

  /**
   * Actualiza los datos de un paciente existente
   * @param cedula - Cédula del paciente a actualizar
   * @param patientData - Datos actualizados del paciente
   * @returns Paciente actualizado
   */
  async updatePatient(cedula: string, patientData: PatientData): Promise<PatientResponse> {
    try {


      const patientRequest = this.buildPatientRequest(patientData)
      const response = await apiClient.put<PatientResponse>(`${this.endpoint}/${cedula}`, patientRequest)


      return response
    } catch (error: any) {

      throw new Error(error.message || `Error al actualizar el paciente con cédula ${cedula}`)
    }
  }

  /**
   * Verifica si un paciente ya existe en el sistema
   * @param cedula - Número de cédula a verificar
   * @returns true si el paciente existe
   */
  async checkPatientExists(cedula: string): Promise<boolean> {
    try {
      const patient = await this.getPatientByCedula(cedula)
      return patient !== null
    } catch (error) {
      // Si hay error (ej: 404), asumimos que no existe
      return false
    }
  }

  // ============================================================================
  // FUNCIONES DE VALIDACIÓN
  // ============================================================================

  /**
   * Valida datos del paciente antes del envío
   * @param patientData - Datos del paciente a validar
   * @returns Resultado de la validación
   */
  validatePatientData(patientData: PatientData): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar cédula
    if (!patientData.numeroCedula || patientData.numeroCedula.length < 6 || patientData.numeroCedula.length > 10) {
      errors.push('La cédula debe tener entre 6 y 10 dígitos')
    }

    // Validar nombre
    if (!patientData.nombrePaciente || patientData.nombrePaciente.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    }

    // Validar edad
    const edad = parseInt(patientData.edad)
    if (!edad || edad < 0 || edad > 150) {
      errors.push('La edad debe ser un número válido entre 0 y 150')
    }

    // Validar sexo
    if (!patientData.sexo) {
      errors.push('Debe seleccionar el sexo del paciente')
    }

    // Validar entidad
    if (!patientData.entidad) {
      errors.push('Debe seleccionar una entidad de salud')
    }

    // Validar tipo de atención
    if (!patientData.tipoAtencion) {
      errors.push('Debe seleccionar el tipo de atención')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  // ============================================================================
  // FUNCIONES DE TRANSFORMACIÓN
  // ============================================================================

  /**
   * Construye el request para crear paciente
   * @param patientData - Datos del paciente del formulario
   * @returns Request formateado para la API
   */
  private buildPatientRequest(patientData: PatientData): CreatePatientRequest {
    return {
      nombre: patientData.nombrePaciente,
      edad: parseInt(patientData.edad),
      sexo: this.mapGenderToApiFormat(patientData.sexo),
      entidad_info: {
        id: patientData.entidadCodigo || this.extractEntityId(patientData.entidad),
        nombre: patientData.entidad
      },
      tipo_atencion: this.mapAttentionTypeToApiFormat(patientData.tipoAtencion),
      cedula: patientData.numeroCedula,
      observaciones: patientData.observaciones || undefined
    }
  }

  /**
   * Mapea el género del formulario al formato de la API
   * @param gender - Género del formulario
   * @returns Género formateado para la API
   */
  private mapGenderToApiFormat(gender: string): string {
    const genderMap: Record<string, string> = {
      'masculino': 'Masculino',
      'femenino': 'Femenino',
      '': 'Otro'
    }
    return genderMap[gender] || 'Otro'
  }

  /**
   * Mapea el tipo de atención del formulario al formato de la API
   * @param attentionType - Tipo de atención del formulario
   * @returns Tipo de atención formateado para la API
   */
  private mapAttentionTypeToApiFormat(attentionType: string): string {
    const attentionMap: Record<string, string> = {
      'ambulatorio': 'Ambulatorio',
      'hospitalizado': 'Hospitalizado',
      '': 'Particular'
    }
    return attentionMap[attentionType] || 'Particular'
  }

  /**
   * Extrae el ID de entidad del nombre (simplificado)
   * TODO: En el futuro esto debería venir de un servicio de entidades
   * @param entityName - Nombre de la entidad
   * @returns ID de la entidad
   */
  private extractEntityId(entityName: string): string {
    // Por ahora usar IDs conocidos según la documentación
    const entityMap: Record<string, string> = {
      'EPS Sanitas': 'ent_001',
      'Sura': 'ent_002',
      'Nueva EPS': 'ent_003',
      'Compensar': 'ent_004',
      'Particular': 'ent_999'
    }
    
    return entityMap[entityName] || 'ent_001' // Default a EPS Sanitas
  }
}

// Exportar instancia singleton
export const patientsApiService = new PatientsApiService()
export default patientsApiService

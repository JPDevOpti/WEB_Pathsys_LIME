import apiClient from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface PathologistResponse {
  id: string
  pathologist_code: string
  pathologist_name: string
  initials?: string
  pathologist_email: string
  medical_license: string
  is_active: boolean
  signature: string
  observations?: string
  created_at: string
  updated_at: string
}

export interface SignatureResponse {
  pathologist_code: string
  signature: string
}

export interface SignatureUpdate {
  signature: string
}

export interface PathologistUpdate {
  pathologist_name?: string
  initials?: string
  pathologist_email?: string
  medical_license?: string
  is_active?: boolean
  observations?: string
}

export class PathologistApiService {
  private static readonly BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}/pathologists`

  /**
   * Obtener patólogo por código
   */
  static async getByCode(code: string): Promise<PathologistResponse | null> {
    try {
      const pathologist = await apiClient.get<PathologistResponse>(`${this.BASE_URL}/${code}`)
      return pathologist
    } catch (error) {
      console.error('Error al obtener patólogo:', error)
      return null
    }
  }

  /**
   * Buscar patólogo por email
   */
  static async getByEmail(email: string): Promise<PathologistResponse | null> {
    try {
      console.log('🔍 PathologistApiService.getByEmail - Buscando patólogo para:', email)
      const pathologists = await apiClient.get<PathologistResponse[]>(`${this.BASE_URL}/search`, {
        params: { q: email, limit: 1 }
      })
      
      console.log('📋 PathologistApiService.getByEmail - Respuesta completa:', pathologists)
      
      // El endpoint devuelve un array directamente
      if (Array.isArray(pathologists) && pathologists.length > 0) {
        console.log('✅ PathologistApiService.getByEmail - Patólogo encontrado:', pathologists[0])
        return pathologists[0] as PathologistResponse
      }
      
      console.log('❌ PathologistApiService.getByEmail - No se encontraron patólogos')
      return null
    } catch (error) {
      console.error('❌ PathologistApiService.getByEmail - Error al buscar patólogo por email:', error)
      return null
    }
  }

  /**
   * Actualizar patólogo
   */
  static async update(code: string, data: PathologistUpdate): Promise<PathologistResponse | null> {
    try {
      const pathologist = await apiClient.put<PathologistResponse>(`${this.BASE_URL}/${code}`, data)
      return pathologist
    } catch (error) {
      console.error('Error al actualizar patólogo:', error)
      throw error
    }
  }

  /**
   * Obtener firma digital
   */
  static async getSignature(code: string): Promise<SignatureResponse | null> {
    try {
      const signature = await apiClient.get<SignatureResponse>(`${this.BASE_URL}/${code}/signature`)
      return signature
    } catch (error) {
      console.error('Error al obtener firma:', error)
      return null
    }
  }

  /**
   * Actualizar firma digital (URL)
   */
  static async updateSignature(code: string, signatureUrl: string): Promise<PathologistResponse | null> {
    try {
      const pathologist = await apiClient.put<PathologistResponse>(`${this.BASE_URL}/${code}/signature`, {
        signature: signatureUrl
      })
      return pathologist
    } catch (error) {
      console.error('Error al actualizar firma:', error)
      throw error
    }
  }

  /**
   * Subir archivo de firma
   */
  static async uploadSignature(code: string, file: File): Promise<PathologistResponse | null> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const pathologist = await apiClient.put<PathologistResponse>(
        `${this.BASE_URL}/${code}/upload-signature`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      return pathologist
    } catch (error) {
      console.error('Error al subir firma:', error)
      throw error
    }
  }
}

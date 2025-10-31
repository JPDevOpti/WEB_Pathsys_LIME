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
  password?: string
}

export class PathologistApiService {
  private static readonly BASE_URL = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}/pathologists`
  private static readonly logPrefix = '[PathologistApiService]'
  private static trimOrEmpty(value?: string) { return (value ?? '').toString().trim() }

  /**
   * Obtener patólogo por código
   */
  static async getByCode(code: string): Promise<PathologistResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return null
      const res: any = await apiClient.get<PathologistResponse>(`${this.BASE_URL}/${normalized}`)
      return res?.data ?? res ?? null
    } catch (error) {
      console.error(`${this.logPrefix} getByCode error:`, error)
      return null
    }
  }

  /**
   * Buscar patólogo por email
   */
  static async getByEmail(email: string): Promise<PathologistResponse | null> {
    try {
      const normalized = this.trimOrEmpty(email)
      if (!normalized) return null
      const res: any = await apiClient.get<PathologistResponse[]>(`${this.BASE_URL}/search`, {
        params: { q: normalized, limit: 1 }
      })
      const list = Array.isArray(res) ? res : res?.data
      return Array.isArray(list) && list.length > 0 ? list[0] : null
    } catch (error) {
      console.error(`${this.logPrefix} getByEmail error:`, error)
      return null
    }
  }

  /**
   * Actualizar patólogo
   */
  static async update(code: string, data: PathologistUpdate): Promise<PathologistResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return null
      const res: any = await apiClient.put<PathologistResponse>(`${this.BASE_URL}/${normalized}`, data)
      return res?.data ?? res ?? null
    } catch (error) {
      console.error(`${this.logPrefix} update error:`, error)
      throw error
    }
  }

  /**
   * Obtener firma digital
   */
  static async getSignature(code: string): Promise<SignatureResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return null
      const res: any = await apiClient.get<SignatureResponse>(`${this.BASE_URL}/${normalized}/signature`)
      return res?.data ?? res ?? null
    } catch (error) {
      console.error(`${this.logPrefix} getSignature error:`, error)
      return null
    }
  }

  /**
   * Actualizar firma digital (URL)
   */
  static async updateSignature(code: string, signatureUrl: string): Promise<PathologistResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return null
      // Permitir cadena vacía para eliminar/limpiar la firma en backend
      const sig = (signatureUrl ?? '').toString()
      const res: any = await apiClient.put<PathologistResponse>(`${this.BASE_URL}/${normalized}/signature`, { signature: sig })
      return res?.data ?? res ?? null
    } catch (error) {
      console.error(`${this.logPrefix} updateSignature error:`, error)
      throw error
    }
  }

  /**
   * Eliminar firma digital
   */
  static async deleteSignature(code: string): Promise<boolean> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized) return false
      await apiClient.delete(`${this.BASE_URL}/${normalized}/signature`)
      return true
    } catch (error) {
      console.error(`${this.logPrefix} deleteSignature error:`, error)
      throw error
    }
  }

  /**
   * Subir archivo de firma
   */
  static async uploadSignature(code: string, file: File): Promise<PathologistResponse | null> {
    try {
      const normalized = this.trimOrEmpty(code)
      if (!normalized || !file) return null
      const formData = new FormData()
      formData.append('file', file)

      const res: any = await apiClient.put<PathologistResponse>(
        `${this.BASE_URL}/${normalized}/upload-signature`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return res?.data ?? res ?? null
    } catch (error) {
      console.error(`${this.logPrefix} uploadSignature error:`, error)
      throw error
    }
  }
}

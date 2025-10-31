import { apiClient } from '@/core/config/axios.config'
import type { CaseResponse } from '@/modules/cases/types/case'

export interface CaseSignRequest {
  method?: string[]
  macro_result?: string
  micro_result?: string
  diagnosis?: string
  observations?: string
  cie10_diagnosis?: {
    code: string
    name: string
  }
  cieo_diagnosis?: {
    code: string
    name: string
  }
}

// El backend devuelve un CaseResponse completo, no solo estos campos
export type CaseSignResponse = CaseResponse

export interface CaseSignValidation {
  case_code: string
  can_sign: boolean
  message: string
  current_state?: string
}

class SignApiService {
  private endpoint = '/cases'

  async signCase(caseCode: string, payload: CaseSignRequest): Promise<CaseSignResponse> {
    try {
      const response = await apiClient.put(`${this.endpoint}/${caseCode}/sign`, payload)
      return response
    } catch (error: any) {
      const errs = error?.response?.data?.errors
      const msg = Array.isArray(errs) && errs.length ? errs.map((e: any) => e?.msg || '').filter(Boolean).join('; ') : null
      throw new Error(msg || error.response?.data?.detail || error.message || `Error al firmar el caso ${caseCode}`)
    }
  }

  async validateCaseForSigning(caseCode: string): Promise<CaseSignValidation> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${caseCode}/sign/validation`)
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || `Error al validar el caso ${caseCode}`)
    }
  }
}

export default new SignApiService()

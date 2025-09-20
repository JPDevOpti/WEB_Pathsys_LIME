import { apiClient } from '@/core/config/axios.config'

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

export interface CaseSignResponse {
  case_code: string
  state: string
  signed_at: string
  message: string
}

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
      throw new Error(error.response?.data?.detail || error.message || `Error al firmar el caso ${caseCode}`)
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

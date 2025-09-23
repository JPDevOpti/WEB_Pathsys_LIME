import { apiClient } from '@/core/config/axios.config'

export interface ComplementaryTestInfo {
  code: string
  name: string
  quantity: number
}

export interface ApprovalInfo {
  reason: string
  request_date: string
  managed_date?: string
  approved_date?: string
  rejected_date?: string
  comments?: string
  assigned_pathologist?: AssignedPathologistInfo
}

export interface AssignedPathologistInfo {
  id: string
  name: string
}

export type ApprovalState = 'request_made' | 'pending_approval' | 'approved' | 'rejected'

export interface ApprovalRequestCreate {
  original_case_code: string
  complementary_tests: ComplementaryTestInfo[]
  reason: string
}

export interface ApprovalRequestUpdate {
  approval_state?: ApprovalState
  complementary_tests?: ComplementaryTestInfo[]
  approval_info?: Partial<ApprovalInfo>
}

export interface ApprovalRequestResponse {
  id: string
  approval_code: string
  original_case_code: string
  approval_state: ApprovalState
  complementary_tests: ComplementaryTestInfo[]
  approval_info: ApprovalInfo
  created_at: string
  updated_at: string
}

export interface ApprovalRequestSearch {
  original_case_code?: string
  approval_state?: ApprovalState
  request_date_from?: string
  request_date_to?: string
}

export interface ApprovalStats {
  total_requests: number
  requests_made: number
  pending_approval: number
  approved: number
  rejected: number
}

export interface ApprovalApproveResult {
  success: boolean
  message: string
  data: {
    approval: ApprovalRequestResponse
    new_case?: any
  }
}

class ApprovalService {
  private readonly baseUrl = '/approvals'

  private sanitizeResponse<T>(response: any): T {
    return response.data || response
  }

  async createApprovalRequest(data: ApprovalRequestCreate): Promise<ApprovalRequestResponse> {
    try {
      const response = await apiClient.post(this.baseUrl, data)
      return this.sanitizeResponse<ApprovalRequestResponse>(response)
    } catch (error: any) {
      console.error('Error en createApprovalRequest:', error)
      throw error
    }
  }

  async getApprovalRequest(approvalCode: string): Promise<ApprovalRequestResponse> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${approvalCode}`)
      return this.sanitizeResponse<ApprovalRequestResponse>(response)
    } catch (error: any) {
      console.error('Error en getApprovalRequest:', error)
      throw error
    }
  }

  async searchApprovalRequests(
    searchParams: ApprovalRequestSearch,
    skip: number = 0,
    limit: number = 50
  ): Promise<{ data: ApprovalRequestResponse[]; total: number; skip: number; limit: number }> {
    try {
      const response = await apiClient.post(
        `${this.baseUrl}/search`,
        searchParams,
        { params: { skip, limit } }
      )
      // El backend devuelve {data: [...], total: 1, skip: 0, limit: 20}
      // Necesitamos devolver el objeto completo, no solo response.data
      return response
    } catch (error: any) {
      console.error('Error en searchApprovalRequests:', error)
      throw error
    }
  }

  async getApprovalsByState(state: ApprovalState, limit: number = 50): Promise<ApprovalRequestResponse[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/state/${state}`, { params: { limit } })
      return this.sanitizeResponse<ApprovalRequestResponse[]>(response)
    } catch (error: any) {
      console.error('Error en getApprovalsByState:', error)
      throw error
    }
  }

  async manageApprovalRequest(approvalCode: string): Promise<ApprovalRequestResponse> {
    try {
      const response = await apiClient.patch(`${this.baseUrl}/${approvalCode}/manage`)
      return this.sanitizeResponse<ApprovalRequestResponse>(response)
    } catch (error: any) {
      console.error('Error en manageApprovalRequest:', error)
      throw error
    }
  }

  async approveRequest(approvalCode: string): Promise<ApprovalApproveResult> {
    try {
      const response = await apiClient.patch(`${this.baseUrl}/${approvalCode}/approve`)
      return this.sanitizeResponse<ApprovalApproveResult>(response)
    } catch (error: any) {
      console.error('Error en approveRequest:', error)
      throw error
    }
  }

  async rejectRequest(approvalCode: string): Promise<ApprovalRequestResponse> {
    try {
      const response = await apiClient.patch(`${this.baseUrl}/${approvalCode}/reject`)
      return this.sanitizeResponse<ApprovalRequestResponse>(response)
    } catch (error: any) {
      console.error('Error en rejectRequest:', error)
      throw error
    }
  }

  async updateApprovalRequest(
    approvalCode: string, 
    updateData: ApprovalRequestUpdate
  ): Promise<ApprovalRequestResponse> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/${approvalCode}`, updateData)
      return this.sanitizeResponse<ApprovalRequestResponse>(response)
    } catch (error: any) {
      console.error('Error en updateApprovalRequest:', error)
      throw error
    }
  }

  async updateComplementaryTests(
    approvalCode: string, 
    complementaryTests: ComplementaryTestInfo[]
  ): Promise<ApprovalRequestResponse> {
    try {
      const response = await apiClient.patch(`${this.baseUrl}/${approvalCode}/tests`, {
        complementary_tests: complementaryTests
      })
      return this.sanitizeResponse<ApprovalRequestResponse>(response)
    } catch (error: any) {
      console.error('Error en updateComplementaryTests:', error)
      throw error
    }
  }

  async deleteApprovalRequest(approvalCode: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.delete(`${this.baseUrl}/${approvalCode}`)
      return this.sanitizeResponse<{ success: boolean; message: string }>(response)
    } catch (error: any) {
      console.error('Error en deleteApprovalRequest:', error)
      throw error
    }
  }

  async getApprovalStatistics(): Promise<ApprovalStats> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/stats`)
      return this.sanitizeResponse<ApprovalStats>(response)
    } catch (error: any) {
      console.error('Error en getApprovalStatistics:', error)
      throw error
    }
  }
}

export default new ApprovalService()

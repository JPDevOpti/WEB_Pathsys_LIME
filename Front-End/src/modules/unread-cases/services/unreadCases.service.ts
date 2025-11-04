import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  UnreadCase,
  UnreadCaseListResponse,
  UnreadCaseListParams,
  UnreadCaseCreatePayload,
  UnreadCaseUpdatePayload,
  BulkMarkDeliveredPayload
} from '../types'

const ENDPOINT = API_CONFIG.ENDPOINTS.UNREAD_CASES

const normalizeParams = (params: UnreadCaseListParams = {}) => {
  const query: Record<string, any> = {}
  if (params.page !== undefined) query.page = params.page
  if (params.limit !== undefined) query.limit = params.limit
  if (params.searchQuery) query.search_query = params.searchQuery
  if (params.selectedInstitution) query.selected_institution = params.selectedInstitution
  if (params.selectedTestType) query.selected_test_type = params.selectedTestType
  if (params.selectedStatus) query.selected_status = params.selectedStatus
  if (params.dateFrom) query.date_from = params.dateFrom
  if (params.dateTo) query.date_to = params.dateTo
  if (params.sortKey) query.sort_key = params.sortKey
  if (params.sortOrder) query.sort_order = params.sortOrder
  return query
}

export const unreadCasesService = {
  async list(params: UnreadCaseListParams = {}): Promise<UnreadCaseListResponse> {
    return apiClient.get<UnreadCaseListResponse>(ENDPOINT, { params: normalizeParams(params) })
  },

  async get(caseCode: string): Promise<UnreadCase> {
    return apiClient.get<UnreadCase>(`${ENDPOINT}/${encodeURIComponent(caseCode)}`)
  },

  async create(payload: UnreadCaseCreatePayload): Promise<UnreadCase> {
    return apiClient.post<UnreadCase>(ENDPOINT, payload)
  },

  async update(caseCode: string, payload: UnreadCaseUpdatePayload): Promise<UnreadCase> {
    return apiClient.patch<UnreadCase>(`${ENDPOINT}/${encodeURIComponent(caseCode)}`, payload)
  },

  async markDelivered(payload: BulkMarkDeliveredPayload): Promise<UnreadCase[]> {
    const response = await apiClient.post<{ updated: UnreadCase[] }>(`${ENDPOINT}/batch/mark-delivered`, payload)
    return response.updated
  }
}


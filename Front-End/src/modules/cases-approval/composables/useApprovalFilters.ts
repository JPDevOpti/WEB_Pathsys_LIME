import { ref } from 'vue'
import type { ApprovalState } from '@/shared/services/approval.service'

export function useApprovalFilters() {
  const searchTerm = ref('')
  const selectedStatus = ref<ApprovalState | ''>('')

  const resetFilters = () => {
    searchTerm.value = ''
    selectedStatus.value = ''
  }

  return {
    searchTerm,
    selectedStatus,
    resetFilters
  }
}

import { ref } from 'vue'

type OperationType = 'approving' | 'rejecting' | 'managing'

export function useApprovalOperations() {
  const operations = ref<Map<string, OperationType>>(new Map())

  const startOperation = (id: string, type: OperationType) => {
    operations.value.set(id, type)
  }

  const endOperation = (id: string) => {
    operations.value.delete(id)
  }

  const isOperating = (id: string): boolean => {
    return operations.value.has(id)
  }

  const getOperationType = (id: string): OperationType | undefined => {
    return operations.value.get(id)
  }

  const isApproving = (id: string): boolean => {
    return operations.value.get(id) === 'approving'
  }

  const isRejecting = (id: string): boolean => {
    return operations.value.get(id) === 'rejecting'
  }

  const isManaging = (id: string): boolean => {
    return operations.value.get(id) === 'managing'
  }

  return {
    operations,
    startOperation,
    endOperation,
    isOperating,
    getOperationType,
    isApproving,
    isRejecting,
    isManaging
  }
}

import { ref, computed } from 'vue'

export function useApprovalPagination() {
  const currentPage = ref(1)
  const itemsPerPage = ref(20)
  const total = ref(0)

  const totalPages = computed(() => Math.ceil(total.value / itemsPerPage.value))
  const skip = computed(() => (currentPage.value - 1) * itemsPerPage.value)

  const setPage = (page: number) => {
    currentPage.value = page
  }

  const setItemsPerPage = (items: number) => {
    itemsPerPage.value = items
    currentPage.value = 1
  }

  const setTotal = (totalItems: number) => {
    total.value = totalItems
  }

  const resetPagination = () => {
    currentPage.value = 1
  }

  return {
    currentPage,
    itemsPerPage,
    total,
    totalPages,
    skip,
    setPage,
    setItemsPerPage,
    setTotal,
    resetPagination
  }
}

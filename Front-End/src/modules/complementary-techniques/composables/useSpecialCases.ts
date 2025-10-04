import { ref } from 'vue'

export function useSpecialCases() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  return {
    loading,
    error,
  }
}



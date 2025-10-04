import { ref } from 'vue'

export function useCTL() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  return { loading, error }
}



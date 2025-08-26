import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCasesStore = defineStore('cases', () => {
  // Estado para controlar la sincronización
  const lastUpdate = ref<Date>(new Date())
  const needsRefresh = ref(false)

  // Función para notificar que se ha creado un nuevo caso
  const notifyCaseCreated = () => {
    lastUpdate.value = new Date()
    needsRefresh.value = true
  }

  // Función para marcar que se ha refrescado
  const markRefreshed = () => {
    needsRefresh.value = false
  }

  // Función para verificar si necesita refrescar
  const shouldRefresh = () => {
    return needsRefresh.value
  }

  return {
    lastUpdate,
    needsRefresh,
    notifyCaseCreated,
    markRefreshed,
    shouldRefresh
  }
})

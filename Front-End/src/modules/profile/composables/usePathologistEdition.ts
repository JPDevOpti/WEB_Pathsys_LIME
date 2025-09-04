import { ref, computed } from 'vue'
import pathologistEditService from '../services/pathologistEditService'
import type { PathologistEditFormModel, PathologistUpdateResponse } from '../types/pathologist.types'

export const usePathologistEdition = () => {
  const isLoading = ref(false)
  const original = ref<PathologistEditFormModel | null>(null)

  // Habilitar envío como en residentes: o validación completa, o solo contraseña válida
  const canSubmit = computed(() => true)

  const validateForm = (form: PathologistEditFormModel) => {
    const errors: Record<string, string> = {}
    if (!form.patologoName?.trim()) errors.patologoName = 'El nombre es requerido'
    if (!form.InicialesPatologo?.trim() || form.InicialesPatologo.trim().length < 2) errors.InicialesPatologo = 'Iniciales válidas requeridas'
    if (!form.PatologoEmail?.trim()) errors.PatologoEmail = 'Email requerido'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.PatologoEmail)) errors.PatologoEmail = 'Email inválido'
    if (!form.registro_medico?.trim()) errors.registro_medico = 'Registro médico requerido'
    return { isValid: Object.keys(errors).length === 0, errors }
  }

  const update = async (form: PathologistEditFormModel) => {
    isLoading.value = true
    try {
      const data = pathologistEditService.prepareUpdateData(form)
      const res = await pathologistEditService.update(form.patologoCode, data)
      if (res.success && res.data) {
        // Los datos ya vienen normalizados del servicio, convertir snake_case a camelCase para el frontend
        original.value = {
          id: res.data.id,
          patologoName: res.data.patologo_name,
          InicialesPatologo: res.data.iniciales_patologo || '',
          patologoCode: res.data.patologo_code,
          PatologoEmail: res.data.patologo_email,
          registro_medico: res.data.registro_medico,
          observaciones: res.data.observaciones || '',
          isActive: res.data.is_active
        }
      }
      return res
    } finally {
      isLoading.value = false
    }
  }

  const setInitialData = (data: PathologistEditFormModel) => { original.value = { ...data } }
  const resetToOriginal = () => (original.value ? { ...original.value } : null)
  const createHasChanges = (current: PathologistEditFormModel) => {
    if (!original.value) return false
    const passwordChanged = !!current.password && current.password.trim().length >= 6
    return (
      original.value.patologoName !== current.patologoName ||
      original.value.InicialesPatologo !== current.InicialesPatologo ||
      original.value.PatologoEmail !== current.PatologoEmail ||
      original.value.registro_medico !== current.registro_medico ||
      original.value.observaciones !== current.observaciones ||
      original.value.isActive !== current.isActive ||
      passwordChanged
    )
  }

  return {
    isLoading,
    canSubmit,
    validateForm,
    update,
    setInitialData,
    resetToOriginal,
    createHasChanges
  }
}



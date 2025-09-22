import { ref, computed } from 'vue'
import pathologistEditService from '../services/pathologistEditService'
import type { PathologistEditFormModel } from '../types/pathologist.types'

export const usePathologistEdition = () => {
  const isLoading = ref(false)
  const original = ref<PathologistEditFormModel | null>(null)
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const isEmailValid = (email: string) => EMAIL_REGEX.test(email)
  const trimOrEmpty = (v?: string) => (v ?? '').toString().trim()

  // Habilitar envío como en residentes: o validación completa, o solo contraseña válida
  const canSubmit = computed(() => true)

  const validateForm = (form: PathologistEditFormModel) => {
    const errors: Record<string, string> = {}
    const name = trimOrEmpty(form.patologoName)
    const initials = trimOrEmpty(form.InicialesPatologo)
    const email = trimOrEmpty(form.PatologoEmail)
    const license = trimOrEmpty(form.registro_medico)

    if (!name) errors.patologoName = 'El nombre es requerido'
    if (!initials || initials.length < 2) errors.InicialesPatologo = 'Iniciales válidas requeridas'
    if (!email) errors.PatologoEmail = 'Email requerido'
    else if (!isEmailValid(email)) errors.PatologoEmail = 'Email inválido'
    if (!license) errors.registro_medico = 'Registro médico requerido'
    return { isValid: Object.keys(errors).length === 0, errors }
  }

  const update = async (form: PathologistEditFormModel) => {
    isLoading.value = true
    try {
      const data = pathologistEditService.prepareUpdateData(form)
      const code = trimOrEmpty(form.patologoCode)
      const res = await pathologistEditService.update(code, data)
      if (res.success && res.data) {
        original.value = {
          id: res.data.id,
          patologoName: res.data.pathologist_name,
          InicialesPatologo: res.data.initials || '',
          patologoCode: res.data.pathologist_code,
          PatologoEmail: res.data.pathologist_email,
          registro_medico: res.data.medical_license,
          observaciones: res.data.observations || '',
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



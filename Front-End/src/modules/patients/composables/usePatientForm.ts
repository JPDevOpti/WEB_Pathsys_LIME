import { reactive, computed } from 'vue'
import type { PatientFormData } from '../types'

export interface PatientFormErrors {
  identification_type: string[]
  identification_number: string[]
  first_name: string[]
  second_name: string[]
  first_lastname: string[]
  second_lastname: string[]
  birth_date: string[]
  gender: string[]
  municipality_code: string[]
  municipality_name: string[]
  subregion: string[]
  address: string[]
  entity_id: string[]
  entity_name: string[]
  care_type: string[]
  observations: string[]
}

export function usePatientForm() {
  const form = reactive<PatientFormData>({
    identification_type: '',
    identification_number: '',
    first_name: '',
    second_name: '',
    first_lastname: '',
    second_lastname: '',
    birth_date: '',
    gender: '',
    municipality_code: '',
    municipality_name: '',
    subregion: '',
    address: '',
    entity_id: '',
    entity_name: '',
    care_type: '',
    observations: ''
  })

  const errors = reactive<PatientFormErrors>({
    identification_type: [],
    identification_number: [],
    first_name: [],
    second_name: [],
    first_lastname: [],
    second_lastname: [],
    birth_date: [],
    gender: [],
    municipality_code: [],
    municipality_name: [],
    subregion: [],
    address: [],
    entity_id: [],
    entity_name: [],
    care_type: [],
    observations: []
  })

  const validationState = reactive({
    hasAttemptedSubmit: false,
    showValidationError: false
  })

  const isFormValid = computed(() => {
    return (
      form.identification_type !== '' &&
      form.identification_number.trim() !== '' &&
      form.first_name.trim() !== '' &&
      form.first_lastname.trim() !== '' &&
      form.birth_date !== '' &&
      form.gender !== '' &&
      form.municipality_code.trim() !== '' &&
      form.municipality_name.trim() !== '' &&
      form.subregion.trim() !== '' &&
      form.address.trim() !== '' &&
      form.entity_id.trim() !== '' &&
      form.entity_name.trim() !== '' &&
      form.care_type !== '' &&
      errors.identification_type.length === 0 &&
      errors.identification_number.length === 0 &&
      errors.first_name.length === 0 &&
      errors.first_lastname.length === 0 &&
      errors.birth_date.length === 0 &&
      errors.gender.length === 0 &&
      errors.municipality_code.length === 0 &&
      errors.municipality_name.length === 0 &&
      errors.subregion.length === 0 &&
      errors.address.length === 0 &&
      errors.entity_id.length === 0 &&
      errors.entity_name.length === 0 &&
      errors.care_type.length === 0
    )
  })

  const clearForm = () => {
    Object.assign(form, {
      identification_type: '',
      identification_number: '',
      first_name: '',
      second_name: '',
      first_lastname: '',
      second_lastname: '',
      birth_date: '',
      gender: '',
      municipality_code: '',
      municipality_name: '',
      subregion: '',
      address: '',
      entity_id: '',
      entity_name: '',
      care_type: '',
      observations: ''
    })
    
    Object.assign(errors, {
      identification_type: [],
      identification_number: [],
      first_name: [],
      second_name: [],
      first_lastname: [],
      second_lastname: [],
      birth_date: [],
      gender: [],
      municipality_code: [],
      municipality_name: [],
      subregion: [],
      address: [],
      entity_id: [],
      entity_name: [],
      care_type: [],
      observations: []
    })
    
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
  }

  const clearErrors = () => {
    Object.keys(errors).forEach(key => {
      (errors as any)[key] = []
    })
  }

  const validateForm = (): boolean => {
    clearErrors()
    let isValid = true

    // Validate identification type
    if (!form.identification_type) {
      errors.identification_type.push('El tipo de identificación es obligatorio')
      isValid = false
    }

    // Validate identification number
    if (!form.identification_number.trim()) {
      errors.identification_number.push('El número de identificación es obligatorio')
      isValid = false
    } else if (!/^[0-9A-Za-z]{6,20}$/.test(form.identification_number.trim())) {
      errors.identification_number.push('El número de identificación debe tener entre 6 y 20 caracteres alfanuméricos')
      isValid = false
    }

    // Validate first name
    if (!form.first_name.trim()) {
      errors.first_name.push('El primer nombre es obligatorio')
      isValid = false
    } else if (form.first_name.trim().length < 2) {
      errors.first_name.push('El primer nombre debe tener al menos 2 caracteres')
      isValid = false
    }

    // Validate first lastname
    if (!form.first_lastname.trim()) {
      errors.first_lastname.push('El primer apellido es obligatorio')
      isValid = false
    } else if (form.first_lastname.trim().length < 2) {
      errors.first_lastname.push('El primer apellido debe tener al menos 2 caracteres')
      isValid = false
    }

    // Validate birth date
    if (!form.birth_date) {
      errors.birth_date.push('La fecha de nacimiento es obligatoria')
      isValid = false
    } else {
      const birthDate = new Date(form.birth_date)
      const today = new Date()
      const age = today.getFullYear() - birthDate.getFullYear()
      
      if (birthDate > today) {
        errors.birth_date.push('La fecha de nacimiento no puede ser futura')
        isValid = false
      } else if (age > 150) {
        errors.birth_date.push('La edad no puede ser mayor a 150 años')
        isValid = false
      }
    }

    // Validate gender
    if (!form.gender) {
      errors.gender.push('El género es obligatorio')
      isValid = false
    }

    // Validate municipality code
    if (!form.municipality_code.trim()) {
      errors.municipality_code.push('El código de municipio es obligatorio')
      isValid = false
    }

    // Validate municipality name
    if (!form.municipality_name.trim()) {
      errors.municipality_name.push('El nombre del municipio es obligatorio')
      isValid = false
    }

    // Validate subregion
    if (!form.subregion.trim()) {
      errors.subregion.push('La subregión es obligatoria')
      isValid = false
    }

    // Validate address
    if (!form.address.trim()) {
      errors.address.push('La dirección es obligatoria')
      isValid = false
    }

    // Validate entity ID
    if (!form.entity_id.trim()) {
      errors.entity_id.push('El ID de entidad es obligatorio')
      isValid = false
    }

    // Validate entity name
    if (!form.entity_name.trim()) {
      errors.entity_name.push('El nombre de entidad es obligatorio')
      isValid = false
    }

    // Validate care type
    if (!form.care_type) {
      errors.care_type.push('El tipo de atención es obligatorio')
      isValid = false
    }

    return isValid
  }

  // Input handlers
  const handleIdentificationInput = (value: string) => {
    // Allow alphanumeric characters
    let cleanValue = value.replace(/[^0-9A-Za-z]/g, '')
    if (cleanValue.length > 20) cleanValue = cleanValue.substring(0, 20)
    form.identification_number = cleanValue
  }

  const handleNameInput = (field: 'first_name' | 'second_name' | 'first_lastname' | 'second_lastname') => (value: string) => {
    // Allow only letters and spaces
    const cleanValue = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '')
    form[field] = cleanValue
  }

  const handleMunicipalityCodeInput = (value: string) => {
    // Allow only numbers
    let cleanValue = value.replace(/\D/g, '')
    if (cleanValue.length > 10) cleanValue = cleanValue.substring(0, 10)
    form.municipality_code = cleanValue
  }

  const handleEntityIdInput = (value: string) => {
    // Allow alphanumeric characters
    let cleanValue = value.replace(/[^0-9A-Za-z]/g, '')
    if (cleanValue.length > 20) cleanValue = cleanValue.substring(0, 20)
    form.entity_id = cleanValue
  }

  return {
    form,
    errors,
    validationState,
    isFormValid,
    clearForm,
    clearErrors,
    validateForm,
    handleIdentificationInput,
    handleNameInput,
    handleMunicipalityCodeInput,
    handleEntityIdInput
  }
}

<template>
  <div class="pathologist-combobox">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Combobox Container -->
    <div class="relative">
      <!-- Input field -->
      <div class="relative">
        <input ref="inputRef" :value="displayText" type="text" :placeholder="placeholder"
          :disabled="disabled || isPatologoUser" :class="[
            'w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white appearance-none',
            errorString ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : (hasValue ? 'border-green-500' : 'border-gray-300'),
            (disabled || isPatologoUser) ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'text-gray-900'
          ]" @focus="handleFocus" @blur="handleBlur" @input="handleInput" @keydown="handleKeyDown"
          autocomplete="off" />

        <!-- Loading spinner -->
        <div v-if="isLoadingPathologists" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <svg class="animate-spin h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
            </path>
          </svg>
        </div>

        <!-- Dropdown arrow -->
        <div v-else class="absolute inset-y-0 right-0 pr-3 flex items-center">
          <svg v-if="!isPatologoUser" class="h-4 w-4 text-gray-400 cursor-pointer transition-transform"
            :class="{ 'transform rotate-180': isOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24"
            @click="toggleDropdown">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          <svg v-else class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <!-- Dropdown options -->
      <div v-if="isOpen && !disabled"
        class="absolute z-[99999] w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
        <!-- Loading state -->
        <div v-if="isLoadingPathologists" class="px-3 py-2 text-sm text-gray-500 text-center">
          Cargando patólogos...
        </div>

        <!-- No results -->
        <div v-else-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
          {{ searchQuery.trim() ? 'No se encontraron patólogos' : 'No hay patólogos disponibles' }}
        </div>

        <!-- Options -->
        <div v-for="(option, index) in filteredOptions" :key="option.value" :class="[
          'px-3 py-2 text-sm cursor-pointer transition-colors',
          index === highlightedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900 hover:bg-gray-100',
          selectedPathologist === option.value ? 'bg-blue-100 text-blue-900 font-medium' : ''
        ]" @click="selectOption(option)" @mouseenter="highlightedIndex = index">
          <div class="flex items-center justify-between">
            <span>{{ option.label }}</span>
            <svg v-if="selectedPathologist === option.value" class="h-4 w-4 text-blue-600" fill="currentColor"
              viewBox="0 0 20 20">
              <path fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Help text -->
    <p v-if="helpText" class="mt-1 text-xs text-gray-500">
      {{ helpText }}
    </p>

    <!-- Mensaje informativo para patólogos -->
    <p v-if="isPatologoUser" class="mt-1 text-xs text-blue-600">
      Tu patólogo está pre-seleccionado automáticamente
    </p>

    <!-- Error message -->
    <p v-if="errorString" class="mt-1 text-sm text-red-600">
      {{ errorString }}
    </p>

    <!-- Load error -->
    <div v-if="loadError" class="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-amber-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <p class="text-sm text-amber-800">No se pudieron cargar los patólogos.</p>
          <button @click="reloadPathologists"
            class="mt-1 text-sm text-amber-700 hover:text-amber-800 underline font-medium">
            Intentar cargar nuevamente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick } from 'vue'
import { usePathologistAPI } from '@/modules/cases/composables/usePathologistAPI'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAuthStore } from '@/stores/auth.store'
import type { FormPathologistInfo, SelectOption } from '@/modules/cases/types'

// Props
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helpText?: string
  errors?: string[]
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Buscar y seleccionar patólogo...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  autoLoad: true
})

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'pathologist-selected', pathologist: FormPathologistInfo | null): void
  (e: 'load-error', error: string): void
  (e: 'load-success', pathologists: FormPathologistInfo[]): void
}>()

// Composables
const { pathologists, loadPathologists, isLoading: isLoadingPathologists } = usePathologistAPI()
const { isPatologo } = usePermissions()
const authStore = useAuthStore()

// Refs
const inputRef = ref<HTMLInputElement>()
const searchQuery = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const loadError = ref('')
const isFocused = ref(false)

// Estado interno del componente seleccionado
const selectedPathologist = ref(props.modelValue)

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

const hasValue = computed(() => {
  return !!(selectedPathologist.value && String(selectedPathologist.value).trim())
})

// Convertir patólogos a opciones del select
const pathologistOptions = computed((): (SelectOption & { pathologist: FormPathologistInfo })[] => {
  return pathologists.value.map(pathologist => ({
    value: pathologist.patologo_code || '', // Usar patologo_code como valor
    label: pathologist.iniciales
      ? `${pathologist.iniciales} - ${pathologist.nombre}`
      : pathologist.nombre,
    pathologist
  }))
})

// Filtrar opciones basado en la búsqueda
const filteredOptions = computed((): (SelectOption & { pathologist: FormPathologistInfo })[] => {
  if (!searchQuery.value.trim()) {
    return pathologistOptions.value
  }

  const query = searchQuery.value.toLowerCase().trim()
  return pathologistOptions.value.filter(option => {
    const label = option.label.toLowerCase()
    const pathologist = option.pathologist

    return (
      label.includes(query) ||
      pathologist.nombre.toLowerCase().includes(query) ||
      (pathologist.iniciales && pathologist.iniciales.toLowerCase().includes(query)) ||
      pathologist.documento.toLowerCase().includes(query)
    )
  })
})

// Obtener el patólogo seleccionado actual
const currentSelectedPathologist = computed((): FormPathologistInfo | null => {
  if (!selectedPathologist.value) return null

  const option = pathologistOptions.value.find(opt => opt.value === selectedPathologist.value)
  return option?.pathologist || null
})

// Texto que se muestra en el input
const displayText = computed(() => {
  if (isFocused.value) {
    return searchQuery.value
  }

  if (selectedPathologist.value && currentSelectedPathologist.value) {
    const pathologist = currentSelectedPathologist.value
    return pathologist.iniciales
      ? `${pathologist.iniciales} - ${pathologist.nombre}`
      : pathologist.nombre
  }

  return searchQuery.value
})

// Funciones del combobox
const handleFocus = () => {
  if (isPatologoUser.value) return // No permitir focus si es patólogo

  isFocused.value = true
  searchQuery.value = ''
  isOpen.value = true
  highlightedIndex.value = -1
}

const handleBlur = () => {
  // Delay para permitir click en opciones
  setTimeout(() => {
    isFocused.value = false
    isOpen.value = false

    // Restaurar texto si no hay selección válida
    if (!selectedPathologist.value) {
      searchQuery.value = ''
    }
  }, 150)
}

const toggleDropdown = () => {
  if (props.disabled || isPatologoUser.value) return

  if (isOpen.value) {
    inputRef.value?.blur()
  } else {
    inputRef.value?.focus()
  }
}

const handleInput = (event: Event) => {
  if (isPatologoUser.value) return // No permitir input si es patólogo

  const target = event.target as HTMLInputElement
  searchQuery.value = target.value

  // Si el usuario está escribiendo, abrir el dropdown
  if (searchQuery.value.trim()) {
    isOpen.value = true
    highlightedIndex.value = -1
  }
}

const selectOption = (option: SelectOption & { pathologist: FormPathologistInfo }) => {
  if (isPatologoUser.value) return // No permitir cambiar selección si es patólogo

  selectedPathologist.value = option.value
  searchQuery.value = ''
  isOpen.value = false
  highlightedIndex.value = -1

  // Emit events
  emit('update:modelValue', option.value)
  emit('pathologist-selected', option.pathologist)

  // Quitar focus del input
  inputRef.value?.blur()
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (props.disabled || isPatologoUser.value) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        isOpen.value = true
      }
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1)
      break

    case 'ArrowUp':
      event.preventDefault()
      if (isOpen.value) {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      }
      break

    case 'Enter':
      event.preventDefault()
      if (isOpen.value && highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
        selectOption(filteredOptions.value[highlightedIndex.value])
      }
      break

    case 'Escape':
      event.preventDefault()
      isOpen.value = false
      highlightedIndex.value = -1
      inputRef.value?.blur()
      break

    case 'Tab':
      isOpen.value = false
      break
  }
}

// Computed para determinar si el usuario es patólogo (no administrador)
const isPatologoUser = computed(() => {
  return isPatologo.value && authStore.userRole !== 'administrador'
})

// Función para buscar automáticamente el patólogo del usuario logueado
const buscarPatologoUsuario = () => {
  // Permitir que patólogos Y administradores puedan tener patólogo pre-seleccionado
  const puedeTenerPatologo = isPatologo.value || authStore.userRole === 'administrador'

  if (puedeTenerPatologo && authStore.user && !selectedPathologist.value) {
    // 1) Preferir seleccionar por código si el usuario lo tiene
    const codigoPatologoUsuario = (authStore.user as any).pathologist_code || (authStore.user as any).patologo_code
    if (codigoPatologoUsuario && pathologists.value.length > 0) {
      const porCodigo = pathologists.value.find(p => p.patologo_code === codigoPatologoUsuario)
      if (porCodigo && porCodigo.patologo_code) {
        selectedPathologist.value = porCodigo.patologo_code
        emit('update:modelValue', porCodigo.patologo_code)
        emit('pathologist-selected', porCodigo)
        return
      }
    }

    // 2) Si no hay código o no coincide, intentar por nombre con múltiples campos
    const nombreUsuario =
      (authStore.user as any).name ||
      (authStore.user as any).username ||
      (authStore.user as any).nombre ||
      (authStore.user as any).nombres ||
      (authStore.user as any).nombre_completo ||
      (authStore.user as any).full_name ||
      ''

    if (nombreUsuario && pathologists.value.length > 0) {
      const nombreUsuarioLower = String(nombreUsuario).toLowerCase()
      const patologoEncontrado = pathologists.value.find(p => {
        if (!p?.nombre) return false
        const nombrePatologo = p.nombre.toLowerCase()
        return (
          nombrePatologo.includes(nombreUsuarioLower) ||
          nombreUsuarioLower.includes(nombrePatologo) ||
          (p.iniciales && p.iniciales.toLowerCase().includes(nombreUsuarioLower))
        )
      })

      if (patologoEncontrado && patologoEncontrado.patologo_code) {
        selectedPathologist.value = patologoEncontrado.patologo_code
        emit('update:modelValue', patologoEncontrado.patologo_code)
        emit('pathologist-selected', patologoEncontrado)
      }
    }
  }
}

// Función para recargar patólogos
const reloadPathologists = async () => {
  try {
    loadError.value = ''
    const result = await loadPathologists()

    if (result.success) {
      emit('load-success', pathologists.value)

      // Después de cargar patólogos, buscar automáticamente el del usuario
      nextTick(() => {
        buscarPatologoUsuario()
      })
    } else {
      loadError.value = result.message || 'Error al cargar patólogos'
      emit('load-error', loadError.value)
    }
  } catch (error: any) {
    const errorMessage = 'Error al cargar la lista de patólogos'
    loadError.value = errorMessage
    emit('load-error', errorMessage)
    console.error('Error al recargar patólogos:', error)
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  selectedPathologist.value = newValue || ''
}, { immediate: true })

watch(selectedPathologist, (newValue) => {
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue)
  }
})

// Watcher para buscar automáticamente el patólogo del usuario cuando se cargan los patólogos
watch(pathologists, (newPathologists) => {
  const puedeTenerPatologo = isPatologo.value || authStore.userRole === 'administrador'
  if (newPathologists.length > 0 && puedeTenerPatologo && !selectedPathologist.value) {
    nextTick(() => {
      buscarPatologoUsuario()
    })
  }
}, { immediate: true })

// Watcher para cuando cambie el usuario o el rol
watch([() => authStore.user, () => isPatologo.value, () => authStore.userRole], () => {
  const puedeTenerPatologo = isPatologo.value || authStore.userRole === 'administrador'
  if (pathologists.value.length > 0 && puedeTenerPatologo && !selectedPathologist.value) {
    nextTick(() => {
      buscarPatologoUsuario()
    })
  }
}, { immediate: true })

// Watcher para la búsqueda - esto permite la búsqueda automática
watch(searchQuery, () => {
  if (isFocused.value && searchQuery.value.trim()) {
    isOpen.value = true
    highlightedIndex.value = -1
  }
})

// Lifecycle
onMounted(async () => {
  if (props.autoLoad && pathologists.value.length === 0) {
    await reloadPathologists()
  }
})

// Sync display text
watch([displayText, isFocused], () => {
  if (!isFocused.value) {
    nextTick(() => {
      searchQuery.value = displayText.value
    })
  }
})


</script>

<style scoped>
.pathologist-combobox {
  position: relative;
}
</style>

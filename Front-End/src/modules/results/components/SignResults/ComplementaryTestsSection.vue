<template>
  <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
    <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
      <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      ¿Se necesitan más pruebas para completar el diagnóstico?
    </h3>

    <!-- Checkbox para activar pruebas complementarias -->
    <div class="mb-4">
      <FormCheckbox
        id="needs-complementary-tests"
        :model-value="needsComplementaryTests"
        @update:model-value="handleNeedsTestsChange"
        label="Solicitar pruebas complementarias"
        class="text-sm font-medium text-gray-700"
      />
    </div>

    <!-- Sección expandible para detalles de pruebas complementarias -->
    <div v-if="needsComplementaryTests" class="space-y-6">
      <!-- Selector dinámico de pruebas complementarias -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <label class="block text-sm font-medium text-gray-700">Pruebas Complementarias <span class="text-red-500">*</span></label>
          <AddButton text="Agregar Prueba" size="sm" @click="addTest" />
        </div>
        <div class="space-y-2">
          <div v-for="(test, index) in tests" :key="index" class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch sm:items-center bg-white border border-gray-200 rounded-lg p-3">
            <div class="flex-1 min-w-0">
              <TestList 
                v-model="test.codigo" 
                :label="`Prueba ${index + 1}`" 
                placeholder="Buscar y seleccionar prueba..." 
                :required="true" 
                :auto-load="true" 
                @test-selected="(t: any) => handleTestSelected(index, t)" 
              />
            </div>
            <div class="w-full sm:w-28">
              <FormInputField 
                v-model.number="test.cantidad" 
                label="Cant." 
                type="number" 
                :min="1" 
                :max="20" 
              />
            </div>
            <div class="flex items-center justify-center sm:w-10 sm:mt-6">
              <RemoveButton v-if="tests.length > 1" size="sm" @click="removeTest(index)" />
            </div>
          </div>
        </div>
        <div v-if="testsError" class="text-xs text-red-600">{{ testsError }}</div>
      </div>

      <!-- Campo de texto para describir las pruebas necesarias -->
      <div>
        <label for="complementary-tests-details" class="block text-sm font-medium text-gray-700 mb-2">
          Motivo de la solicitud <span class="text-red-500">*</span>
        </label>
        <FormTextarea
          id="complementary-tests-details"
          :model-value="complementaryTestsDetails"
          @update:model-value="handleDetailsChange"
          placeholder="Describa el motivo por el cual se requieren estas pruebas complementarias para completar el diagnóstico..."
          :rows="4"
          class="w-full"
        />
        <p v-if="descriptionError" class="mt-1 text-xs text-red-600">{{ descriptionError }}</p>
        <p class="mt-1 text-xs text-gray-500">Este motivo se incluirá en la solicitud de aprobación de pruebas complementarias.</p>
      </div>

      <!-- Botón para crear solicitud de aprobación -->
      <div class="flex justify-end flex-col items-end">
        <SaveButton
          :disabled="!isReadyToSign"
          :loading="signingWithChanges"
          text="Crear Solicitud de Aprobación"
          loading-text="Creando solicitud..."
          @click="handleSignWithChanges"
          size="md"
          variant="secondary"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FormCheckbox, FormTextarea, FormInputField } from '@/shared/components/forms'
import { SaveButton, AddButton, RemoveButton } from '@/shared/components/buttons'
import { TestList } from '@/shared/components/List'
import type { PruebaComplementaria } from '@/modules/results/services/casoAprobacion.service'

// Props
interface Props {
  initialNeedsTests?: boolean
  initialDetails?: string
  casoOriginal: string
}

const props = withDefaults(defineProps<Props>(), {
  initialNeedsTests: false,
  initialDetails: ''
})

// Emits
const emit = defineEmits<{
  (e: 'needs-tests-change', value: boolean): void
  (e: 'details-change', value: string): void
  (e: 'create-approval-request', data: { caso_original: string; motivo: string; pruebas_complementarias: PruebaComplementaria[] }): void
  (e: 'sign-with-changes', data: { details: string; tests: PruebaComplementaria[] }): void
}>()

// Estado local
const needsComplementaryTests = ref(props.initialNeedsTests)
const complementaryTestsDetails = ref(props.initialDetails)
const signingWithChanges = ref(false)

// Tests dinámicos - Usando la interfaz PruebaComplementaria actualizada
const tests = ref<PruebaComplementaria[]>([{ codigo: '', nombre: '', cantidad: 1 }])

// Errores simples
const testsError = ref('')
const descriptionError = ref('')

const validate = (): boolean => {
  testsError.value = ''
  descriptionError.value = ''
  
  // Validar que al menos una prueba tenga código
  const validTests = tests.value.filter(t => t.codigo && t.codigo.trim() !== '')
  if (validTests.length === 0) {
    testsError.value = 'Seleccione al menos una prueba complementaria.'
    return false
  }
  
  // Validar que todas las pruebas válidas tengan nombre
  const testsWithoutName = validTests.filter(t => !t.nombre || t.nombre.trim() === '')
  if (testsWithoutName.length > 0) {
    testsError.value = 'Algunas pruebas no tienen nombre válido. Vuelva a seleccionarlas.'
    return false
  }
  
  // Validar cantidad de cada prueba
  const testsWithInvalidQuantity = validTests.filter(t => !t.cantidad || t.cantidad < 1 || t.cantidad > 20)
  if (testsWithInvalidQuantity.length > 0) {
    testsError.value = 'Las cantidades deben estar entre 1 y 20.'
    return false
  }
  
  // Validar que el motivo no esté vacío
  if (!complementaryTestsDetails.value.trim()) {
    descriptionError.value = 'El motivo de la solicitud es obligatorio.'
    return false
  }
  
  // Validar longitud del motivo
  if (complementaryTestsDetails.value.trim().length < 10) {
    descriptionError.value = 'El motivo debe tener al menos 10 caracteres.'
    return false
  }
  
  return true
}

const isReadyToSign = computed<boolean>(() => {
  // Verificar que hay al menos una prueba válida
  const hasValidTests = tests.value.some(t => 
    t.codigo && t.codigo.trim() !== '' && 
    t.nombre && t.nombre.trim() !== '' && 
    t.cantidad && t.cantidad >= 1 && t.cantidad <= 20
  )
  
  // Verificar que hay motivo válido (al menos 10 caracteres)
  const hasValidReason = complementaryTestsDetails.value.trim() !== '' && 
                          complementaryTestsDetails.value.trim().length >= 10
  
  return hasValidTests && hasValidReason
})

// Manipulación de pruebas
const addTest = () => {
  // Asegurar que la nueva prueba tenga estructura válida
  tests.value.push({ 
    codigo: '', 
    nombre: '', 
    cantidad: 1 
  })
  // Limpiar errores al agregar nueva prueba
  testsError.value = ''
}

const removeTest = (index: number) => {
  if (tests.value.length > 1) {
    tests.value.splice(index, 1)
    // Limpiar errores después de remover
    testsError.value = ''
  }
}

const handleTestSelected = (index: number, test: any) => {
  if (!test) return
  
  const item = tests.value[index]
  if (item && typeof item === 'object') {
    // Mapear desde TestDetails (estructura principal)
    item.codigo = test.pruebaCode || test.codigo || test.code || ''
    item.nombre = test.pruebasName || test.nombre || test.name || test.label || item.codigo
    
    // Validación adicional
    if (!item.codigo.trim()) {
      console.warn('TestList devolvió una prueba sin código válido:', test)
      return
    }
    if (!item.nombre.trim()) {
      item.nombre = item.codigo // fallback al código si no hay nombre
    }
    
    // Limpiar errores si la selección es válida
    if (item.codigo.trim()) {
      testsError.value = ''
    }
  }
}

// Handlers
const handleNeedsTestsChange = (value: boolean) => {
  needsComplementaryTests.value = value
  if (!value) {
    // Limpiar datos cuando se desactiva
    complementaryTestsDetails.value = ''
    tests.value = [{ codigo: '', nombre: '', cantidad: 1 }]
  }
  emit('needs-tests-change', value)
}

const handleDetailsChange = (value: string) => {
  complementaryTestsDetails.value = value
  // Limpiar error si el motivo empieza a tener contenido válido
  if (value.trim().length >= 10) {
    descriptionError.value = ''
  }
  emit('details-change', value)
}

const handleSignWithChanges = async () => {
  // Validar antes de proceder
  if (!validate()) {
    console.warn('Validación falló al crear solicitud de aprobación')
    return
  }
  
  signingWithChanges.value = true
  try {
    // Filtrar y validar pruebas - solo las que tienen código y nombre válidos
    const validTests = tests.value.filter(test => 
      test.codigo && test.codigo.trim() !== '' && 
      test.nombre && test.nombre.trim() !== ''
    )
    
    if (validTests.length === 0) {
      testsError.value = 'No hay pruebas válidas seleccionadas.'
      return
    }
    
    // Preparar datos para envío al backend
    const testsToSend: PruebaComplementaria[] = validTests.map(test => ({
      codigo: test.codigo.trim(),
      nombre: test.nombre.trim(),
      cantidad: Math.max(1, Math.min(20, test.cantidad || 1)) // Asegurar rango válido
    }))
    
    // Validación final antes de enviar
    if (!props.casoOriginal || !/^[0-9]{4}-[0-9]{5}$/.test(props.casoOriginal)) {
      testsError.value = 'Código de caso original inválido.'
      return
    }
    
    const motivoFinal = complementaryTestsDetails.value.trim()
    if (motivoFinal.length < 10) {
      descriptionError.value = 'El motivo debe tener al menos 10 caracteres.'
      return
    }
    
    // Emit los datos validados
    emit('create-approval-request', {
      caso_original: props.casoOriginal,
      motivo: motivoFinal,
      pruebas_complementarias: testsToSend
    })
    
    emit('sign-with-changes', { 
      details: motivoFinal, 
      tests: testsToSend 
    })
    
    console.log('Solicitud de aprobación enviada:', {
      caso_original: props.casoOriginal,
      motivo: motivoFinal,
      pruebas_count: testsToSend.length,
      pruebas_complementarias: testsToSend
    })
    
  } catch (error) {
    console.error('Error en handleSignWithChanges:', error)
    testsError.value = 'Error interno al procesar la solicitud.'
  } finally {
    signingWithChanges.value = false
  }
}
</script>
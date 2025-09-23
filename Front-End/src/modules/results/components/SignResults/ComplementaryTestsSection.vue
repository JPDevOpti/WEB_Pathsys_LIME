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
                v-model="test.code" 
                :label="`Prueba ${index + 1}`" 
                placeholder="Buscar y seleccionar prueba..." 
                :required="true" 
                :auto-load="true" 
                @test-selected="(t: any) => handleTestSelected(index, t)" 
              />
            </div>
            <div class="w-full sm:w-28">
              <FormInputField 
                v-model.number="test.quantity" 
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
        <FormTextareaUnlimited
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
import { ref } from 'vue'
import { FormCheckbox, FormTextareaUnlimited, FormInputField } from '@/shared/components/forms'
import { SaveButton, AddButton, RemoveButton } from '@/shared/components/buttons'
import { TestList } from '@/shared/components/List'
import type { ComplementaryTestInfo } from '@/shared/services/approval.service'

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
  (e: 'create-approval-request', data: { case_code: string; reason: string; complementary_tests: ComplementaryTestInfo[] }): void
  (e: 'sign-with-changes', data: { details: string; tests: ComplementaryTestInfo[] }): void
}>()

// Estado local
const needsComplementaryTests = ref(props.initialNeedsTests)
const complementaryTestsDetails = ref(props.initialDetails)
const signingWithChanges = ref(false)

// Tests dinámicos - Usando la nueva interfaz ComplementaryTestInfo
const tests = ref<ComplementaryTestInfo[]>([{ code: '', name: '', quantity: 1 }])

// Errores simples
const testsError = ref('')
const descriptionError = ref('')

const validate = (): boolean => {
  testsError.value = ''
  descriptionError.value = ''
  
  const validTests = tests.value.filter(t => t.code && t.code.trim() !== '')
  if (validTests.length === 0) {
    testsError.value = 'Seleccione al menos una prueba complementaria.'
    return false
  }
  
  const testsWithoutName = validTests.filter(t => !t.name || t.name.trim() === '')
  if (testsWithoutName.length > 0) {
    testsError.value = 'Algunas pruebas no tienen nombre válido. Vuelva a seleccionarlas.'
    return false
  }
  
  const testsWithInvalidQuantity = validTests.filter(t => !t.quantity || t.quantity < 1 || t.quantity > 20)
  if (testsWithInvalidQuantity.length > 0) {
    testsError.value = 'Las cantidades deben estar entre 1 y 20.'
    return false
  }
  
  if (!complementaryTestsDetails.value.trim()) {
    descriptionError.value = 'El motivo de la solicitud es obligatorio.'
    return false
  }
  
  return true
}


// Manipulación de pruebas
const addTest = () => {
  tests.value.push({ 
    code: '', 
    name: '', 
    quantity: 1 
  })
  testsError.value = ''
}

const removeTest = (index: number) => {
  if (tests.value.length > 1) {
    tests.value.splice(index, 1)
    testsError.value = ''
  }
}

const handleTestSelected = (index: number, test: any) => {
  if (!test) return
  
  const item = tests.value[index]
  if (item && typeof item === 'object') {
    item.code = test.pruebaCode || test.codigo || test.code || ''
    item.name = test.pruebasName || test.nombre || test.name || test.label || item.code
    
    if (!item.code.trim()) {
      console.warn('TestList devolvió una prueba sin código válido:', test)
      return
    }
    if (!item.name.trim()) {
      item.name = item.code
    }
    
    if (item.code.trim()) {
      testsError.value = ''
    }
  }
}

// Handlers
const handleNeedsTestsChange = (value: boolean) => {
  needsComplementaryTests.value = value
  if (!value) {
    complementaryTestsDetails.value = ''
    tests.value = [{ code: '', name: '', quantity: 1 }]
  }
  emit('needs-tests-change', value)
}

const handleDetailsChange = (value: string) => {
  complementaryTestsDetails.value = value
  if (value.trim().length > 0) {
    descriptionError.value = ''
  }
  emit('details-change', value)
}

const handleSignWithChanges = async () => {
  if (!validate()) {
    console.warn('Validación falló al crear solicitud de aprobación')
    return
  }
  
  signingWithChanges.value = true
  try {
    const validTests = tests.value.filter(test => 
      test.code && test.code.trim() !== '' && 
      test.name && test.name.trim() !== ''
    )
    
    if (validTests.length === 0) {
      testsError.value = 'No hay pruebas válidas seleccionadas.'
      return
    }
    
    const testsToSend: ComplementaryTestInfo[] = validTests.map(test => ({
      code: test.code.trim(),
      name: test.name.trim(),
      quantity: Math.max(1, Math.min(20, test.quantity || 1))
    }))
    
    if (!props.casoOriginal || !/^[0-9]{4}-[0-9]{5}$/.test(props.casoOriginal)) {
      testsError.value = 'Código de caso original inválido.'
      return
    }
    
    const motivoFinal = complementaryTestsDetails.value.trim()
    
    // Solo emitir create-approval-request para crear la solicitud
    // El componente padre manejará la lógica de firma por separado
    emit('create-approval-request', {
      case_code: props.casoOriginal,
      reason: motivoFinal,
      complementary_tests: testsToSend
    })
    
    console.log('Solicitud de aprobación enviada:', {
      case_code: props.casoOriginal,
      reason: motivoFinal,
      pruebas_count: testsToSend.length,
      complementary_tests: testsToSend
    })
    
  } catch (error) {
    console.error('Error en handleSignWithChanges:', error)
    testsError.value = 'Error interno al procesar la solicitud.'
  } finally {
    signingWithChanges.value = false
  }
}
</script>
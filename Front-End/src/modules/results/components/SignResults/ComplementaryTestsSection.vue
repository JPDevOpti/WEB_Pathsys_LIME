<template>
  <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
    <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
      <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      Pruebas Complementarias
    </h3>

    <!-- Checkbox para activar pruebas complementarias -->
    <div class="mb-4">
      <FormCheckbox
        id="needs-complementary-tests"
        :model-value="needsComplementaryTests"
        @update:model-value="handleNeedsTestsChange"
        label="Se necesitan pruebas complementarias"
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
                @test-selected="(t) => handleTestSelected(index, t)" 
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
          Descripción de las pruebas complementarias requeridas <span class="text-red-500">*</span>
        </label>
        <FormTextarea
          id="complementary-tests-details"
          :model-value="complementaryTestsDetails"
          @update:model-value="handleDetailsChange"
          placeholder="Describa las pruebas complementarias que se requieren para completar el diagnóstico..."
          :rows="4"
          class="w-full"
        />
        <p v-if="descriptionError" class="mt-1 text-xs text-red-600">{{ descriptionError }}</p>
      </div>

      <!-- Botón para firmar con cambios -->
      <div class="flex justify-end">
        <SaveButton
          :disabled="!isReadyToSign"
          :loading="signingWithChanges"
          text="Solicitar Pruebas Complementarias"
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

// Props
interface Props {
  initialNeedsTests?: boolean
  initialDetails?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialNeedsTests: false,
  initialDetails: ''
})

// Emits
const emit = defineEmits<{
  (e: 'needs-tests-change', value: boolean): void
  (e: 'details-change', value: string): void
  (e: 'sign-with-changes', data: { details: string; tests: ComplementaryTestItem[] }): void
}>()

// Estado local
const needsComplementaryTests = ref(props.initialNeedsTests)
const complementaryTestsDetails = ref(props.initialDetails)
const signingWithChanges = ref(false)

// Tests dinámicos
interface ComplementaryTestItem { code: string; name: string; quantity: number }
const tests = ref<ComplementaryTestItem[]>([{ code: '', name: '', quantity: 1 }])

// Errores simples
const testsError = ref('')
const descriptionError = ref('')

const validate = () => {
  testsError.value = ''
  descriptionError.value = ''
  if (!tests.value.some(t => t.code.trim() !== '')) {
    testsError.value = 'Seleccione al menos una prueba.'
  }
  if (!complementaryTestsDetails.value.trim()) {
    descriptionError.value = 'La descripción es obligatoria.'
  }
  return !testsError.value && !descriptionError.value
}

const isReadyToSign = computed(() => {
  return tests.value.some(t => t.code.trim() !== '') && complementaryTestsDetails.value.trim() !== ''
})

// Manipulación de pruebas
const addTest = () => {
  tests.value.push({ code: '', name: '', quantity: 1 })
  emit('details-change', complementaryTestsDetails.value)
}

const removeTest = (index: number) => {
  if (tests.value.length > 1) {
    tests.value.splice(index, 1)
  }
}

const handleTestSelected = (index: number, test: any) => {
  if (!test) return
  const item = tests.value[index]
  if (item) {
    item.code = test.pruebaCode || test.code || ''
    item.name = test.pruebasName || test.nombre || test.label || ''
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
  emit('details-change', value)
}

const handleSignWithChanges = async () => {
  if (!validate()) return
  
  signingWithChanges.value = true
  try {
    // Filtrar solo las pruebas que tienen código seleccionado
    const validTests = tests.value.filter(test => test.code.trim() !== '')
    
    const signData = {
      details: complementaryTestsDetails.value,
      tests: validTests
    }
    
    emit('sign-with-changes', signData)
  } finally {
    signingWithChanges.value = false
  }
}
</script>

<template>
  <transition name="fade-scale">
    <div
      v-if="isOpen"
      :class="['fixed right-0 bottom-0 z-[100000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="handleClose"
    >
      <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <button
          @click="handleClose"
          class="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white/90 hover:bg-white transition-all duration-200 text-gray-600 hover:text-gray-800 ring-1 ring-transparent hover:ring-gray-200 hover:scale-105"
          title="Cerrar"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <div class="flex-shrink-0 px-4 py-4 pr-12 border-b border-gray-200 bg-white rounded-t-2xl">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                <SpecialCaseIcon class="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Nuevo caso sin lectura</h3>
              <p class="text-gray-600 text-xs mt-1">Complete los datos del nuevo registro - Se generará código automáticamente (ej: TC2025-00001)</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto overflow-x-visible p-6 space-y-6">
          <!-- Información del Paciente y Caso -->
          <div class="bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <UserCircleIcon class="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Información del Caso</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Complete los datos del paciente o marque como caso especial</p>
                </div>
              </div>
            </div>
            <div class="p-6 overflow-visible">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Tipo de Documento -->
                <FormSelect
                  v-if="!formData.isSpecialCase"
                  v-model="formData.documentType"
                  label="Tipo de Documento"
                  :options="[
                    { value: '', label: 'Seleccione...' },
                    { value: 'CC', label: 'Cédula de Ciudadanía' },
                    { value: 'TI', label: 'Tarjeta de Identidad' },
                    { value: 'CE', label: 'Cédula de Extranjería' },
                    { value: 'PA', label: 'Pasaporte' },
                    { value: 'RC', label: 'Registro Civil' }
                  ]"
                  :errors="errors.documentType ? [errors.documentType] : []"
                />

                <FormInput
                  v-if="!formData.isSpecialCase"
                  v-model="formData.patientDocument"
                  label="Documento"
                  placeholder="Ej: 70900325"
                  :errors="errors.patientDocument ? [errors.patientDocument] : []"
                  type="text"
                  maxlength="15"
                />

                <FormInput
                  v-if="!formData.isSpecialCase"
                  v-model="formData.firstName"
                  label="Primer Nombre"
                  placeholder="Ej: FRANCISCO"
                  :errors="errors.firstName ? [errors.firstName] : []"
                  maxlength="50"
                />

                <FormInput
                  v-if="!formData.isSpecialCase"
                  v-model="formData.secondName"
                  label="Segundo Nombre"
                  placeholder="Ej: JAVIER"
                  maxlength="50"
                />

                <FormInput
                  v-if="!formData.isSpecialCase"
                  v-model="formData.firstLastName"
                  label="Primer Apellido"
                  placeholder="Ej: ARBELAEZ"
                  :errors="errors.firstLastName ? [errors.firstLastName] : []"
                  maxlength="50"
                />

                <FormInput
                  v-if="!formData.isSpecialCase"
                  v-model="formData.secondLastName"
                  label="Segundo Apellido"
                  placeholder="Ej: GÓMEZ"
                  maxlength="50"
                />

                <div :class="formData.isSpecialCase ? 'md:col-span-2' : ''">
                  <EntityList
                    v-model="formData.entityCode"
                    label="Entidad"
                    placeholder="Buscar y seleccionar entidad..."
                    :errors="errors.entityCode ? [errors.entityCode] : []"
                    @entity-selected="handleEntitySelected"
                  />
                </div>

                <FormInputField
                  v-model.number="formData.numberOfPlates"
                  label="Número de Placas"
                  type="number"
                  min="0"
                  placeholder="0"
                />

                <FormTextarea
                  v-model="formData.notes"
                  label="Observaciones generales"
                  placeholder="Notas adicionales sobre el caso"
                  :rows="2"
                  :maxLength="500"
                  class="md:col-span-2"
                />
              </div>

              <div class="mt-4 flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg">
                <FormCheckbox
                  v-model="formData.isSpecialCase"
                  id="specialCase"
                  :label="'Caso especial (laboratorio externo, sin datos de paciente)'"
                >
                  <template #label-prefix>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </template>
                </FormCheckbox>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <TestIcon class="w-4 h-4 text-purple-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Pruebas a Realizar</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Seleccione el tipo de prueba y agregue las pruebas necesarias</p>
                </div>
              </div>
            </div>
            <div class="p-6 space-y-4 overflow-visible">
              <div class="flex items-center justify-between">
                <h5 class="text-sm font-semibold text-gray-800">Tipos de prueba</h5>
                <AddButton text="Agregar tipo de prueba" @click="addTestGroup" />
              </div>
              <p v-if="errors.tests" class="text-xs text-red-600">{{ errors.tests }}</p>

              <!-- Cada grupo de pruebas -->
              <div 
                v-for="(testGroup, groupIndex) in formData.testGroups" 
                :key="groupIndex"
                class="bg-white border border-gray-200 rounded-xl p-4 space-y-3 shadow-sm"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-1 overflow-visible">
                    <FormSelect
                      v-model="testGroup.type"
                      :label="`Tipo de prueba #${groupIndex + 1}`"
                      placeholder="Seleccione el tipo de prueba"
                      :options="[
                        { value: '', label: 'Seleccione...' },
                        { value: 'LOW_COMPLEXITY_IHQ', label: 'IHQ Baja Complejidad' },
                        { value: 'HIGH_COMPLEXITY_IHQ', label: 'IHQ Alta Complejidad' },
                        { value: 'SPECIAL_IHQ', label: 'IHQ Especiales' },
                        { value: 'HISTOCHEMISTRY', label: 'Histoquímicas' }
                      ]"
                      :error="errors[`testGroup_${groupIndex}_type`]"
                    />
                  </div>
                  <RemoveButton
                    v-if="formData.testGroups.length > 1"
                    @click="removeTestGroup(groupIndex)"
                    title="Eliminar tipo de prueba"
                    class="mt-6 flex-shrink-0"
                  />
                </div>

                <div v-if="testGroup.type" class="space-y-3 overflow-visible">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Pruebas</span>
                    <AddButton text="Agregar prueba" @click="addTestToGroup(groupIndex)" />
                  </div>

                  <div class="space-y-2">
                    <div 
                      v-for="(test, testIndex) in testGroup.tests" 
                      :key="testIndex"
                      class="grid grid-cols-1 md:grid-cols-[1fr_120px_40px] gap-3 items-end"
                    >
                      <div class="overflow-visible">
                        <TestList
                          v-model="test.code"
                          :label="`Prueba #${testIndex + 1}`"
                          :placeholder="`Buscar y seleccionar prueba ${testIndex + 1}...`"
                          :required="true"
                          :auto-load="true"
                          @test-selected="(t: any) => onTestSelected(groupIndex, testIndex, t)"
                        />
                      </div>
                      <div>
                        <FormInputField 
                          v-model.number="test.quantity" 
                          label="Cantidad" 
                          type="number" 
                          min="1" 
                          placeholder="1" 
                        />
                      </div>
                      <div class="flex items-center justify-center md:pb-2">
                        <RemoveButton 
                          @click="removeTestFromGroup(groupIndex, testIndex)" 
                          title="Eliminar prueba" 
                        />
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <!-- Recepción y Entrega -->
          <div class="bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <CalendarIcon class="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Información de Recepción</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Registre la fecha de ingreso y a quién se entregará</p>
                </div>
              </div>
            </div>
            <div class="p-6 space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Fecha de Ingreso -->
                <DateInputField
                  v-model="formData.entryDate"
                  label="Fecha de Ingreso"
                  :errors="errors.entryDate ? [errors.entryDate] : []"
                  required
                />

                <!-- Entregado A -->
                <FormInputField
                  v-model="formData.deliveredTo"
                  label="Entregado A"
                  placeholder="Ej: IMQ, AMPR"
                  :errors="errors.deliveredTo ? [errors.deliveredTo] : []"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div class="flex justify-end gap-3">
            <ClearButton 
              text="Limpiar" 
              size="sm"
              @click="handleReset"
            >
              <template #icon>
                <RefreshIcon class="w-4 h-4 mr-2" />
              </template>
            </ClearButton>
            <SaveButton 
              text="Guardar"
              size="sm"
              :loading="isSaving"
              :fit-content="true"
              @click="handleSave"
            />
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { SpecialCaseIcon, UserCircleIcon, CalendarIcon, TestIcon, RefreshIcon } from '@/assets/icons'
import { useSidebar } from '@/shared/composables/SidebarControl'
import { useAuthStore } from '@/stores/auth.store'
import FormInput from '@/shared/components/ui/forms/FormInput.vue'
import FormSelect from '@/shared/components/ui/forms/FormSelect.vue'
import FormTextarea from '@/shared/components/ui/forms/FormTextarea.vue'
import FormCheckbox from '@/shared/components/ui/forms/FormCheckbox.vue'
import FormInputField from '@/shared/components/ui/forms/FormInputField.vue'
import DateInputField from '@/shared/components/ui/forms/DateInputField.vue'
import EntityList from '@/shared/components/ui/lists/EntityList.vue'
import TestList from '@/shared/components/ui/lists/TestList.vue'
import { AddButton, RemoveButton } from '@/shared/components/ui/buttons'
import SaveButton from '@/shared/components/ui/buttons/SaveButton.vue'
import ClearButton from '@/shared/components/ui/buttons/ClearButton.vue'
import type { EntityInfo } from '@/modules/cases/types/case'

interface Props {
  isOpen: boolean
}

interface TestItem {
  code: string
  quantity: number
  name?: string
}

interface TestGroup {
  type: 'LOW_COMPLEXITY_IHQ' | 'HIGH_COMPLEXITY_IHQ' | 'SPECIAL_IHQ' | 'HISTOCHEMISTRY' | ''
  tests: TestItem[]
}

interface FormData {
  caseCode?: string
  isSpecialCase: boolean
  documentType: string
  patientDocument: string
  firstName: string
  secondName: string
  firstLastName: string
  secondLastName: string
  entityCode: string
  entityName: string
  notes: string
  testGroups: TestGroup[]
  entryDate: string
  receivedBy: string
  numberOfPlates: number
  deliveredTo: string
  deliveryDate: string
  status: string
}

defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: FormData): void
}>()

const isSaving = ref(false)
const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const authStore = useAuthStore()

// Computed class for overlay positioning based on sidebar state
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const normalizeTests = (tests: any[]): TestItem[] => {
  if (!Array.isArray(tests)) return []
  return tests.map((test: any) => ({
    code: test?.code || '',
    quantity: Number.isFinite(Number(test?.quantity)) ? Number(test.quantity) : 1,
    name: test?.name || ''
  }))
}

const normalizeTestGroups = (groups?: any[]): TestGroup[] => {
  if (!Array.isArray(groups) || !groups.length) {
    return [{ type: '', tests: [] }]
  }
  return groups.map((group: any) => ({
    type: group?.type || '',
    tests: normalizeTests(group?.tests)
  }))
}

const formData = ref<FormData>({
  caseCode: undefined,
  isSpecialCase: false,
  documentType: '',
  patientDocument: '',
  firstName: '',
  secondName: '',
  firstLastName: '',
  secondLastName: '',
  entityCode: '',
  entityName: '',
  notes: '',
  testGroups: normalizeTestGroups(),
  entryDate: new Date().toISOString().split('T')[0],
  receivedBy: '',
  numberOfPlates: 0,
  deliveredTo: '',
  deliveryDate: '',
  status: 'En proceso'
})

// Llenar automáticamente "Recibido Por" con el nombre del usuario autenticado
const initializeReceivedBy = () => {
  if (authStore.user) {
    const user = authStore.user
    formData.value.receivedBy = user.name || user.email || ''
  }
}

// Inicializar al montar
onMounted(() => {
  initializeReceivedBy()
})

const errors = ref<Record<string, string>>({})

const clearTestErrorsForGroup = (groupIndex: number) => {
  Object.keys(errors.value).forEach((key) => {
    if (key.startsWith(`testGroup_${groupIndex}_`)) {
      delete errors.value[key]
    }
  })
}

// Limpiar campos de paciente cuando se marca como caso especial
watch(() => formData.value.isSpecialCase, (isSpecial) => {
  if (isSpecial) {
    formData.value.documentType = ''
    formData.value.patientDocument = ''
    formData.value.firstName = ''
    formData.value.secondName = ''
    formData.value.firstLastName = ''
    formData.value.secondLastName = ''
    errors.value.documentType = ''
    errors.value.patientDocument = ''
    errors.value.firstName = ''
    errors.value.firstLastName = ''
  }
})

// Sincronizar pruebas iniciales según tipo seleccionado
watch(() => formData.value.testGroups.map(group => group.type), (types) => {
  types.forEach((type, idx) => {
    const target = formData.value.testGroups[idx]
    if (type && target.tests.length === 0) {
      target.tests.push({ code: '', quantity: 1, name: '' })
    }
    if (!type) {
      target.tests = []
      clearTestErrorsForGroup(idx)
    }
  })
}, { deep: true })

const validateForm = (): boolean => {
  errors.value = {}
  let isValid = true

  // Validar datos de paciente (solo si no es caso especial)
  // Información del caso es opcional; limpiar errores previos
  errors.value.documentType = ''
  errors.value.patientDocument = ''
  errors.value.firstName = ''
  errors.value.firstLastName = ''
  errors.value.entityCode = ''
  errors.value.entryDate = ''
  errors.value.receivedBy = ''

  // Validar que al menos haya una prueba válida
  const hasValidTests = formData.value.testGroups.some(group => 
    group.type && group.tests.length > 0 && group.tests.every(test => test.code && test.quantity > 0)
  )

  if (!hasValidTests) {
    errors.value.tests = 'Debe agregar al menos un tipo de prueba con pruebas válidas'
    isValid = false
  }

  // Validar cada grupo de pruebas
  formData.value.testGroups.forEach((group, groupIndex) => {
    if (group.tests.length > 0 && !group.type) {
      errors.value[`testGroup_${groupIndex}_type`] = 'Debe seleccionar el tipo de prueba'
      isValid = false
    }
    group.tests.forEach((test, testIndex) => {
      if (!test.code) {
        errors.value[`testGroup_${groupIndex}_test_${testIndex}_code`] = 'Seleccione una prueba'
        isValid = false
      }
      if (!test.quantity || test.quantity <= 0) {
        errors.value[`testGroup_${groupIndex}_test_${testIndex}_quantity`] = 'La cantidad debe ser mayor a 0'
        isValid = false
      }
    })
  })

  return isValid
}

const handleSave = async () => {
  if (!validateForm()) {
    return
  }

  isSaving.value = true

  emit('save', { ...formData.value })
  isSaving.value = false
  handleReset()
  emit('close')
}

const handleEntitySelected = (entity: EntityInfo | null) => {
  if (entity) {
    formData.value.entityName = entity.name
  } else {
    formData.value.entityName = ''
  }
}

// Métodos para gestión de pruebas
const addTestGroup = () => {
  formData.value.testGroups.push({ type: '', tests: [] })
}

const removeTestGroup = (groupIndex: number) => {
  formData.value.testGroups.splice(groupIndex, 1)
  if (!formData.value.testGroups.length) {
    formData.value.testGroups.push({ type: '', tests: [] })
  }
  Object.keys(errors.value).forEach((key) => {
    if (key.startsWith('testGroup_')) delete errors.value[key]
  })
}

const addTestToGroup = (groupIndex: number) => {
  formData.value.testGroups[groupIndex].tests.push({ code: '', quantity: 1, name: '' })
}

const removeTestFromGroup = (groupIndex: number, testIndex: number) => {
  formData.value.testGroups[groupIndex].tests.splice(testIndex, 1)
  clearTestErrorsForGroup(groupIndex)
}

const onTestSelected = (groupIndex: number, testIndex: number, test: any) => {
  if (test && test.name) {
    formData.value.testGroups[groupIndex].tests[testIndex].name = test.name
  }
}

const handleReset = () => {
  formData.value = {
    caseCode: undefined,
    isSpecialCase: false,
    documentType: '',
    patientDocument: '',
    firstName: '',
    secondName: '',
    firstLastName: '',
    secondLastName: '',
    entityCode: '',
    entityName: '',
    notes: '',
    testGroups: normalizeTestGroups(),
    entryDate: new Date().toISOString().split('T')[0],
    receivedBy: '',
    numberOfPlates: 0,
    deliveredTo: '',
    deliveryDate: '',
    status: 'En proceso'
  }
  errors.value = {}
  initializeReceivedBy()
}

const handleClose = () => {
  if (isSaving.value) return
  emit('close')
}
</script>

<style scoped>
/* Fade transition for overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Slide transition for drawer */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

/* Hacer los campos más compactos */
:deep(.space-y-1) {
  margin-top: 0 !important;
}

:deep(.space-y-1 label) {
  font-size: 0.75rem !important;
  margin-bottom: 0.25rem !important;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-weight: 500;
  color: #374151;
}

:deep(.space-y-1 input),
:deep(.space-y-1 select) {
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
  font-size: 0.875rem !important;
  height: auto !important;
}

:deep(.relative.group label) {
  font-size: 0.75rem !important;
  margin-bottom: 0.25rem !important;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-weight: 500;
  color: #374151;
}

:deep(.relative.group input) {
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
  font-size: 0.875rem !important;
  height: auto !important;
}

:deep(.entity-combobox label) {
  font-size: 0.75rem !important;
  margin-bottom: 0.25rem !important;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-weight: 500;
  color: #374151;
}

:deep(.entity-combobox input) {
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
  font-size: 0.875rem !important;
}

/* Estilos para DateInputField */
:deep(.date-input-field label) {
  font-size: 0.75rem !important;
  margin-bottom: 0.25rem !important;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-weight: 500;
  color: #374151;
}

:deep(.date-input-field input) {
  padding-top: 0.5rem !important;
  padding-bottom: 0.5rem !important;
  font-size: 0.875rem !important;
  height: auto !important;
}
</style>
